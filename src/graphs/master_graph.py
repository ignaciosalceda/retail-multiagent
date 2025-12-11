# src/graphs/master_graph.py

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END

from langchain_core.messages import SystemMessage, HumanMessage

from src.config.llm import get_llm
from src.graphs.sql_agent_graph import build_sql_agent_graph
from src.graphs.docs_agent_graph import build_docs_agent_graph
from src.graphs.report_agent_graph import build_report_agent_graph


class MasterState(TypedDict, total=False):
    question: str

    intent: Literal["sql", "docs", "mixed"]
    route_reason: str

    # Resultados SQL
    sql_answer: str
    sql_markdown: str

    # Resultados Docs
    docs_answer: str

    # Informe final
    report_markdown: str
    pdf_path: str


# Subgrafos ya compilados
_sql_app = build_sql_agent_graph()
_docs_app = build_docs_agent_graph()
_report_app = build_report_agent_graph()


# ---------- NODOS ----------

def router_node(state: MasterState) -> MasterState:
    llm = get_llm()
    system_msg = SystemMessage(
        content=(
            "Eres un enrutador de intenciones para un sistema analítico retail.\n"
            "Decide si la pregunta del usuario requiere:\n"
            "- 'sql': cuando pide números, métricas, comparaciones basadas en la BD.\n"
            "- 'docs': cuando pide definiciones, contexto, explicaciones del esquema o negocio.\n"
            "- 'mixed': cuando claramente necesita datos + contexto.\n"
            "Responde SOLO con un JSON como:\n"
            "{ \"intent\": \"sql|docs|mixed\", \"reason\": \"explicación breve\" }"
        )
    )
    user_msg = HumanMessage(content=f"Pregunta del usuario:\n{state['question']}")

    resp = llm.invoke([system_msg, user_msg])

    import json
    try:
        data = json.loads(resp.content)
        intent = data.get("intent", "docs")
        reason = data.get("reason", "")
        if intent not in ("sql", "docs", "mixed"):
            intent = "docs"
    except Exception:
        intent = "docs"
        reason = f"No se pudo parsear JSON desde la respuesta: {resp.content}"

    return {**state, "intent": intent, "route_reason": reason}


def sql_flow_node(state: MasterState) -> MasterState:
    question = state["question"]
    sql_state = _sql_app.invoke({"question": question})

    return {
        **state,
        "sql_answer": sql_state.get("answer", ""),
        "sql_markdown": sql_state.get("sql_markdown", ""),
    }


def docs_flow_node(state: MasterState) -> MasterState:
    question = state["question"]
    docs_state = _docs_app.invoke({"question": question})

    return {
        **state,
        "docs_answer": docs_state.get("answer", ""),
    }


def sql_and_docs_flow_node(state: MasterState) -> MasterState:
    # Primero SQL
    state_after_sql = sql_flow_node(state)
    # Luego Docs (usando ya el state enriquecido)
    state_after_docs = docs_flow_node(state_after_sql)
    return state_after_docs


def report_flow_node(state: MasterState) -> MasterState:
    # Preparamos el estado que espera el ReportAgent
    report_input = {
        "question": state.get("question", ""),
        "intent": state.get("intent", ""),
        "sql_answer": state.get("sql_answer", ""),
        "sql_markdown": state.get("sql_markdown", ""),
        "docs_answer": state.get("docs_answer", ""),
    }

    report_state = _report_app.invoke(report_input)

    return {
        **state,
        "report_markdown": report_state.get("report_markdown", ""),
        "pdf_path": report_state.get("pdf_path", ""),
    }


def build_master_graph():
    graph = StateGraph(MasterState)

    graph.add_node("router", router_node)
    graph.add_node("sql_flow", sql_flow_node)
    graph.add_node("docs_flow", docs_flow_node)
    graph.add_node("sql_and_docs_flow", sql_and_docs_flow_node)
    graph.add_node("report_flow", report_flow_node)

    graph.set_entry_point("router")

    # Condicional desde router
    def route_after_router(state: MasterState):
        intent = state.get("intent", "docs")
        if intent == "sql":
            return "sql_flow"
        elif intent == "docs":
            return "docs_flow"
        else:
            return "sql_and_docs_flow"

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "sql_flow": "sql_flow",
            "docs_flow": "docs_flow",
            "sql_and_docs_flow": "sql_and_docs_flow",
        },
    )

    # Tras cualquier flujo → report
    graph.add_edge("sql_flow", "report_flow")
    graph.add_edge("docs_flow", "report_flow")
    graph.add_edge("sql_and_docs_flow", "report_flow")

    graph.add_edge("report_flow", END)

    return graph.compile()
