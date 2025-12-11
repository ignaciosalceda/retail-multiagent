# src/config/llm.py

from functools import lru_cache
from langchain_ollama import ChatOllama


@lru_cache
def get_llm():
    """
    Devuelve un LLM local usando Ollama.
    """
    llm = ChatOllama(
        model="mistral",              # o el modelo que tengas realmente en ollama list
        base_url="http://localhost:11434",
        temperature=0,
    )
    return llm
