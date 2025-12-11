# src/graphs/docs_agent_graph.py

from typing import TypedDict, List
import os
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document


DOCS_DIR = Path("docs")


class DocsAgentState(TypedDict, total=False):
    question: str
    retrieved_docs: List[Document]
    answer: str


# ---- Cargar documentos y vectorstore (simple, en memoria) ----

def load_docs() -> List[Document]:
    docs: List[Document] = []
    for path in DOCS_DIR.glob("*.md"):
        loader = TextLoader(str(path), encoding="utf-8")
        docs.extend(loader.load())
    return docs


# Embeddings y vectorstore globales (en memoria)
_docs = load_docs()
_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
_vectorstore = FAISS.from_documents(_docs, _embeddings)
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 4})


def get_llm():
    # reutilizamos el mismo modelo local
    return ChatOllama(model="mistral", base_url="http://localhost:11434", temperature=0)


# ---- Nodos del grafo ----

def retrieve_docs_node(state: DocsAgentState) -> DocsAgentState:
    question = state["question"]
    # En las versiones nuevas de LangChain, los retrievers son Runnable:
    docs = _retriever.invoke(question)
    return {**state, "retrieved_docs": docs}

def answer_from_docs_node(state: DocsAgentState) -> DocsAgentState:
    llm = get_llm()
    question = state["question"]
    docs = state.get("retrieved_docs", [])

    context = "\n\n".join([f"[{i}] {d.page_content}" for i, d in enumerate(docs)])

    system_msg = SystemMessage(
        content=(
            "Eres un asistente experto en el dominio retail de esta empresa. "
            "Respondes usando ÚNICAMENTE la información del contexto proporcionado. "
            "Si no tienes suficiente información, dilo explícitamente."
        )
    )
    user_msg = HumanMessage(
        content=(
            f"Pregunta del usuario:\n{question}\n\n"
            f"Contexto disponible (documentos):\n{context}\n\n"
            "Redacta una respuesta clara en castellano, citando ideas de los documentos cuando sea relevante."
        )
    )

    resp = llm.invoke([system_msg, user_msg])
    return {**state, "answer": resp.content}


def build_docs_agent_graph():
    graph = StateGraph(DocsAgentState)

    graph.add_node("retrieve_docs", retrieve_docs_node)
    graph.add_node("answer_from_docs", answer_from_docs_node)

    graph.set_entry_point("retrieve_docs")
    graph.add_edge("retrieve_docs", "answer_from_docs")
    graph.add_edge("answer_from_docs", END)

    return graph.compile()
