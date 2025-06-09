from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

#-----{Defines a prompt template for Chain-of-Thought question reframing}-----
def get_cot_prompt():
    #-----{Systems Role}-----
    system_message = (
        "You are a highly skilled research assistant who reframes research questions clearly and precisely. "
        "Given a chat history and the latest user question which might reference context in the chat history, "
        "formulate a standalone question that can be understood without the chat history. "
        "IMPORTANT: Provide ONLY the final reframed question in plain text. "
        "Do NOT include chain-of-thought, reasoning, or any explanation about how you generated the reframed question."
    )

    #-----{User Role}-----
    user_message = (
        "Question:\n{question}\n\n"
    )
    messages = [
        SystemMessagePromptTemplate.from_template(template=system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(template=user_message)
    ]
    return ChatPromptTemplate.from_messages(messages=messages)


#-----{Defines a prompt template for summarizing research paper excerpts}-----
def get_summarize_prompt():
    #-----{Systems Role}-----
    system_message = (
        "You are a helpful assistant that summarizes research papers in plain language. "
        "You only use the provided excerpts and do not add external information. "
        "You also consider the previous conversations (chat_history) given by the user "
        "to determine the context. "
        "format your answer using appropriate Markdown syntax—such as bullet points (🔹), "
        "numbered lists (1.), alphabetical lists (a.), bold (**text**), italics (*text*), quotes (>), "
        "headings (#, ##, ###), and tables (| Column | Column |)—when relevant to make the answer "
        "clearer and more readable, but avoid unnecessary formatting if not needed."
        "IMPORTANT: Always close any <think>...</think> blocks properly."
        "By default, limit your answer to a maximum of 4-5 sentences. "
        "If the user specifically requests a detailed answer, then provide up to 7-8 sentences maximum."
    )

    #-----{User Role}-----
    user_message = (
        "Context:\n{context}\n\n"
        "Question:\n{reframed_question}\n\n"
        "Chat History:\n{chat_history}\n\n"
        "Please follow these steps:\n"
        "Step 1: Read the research paper excerpt carefully.\n"
        "Step 2: Refer to the previous conversations provided in chat_history and determine "
        "whether the current question is relevant to that topic. If yes, answer accordingly based on both the context and chat_history.\n"
        "Step 3: If the question is not relevant to the chat_history but is relevant to the context, then answer based on the context alone, ignoring the chat_history.\n"
        "Step 4: If the question is NOT relevant to the context, politely explain that the question is not relevant. "
        "Then, suggest 1-3 alternative questions that would be relevant to the provided research paper excerpt.\n"
    )

    messages = [
        SystemMessagePromptTemplate.from_template(template=system_message),
        HumanMessagePromptTemplate.from_template(template=user_message)
    ]
    return ChatPromptTemplate.from_messages(messages=messages)


#-----{Defines a prompt template for critiquing answers with citations}-----
def get_critique_prompt():
    #-----{Systems Role}-----
    system_message = (
        "You are an academic reviewer. "
        "You critique answers for accuracy, completeness, and clarity. "
        "When possible, include references to the provided context to support your critique (e.g. [Source: Page X, Paragraph Y]). "
        "IMPORTANT: Provide ONLY the final critique in plain text. "
        "Do NOT include chain-of-thought, reasoning, or any explanation about how you generated the critique."
    )

    #-----{User Role}-----
    user_message = (
        "Answer:\n{answer}\n\n"
        "Context:\n{context}\n\n"
        "Please follow these steps:\n"
        "Step 1: Read the answer and the context carefully.\n"
        "Step 2: Critique the answer for accuracy, completeness, and clarity.\n"
        "Step 3: Provide references to the context where applicable (e.g. [Source: Page X, Paragraph Y]).\n"
        "IMPORTANT: Provide ONLY the final critique as plain text. "
        "Do NOT include chain-of-thought, reasoning, or any explanation about how you generated the critique. "
    )
    messages = [
        SystemMessagePromptTemplate.from_template(template=system_message),
        HumanMessagePromptTemplate.from_template(template=user_message)
    ]
    return ChatPromptTemplate.from_messages(messages=messages)