from langchain_ollama import ChatOllama


def init_chat_llm(
    model: str = "llama3.2:latest", temperature: float = 0.0
) -> ChatOllama:
    llm = ChatOllama(model=model, temperature=temperature)

    return llm
