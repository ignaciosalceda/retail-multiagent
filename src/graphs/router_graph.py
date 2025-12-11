# src/graphs/router_graph.py

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.llm import get_llm
from src.graphs.sql_agent_graph import build_sql_agent_graph
from src.graphs.docs_agent_graph import build_docs_agent_graph


class GlobalState(TypedDict, total=False):
    question: str
    intent: Literal["sql", "docs"]
    route_reason: str

    # SQL results
    sql_answer: str
    sql_markdown: str

    # Docs results
    docs_answer: str


# --- Nodos de sub-flujos (usamos los graphs ya compilados) ---

_sql_app = build_sql_agent_graph()
_docs_app = build_docs_agent_graph()


def router_node(state: GlobalState) -> GlobalState:
    llm = get_llm()
    system_msg = SystemMessage(
        content=(
            "Eres un enrutador de intenciones para un sistema de ayuda analítica retail. "
            "Tienes que decidir si una pregunta del usuario requiere:\n"
            "- 'sql': cuando pide números, métricas, agregados, comparaciones basadas en datos de la BD.\n"
            "- 'docs': cuando pide definiciones, contexto de negocio, explicaciones de tablas, métricas o procesos.\n"
            "Responde SOLO con un JSON de la forma:\n"
            "{ \"intent\": \"sql|docs\", \"reason\": \"explicación breve\" }"
        )
    )
    user_msg = HumanMessage(content=f"Pregunta del usuario:\n{state['question']}")
    resp = llm.invoke([system_msg, user_msg])

    # Nos fiamos de que devuelva algo tipo JSON; si no, lo parcheas luego.
    import json
    try:
        data = json.loads(resp.content)
        intent = data.get("intent", "docs")
        reason = data.get("reason", "")
    except Exception:
        intent = "docs"
        reason = f"No pude parsear la respuesta del router, fallback a 'docs'. Respuesta LLM: {resp.content}"

    return {**state, "intent": intent, "route_reason": reason}


def sql_flow_node(state: GlobalState) -> GlobalState:
    # delegamos en el SQLAgentGraph
    question = state["question"]
    sql_state = _sql_app.invoke({"question": question})

    return {
        **state,
        "sql_answer": sql_state.get("answer", ""),
        "sql_markdown": sql_state.get("sql_markdown", ""),
    }


def docs_flow_node(state: GlobalState) -> GlobalState:
    question = state["question"]
    docs_state = _docs_app.invoke({"question": question})

    return {
        **state,
        "docs_answer": docs_state.get("answer", ""),
    }


def build_router_graph():
    graph = StateGraph(GlobalState)

    graph.add_node("router", router_node)
    graph.add_node("sql_flow", sql_flow_node)
    graph.add_node("docs_flow", docs_flow_node)

    graph.set_entry_point("router")

    # Router → elige a cuál ir según intent
    def route_after_router(state: GlobalState):
        intent = state.get("intent", "docs")
        if intent == "sql":
            return "sql_flow"
        else:
            return "docs_flow"

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "sql_flow": "sql_flow",
            "docs_flow": "docs_flow",
        },
    )

    # Ambos flujos terminan
    graph.add_edge("sql_flow", END)
    graph.add_edge("docs_flow", END)

    return graph.compile()
