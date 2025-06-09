import streamlit as st
import re
import time

from ai.pdf_summarizer.models.ModelLoader import get_model
from ai.pdf_summarizer.models.OutputParsers import get_str_output_parser
from ai.pdf_summarizer.prompts.Prompts import get_cot_prompt, get_summarize_prompt, get_critique_prompt
from ai.pdf_summarizer.chains.Chain import build_chain, build_chat_chain
from ai.pdf_summarizer.rag.Retrivers import get_rag
from ai.pdf_summarizer.memory.Memory import add_message_to_history
from utils.logger.SessionId import get_session_id
from utils.logger.EventLogger import log_message

# ---{ Helper function to separate <think></think> }---
def parse_thought_and_answer(full_text, log_base="logs/chatbot/", echo=False):
    try:
        # -----------{Extract chain-of-thought between <think>...</think>}-----------
        think_match = re.search(r"<think\s*>(.*?)</think\s*>", full_text, re.DOTALL | re.IGNORECASE)
        chain_of_thought = think_match.group(1).strip() if think_match else None
        log_message("[Success] Extracted chain-of-thought successfully.", log_file=log_base, echo=echo)

        # -----------{Remove ALL <think>...</think> blocks from text}-----------
        summary = re.sub(r"<think\s*>.*?</think\s*>", "", full_text, flags=re.DOTALL | re.IGNORECASE).strip()
        log_message("[Success] Cleaned summary response successfully.", log_file=log_base, echo=echo)

        return chain_of_thought, summary
    except Exception as e:
        log_message(f"[Error] parse_thought_and_answer: {e}", log_file=log_base, echo=echo)
        raise

#---{Connect chains using models, prompts, and retrievers}---
def connect_chains(vectorstore, log_base="logs/chatbot/", echo=False):
    try:
        status_placeholder = st.empty()

        with status_placeholder.status("🤖 Generating your response...", expanded=True):
            #---{Retrieve user input & session id from session state}---
            user_input = st.session_state.user_input
            session_id = get_session_id()

            #---{Create RAG retriever}---
            st.write("📚 Finding relevant information...")
            time.sleep(0.5)
            retriever = get_rag(vectorstore=vectorstore, log_base=log_base, echo=echo)
            log_message("[Success] RAG retriever created successfully.", log_file=log_base, echo=echo)

            #---{Output Parser}---
            output_parser = get_str_output_parser()
            log_message("[Success] Ouput Parser created successfully.", log_file=log_base, echo=echo)

            #---{Initiate prompt templates}---
            st.write("💬 Preparing questions and summaries...")
            time.sleep(0.5)
            formatted_cot_prompt = get_cot_prompt()
            log_message("[Success] Chain-of-thought prompt created successfully.", log_file=log_base, echo=echo)

            #---{Initiate summary prompt templates}---
            formatted_summary_prompt = get_summarize_prompt()
            log_message("[Success] Summarization prompt created successfully.", log_file=log_base, echo=echo)

            #---{Get prompt model}---
            st.write("🤖 Details send to model...")
            time.sleep(0.5)
            prompt_model = get_model(model_work="question_reframer", log_base=log_base, echo=echo)
            log_message("[Success] Prompt model loaded successfully.", log_file=log_base, echo=echo)

            #---{Get summarizer model}---
            context_model = get_model(model_work="context_summarizer", log_base=log_base, echo=echo)
            log_message("[Success] Context summarizer model loaded successfully.", log_file=log_base, echo=echo)

            #---{Build chains}---
            st.write("🔗 Connecting all the pieces...")
            time.sleep(0.5)
            reframing_chain = build_chain(prompt=formatted_cot_prompt, model=prompt_model, log_base=log_base, echo=echo)
            summarization_chain = build_chain(prompt=formatted_summary_prompt, model=context_model, log_base=log_base, echo=echo)
            log_message("[Success] Chains built successfully.", log_file=log_base, echo=echo)

            #---{Build main chat chain}---
            chain = build_chat_chain(reframing_chain=reframing_chain, retriever=retriever, summarization_chain=summarization_chain, 
                                    output_parser=output_parser, log_base=log_base, echo=False)
            log_message("[Success] Chat chain built successfully.", log_file=log_base, echo=echo)

            #---{Invoke the chain with user input}---
            st.write("⚡ Getting your answer...")
            time.sleep(0.5)
            response = chain.invoke(
                {"question": user_input}, 
                {'configurable': {'session_id': session_id}}
            )
            #---{Parse the response}---
            st.write("⚡ Saving your memory...")
            time.sleep(0.5)
            reframed_question_response = response.get("reframed_question", "")
            raw_summary = response.get("answer", "")

            if raw_summary:
                chain_of_thought, summary_response = parse_thought_and_answer(
                    raw_summary, 
                    log_base=log_base, 
                    echo=echo
                )
            else:
                chain_of_thought, summary_response = "", "No response generated"

            #---{Saving the memory}---
            add_message_to_history(session_id=session_id,message=user_input,is_user=True, log_base=log_base, echo=echo)
            add_message_to_history(session_id=session_id,message=reframed_question_response,is_user=False, log_base=log_base, echo=echo)
            add_message_to_history(session_id=session_id,message=raw_summary,is_user=False, log_base=log_base, echo=echo)
            log_message("[Success] Saved Memory successfully.", log_file=log_base, echo=echo)
        return reframed_question_response, chain_of_thought, summary_response

    except Exception as e:
        log_message(f"[Error] connect_chains: {e}", log_file=log_base, echo=echo)
        raise