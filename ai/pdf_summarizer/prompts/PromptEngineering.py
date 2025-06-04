from langchain.prompts import ChatPromptTemplate

def get_prompt_template():
    return ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Please respond to the questions asked."),
        ("user", "Question: {question}")
    ])