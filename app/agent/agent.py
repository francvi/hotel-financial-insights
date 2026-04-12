from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from .system_prompt import SYSTEM_PROMPT

LLM_MODEL = "llama3.2:latest"

llm = ChatOllama(model=LLM_MODEL, temperature=0.2)


def build_agent(tools=None, system_prompt=None):
    return create_agent(
        model=llm,
        tools=tools or [],
        system_prompt=system_prompt or SYSTEM_PROMPT,
    )
