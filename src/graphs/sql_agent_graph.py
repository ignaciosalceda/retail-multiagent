# src/graphs/sql_agent_graph.py

from typing import TypedDict, List, Dict, Any
import re

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.llm import get_llm
from src.data.db import run_query


class SQLAgentState(TypedDict, total=False):
    question: str
    sql_raw: str
    sql_query: str
    sql_rows: List[Dict[str, Any]]
    sql_markdown: str
    answer: str


def extract_sql(text: str) -> str:
    code_block = re.search(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if code_block:
        return code_block.group(1).strip()
    return text.strip()


def sanitize_sql_for_oracle(sql: str) -> str:
    cleaned = sql.strip()
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()
    lower = cleaned.lower()
    if "fetch first" not in lower:
        cleaned = f"{cleaned}\nFETCH FIRST 50 ROWS ONLY"
    return cleaned


def rows_to_markdown(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No hay resultados."
    headers = list(rows[0].keys())
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = []
    for row in rows:
        values = [str(row.get(h, "")) for h in headers]
        row_lines.append("| " + " | ".join(values) + " |")
    return "\n".join([header_line, separator_line] + [*row_lines])

def generate_sql_node(state: SQLAgentState) -> SQLAgentState:
    llm = get_llm()
    system_sql = SystemMessage(
        content=(
            "Eres un generador de SQL para Oracle. "
            "Debes devolver ÚNICAMENTE una consulta SQL válida para Oracle, sin explicación. "
            "Usa las tablas: categorias(id, nombre), productos(id, nombre, categoria_id, precio), "
            "tiendas(id, nombre, ciudad), ventas(id, fecha, producto_id, tienda_id, cantidad, total). "
            "Usa siempre FETCH FIRST n ROWS ONLY para limitar filas, no uses LIMIT."
        )
    )
    user_sql = HumanMessage(
        content=(
            f"Genera una única consulta SQL para responder a la siguiente pregunta:\n\n{state['question']}\n\n"
            "Puedes devolverla dentro de un bloque ```sql``` si quieres."
        )
    )
    resp = llm.invoke([system_sql, user_sql])
    sql_raw = extract_sql(resp.content)
    return {**state, "sql_raw": sql_raw}

def sanitize_sql_node(state: SQLAgentState) -> SQLAgentState:
    sql_raw = state["sql_raw"]
    sql_query = sanitize_sql_for_oracle(sql_raw)
    return {**state, "sql_query": sql_query}

def execute_sql_node(state: SQLAgentState) -> SQLAgentState:
    sql_query = state["sql_query"]
    rows = run_query(sql_query)
    markdown = rows_to_markdown(rows[:50])
    return {**state, "sql_rows": rows, "sql_markdown": markdown}

def explain_sql_node(state: SQLAgentState) -> SQLAgentState:
    llm = get_llm()
    system_explain = SystemMessage(
        content=(
            "Eres un analista de datos retail. "
            "Explicas resultados de consultas SQL de forma clara y en castellano."
        )
    )

    explain_msg = HumanMessage(
        content=(
            f"Pregunta original del usuario:\n{state['question']}\n\n"
            f"Consulta SQL ejecutada:\n```sql\n{state['sql_query']}\n```\n\n"
            "Resultados (tabla en markdown):\n"
            f"{state['sql_markdown']}\n\n"
            "Explica de forma clara qué está pasando, resumiendo los resultados numéricos más relevantes."
        )
    )

    resp = llm.invoke([system_explain, explain_msg])
    return {**state, "answer": resp.content}

def build_sql_agent_graph():
    graph = StateGraph(SQLAgentState)

    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("sanitize_sql", sanitize_sql_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("explain_sql", explain_sql_node)

    graph.set_entry_point("generate_sql")
    graph.add_edge("generate_sql", "sanitize_sql")
    graph.add_edge("sanitize_sql", "execute_sql")
    graph.add_edge("execute_sql", "explain_sql")
    graph.add_edge("explain_sql", END)

    return graph.compile()
