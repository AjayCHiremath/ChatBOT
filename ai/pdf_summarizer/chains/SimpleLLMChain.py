def get_chat_chain(prompt, llm, parser):
    return prompt | llm | parser