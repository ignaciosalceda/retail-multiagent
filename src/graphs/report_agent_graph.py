# src/graphs/report_agent_graph.py

from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.llm import get_llm
from src.reports.pdf_generator import markdown_to_pdf


class ReportState(TypedDict, total=False):
    question: str
    intent: str

    sql_answer: str
    sql_markdown: str
    docs_answer: str

    report_markdown: str
    pdf_path: str

def generate_report_markdown_node(state: ReportState) -> ReportState:
    llm = get_llm()

    system_msg = SystemMessage(
        content=(
            "Eres un analista senior que redacta informes ejecutivos en formato Markdown. "
            "Tu trabajo es transformar resultados técnicos en un informe claro, estructurado "
            "y profesional para negocio."
        )
    )

    user_msg = HumanMessage(
        content=(
            f"Pregunta del usuario:\n{state.get('question')}\n\n"
            f"Intención detectada:\n{state.get('intent')}\n\n"
            f"Resultados SQL (si existen):\n{state.get('sql_answer')}\n\n"
            f"Tabla SQL (si existe):\n{state.get('sql_markdown')}\n\n"
            f"Resultados de documentación (si existen):\n{state.get('docs_answer')}\n\n"
            "Genera un informe en Markdown con esta estructura:\n"
            "# Informe de análisis\n"
            "## 1. Pregunta\n"
            "## 2. Resumen ejecutivo\n"
            "## 3. Resultados cuantitativos (si hay SQL)\n"
            "## 4. Contexto documental (si existe)\n"
            "## 5. Conclusiones\n"
        )
    )

    resp = llm.invoke([system_msg, user_msg])

    return {
        **state,
        "report_markdown": resp.content
    }

def generate_pdf_node(state: ReportState) -> ReportState:
    markdown = state["report_markdown"]
    pdf_path = markdown_to_pdf(markdown, output_path="final_report.pdf")

    return {
        **state,
        "pdf_path": pdf_path
    }


def build_report_agent_graph():
    graph = StateGraph(ReportState)

    graph.add_node("generate_markdown", generate_report_markdown_node)
    graph.add_node("generate_pdf", generate_pdf_node)

    graph.set_entry_point("generate_markdown")
    graph.add_edge("generate_markdown", "generate_pdf")
    graph.add_edge("generate_pdf", END)

    return graph.compile()
