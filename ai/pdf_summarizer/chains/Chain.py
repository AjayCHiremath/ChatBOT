from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnableSequence, RunnablePassthrough
from langchain_core.messages import trim_messages
from langchain_core.messages.utils import count_tokens_approximately

from utils.logger.EventLogger import log_message
from ai.pdf_summarizer.memory.Memory import get_memory

from utils.global_variables import MAX_TOKENS_CHAT_HISTORY

# ---{ Helper function to trim chat history }---
def build_trim_step():
    return RunnableLambda(lambda inputs: {
        **inputs,
        "chat_history": trim_messages( inputs.get("chat_history", []),
                                          max_tokens=MAX_TOKENS_CHAT_HISTORY,
                                          strategy="last",
                                          token_counter=count_tokens_approximately,  # Fast approximate counting
                                          include_system=True,
                                          allow_partial=False,
                                          start_on="human"
                            )}
         )

# ---{ Helper function to build the Reframing Chain }---
def build_chain(prompt, model, log_base="logs/chatbot/", echo=False):
    try:       
        # ---{Build the LangChain LLMChain with prompt & model}---
        model_chain = (prompt | model)
        log_message("[Success] LLMChain built successfully.", log_file=log_base, echo=echo)
        return model_chain
    except Exception as e:
        log_message(f"[Error] build_chain: {e}", log_file=log_base, echo=echo)
        raise

# ---{ Helper function to clean metadata }---
def clean_metadata(meta):
    keys_to_keep = ["page", "total_pages", "source", "session_id"]
    return {k: v for k, v in meta.items() if k in keys_to_keep}

# ---{ Helper function to build Sequential Chat Chain }---
def build_chat_chain(reframing_chain, summarization_chain, retriever, output_parser, log_base="logs/chatbot/", echo=False):
    try:
        # ---{Get Trimmer function}---
        trimmer = build_trim_step()
        
        chain = RunnableSequence(
            #---------{Pass the original inputs as-is.}---------
            RunnablePassthrough() |

            #---------{Trim chat history to fit within token limits for context window.}---------
            trimmer |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Trimmed chat history: {inputs.get('chat_history', [])}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Prepare inputs explicitly for the reframing chain:}---------
            #---------{Extract 'question' and keep 'chat_history' from the previous step.}---------
            RunnableLambda(lambda inputs: {
                "question": inputs["question"],
                "chat_history": inputs.get("chat_history", [])
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Prepared inputs for reframing: {inputs}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Call the reframing chain explicitly.}---------
            #---------{The reframing_chain is expected to produce an AIMessage object (the reframed question).}---------
            #---------{We also carry forward 'chat_history' so we can preserve it in the next steps.}---------
            RunnableLambda(lambda inputs: {
                "reframed_output": reframing_chain.invoke({
                    "question": inputs["question"],
                    "chat_history": inputs["chat_history"]
                }) or "",
                "chat_history": inputs["chat_history"]
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Reframing output: {inputs.get('reframed_output')}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Extract the final reframed question from the AIMessage object (if available).}---------
            #---------{We remove any chain-of-thought or formatting by stripping.}---------
            #---------{We keep 'chat_history' to preserve memory for later steps.}---------
            RunnableLambda(lambda inputs: {
                "reframed_question": inputs["reframed_output"].content.strip()
                                     if hasattr(inputs["reframed_output"], 'content')
                                     else str(inputs["reframed_output"]),
                "chat_history": inputs["chat_history"]
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Reframed question extracted: {inputs.get('reframed_question')}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Document retrieval step using retriever:}---------
            #---------{Use the reframed question to get relevant context documents.}---------
            #---------{Also forward 'chat_history' for potential use in subsequent steps.}---------
            RunnableLambda(lambda inputs: {
                "reframed_question": inputs["reframed_question"],
                "chat_history": inputs["chat_history"],
                "context_docs": retriever.invoke(inputs["reframed_question"]) or []
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Retrieved context docs: {inputs.get('context_docs')}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Combine the retrieved documents into a single text string ('context'):}---------
            #---------{Concatenate all page contents from the documents.}---------
            #---------{Also forward 'reframed_question' and 'chat_history'.}---------
            RunnableLambda(lambda inputs: {
                "context": "".join(
                    f"[Metadata: {', '.join(f'{k}={v}' for k, v in clean_metadata(doc.metadata).items())}]\n{doc.page_content}"
                    for doc in (inputs["context_docs"] or [])
                ),
                "reframed_question": inputs["reframed_question"],
                "chat_history": inputs["chat_history"]
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Context concatenated: {inputs.get('context')}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Summarization step:}---------
            #---------{Send the combined 'context' and 'reframed_question' to the summarization chain.}---------
            #---------{Forward 'chat_history' as well for completeness.}---------
            RunnableLambda(lambda inputs: {
                "summary_output": summarization_chain.invoke({
                    "context": inputs["context"],
                    "reframed_question": inputs["reframed_question"],
                    "chat_history": inputs["chat_history"]
                }),
                "reframed_question": inputs["reframed_question"],
                "chat_history": inputs["chat_history"]
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Summary output: {inputs.get('summary_output')}", log_file=log_base, echo=echo),
                inputs
            )[1]) |

            #---------{Prepare the final answer:}---------
            #---------{Parse the summarization output (AIMessage object or string).}---------
            #---------{Extract plain text and store it as 'answer'.}---------
            RunnableLambda(lambda inputs: {
                "answer": output_parser.parse(
                    inputs["summary_output"].content.strip()
                    if hasattr(inputs["summary_output"], 'content')
                    else str(inputs["summary_output"])
                ),
                "reframed_question": inputs["reframed_question"]
            }) |

            #---------{Logging Steps}---------
            RunnableLambda(lambda inputs: (
                log_message(f"[Step] Final answer parsed: {inputs.get('answer')}", log_file=log_base, echo=echo),
                log_message(f"[Step] Reframed question parsed: {inputs.get('reframed_question', [])}", log_file=log_base, echo=echo),
                inputs
            )[-1])
        )

        
        # ---{Helper function to get/store memory }---
        def get_session_history(session_id):
            return get_memory(session_id=session_id, log_base=log_base, echo=echo)
    
        full_chain = RunnableWithMessageHistory(
            runnable=chain,
            get_session_history=get_session_history,
            input_key="question",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        log_message("[Success] Chat chain built successfully.", log_file=log_base, echo=echo)
        return full_chain
    except Exception as e:
        log_message(f"[Error] build_chat_chain: {e}", log_file=log_base, echo=echo)
        raise