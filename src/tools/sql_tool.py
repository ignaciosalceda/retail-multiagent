# src/tools/sql_tool.py

from typing import Any, Dict, List
import json

from langchain_core.tools import tool

from src.data.db import run_query


def _truncate_rows(rows: List[Dict[str, Any]], max_rows: int = 50) -> List[Dict[str, Any]]:
    """
    Limita el número de filas para no devolver tochos gigantes al modelo.
    """
    if len(rows) <= max_rows:
        return rows
    return rows[:max_rows]


def _rows_to_markdown(rows: List[Dict[str, Any]]) -> str:
    """
    Convierte una lista de dicts en una tabla markdown simple.
    Útil para que el modelo lo lea y lo explique al usuario.
    """
    if not rows:
        return "No results."

    headers = list(rows[0].keys())
    # Encabezados
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"

    # Filas
    row_lines = []
    for row in rows:
        values = [str(row.get(h, "")) for h in headers]
        row_lines.append("| " + " | ".join(values) + " |")

    return "\n".join([header_line, separator_line] + row_lines)


@tool("query_retail_database")
def query_retail_database(sql_query: str) -> str:
    """
    Ejecuta una consulta SQL de solo lectura sobre la base de datos retail.

    IMPORTANTE (para el modelo que use esta tool):
    - Solo se permiten consultas SELECT (nunca INSERT, UPDATE, DELETE, DROP, etc.).
    - Utiliza las tablas del esquema retail (por ejemplo: ventas, tiendas, productos, regiones, clientes, etc.).
    - Intenta ser lo más específico posible con columnas y condiciones.

    Devuelve:
    - Un JSON con dos campos:
        - "rows": lista de filas (máx. 50) en formato dict.
        - "markdown_table": representación en tabla markdown de los resultados.
    """
    # Seguridad básica: no permitimos nada que no sea SELECT
    lower_sql = sql_query.strip().lower()
    if not lower_sql.startswith("select"):
        return json.dumps(
            {
                "error": "Only SELECT queries are allowed.",
                "rows": [],
                "markdown_table": "",
            }
        )

    try:
        rows = run_query(sql_query)
        rows_trunc = _truncate_rows(rows, max_rows=50)
        markdown = _rows_to_markdown(rows_trunc)
        return json.dumps(
            {
                "rows": rows_trunc,
                "markdown_table": markdown,
            },
            default=str,  # por si hay tipos raros (Decimal, datetime, etc.)
        )
    except Exception as e:
        return json.dumps(
            {
                "error": f"Database error: {e}",
                "rows": [],
                "markdown_table": "",
            }
        )
