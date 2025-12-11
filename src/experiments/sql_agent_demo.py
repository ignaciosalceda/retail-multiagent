# src/experiments/sql_agent_demo.py

# src/experiments/sql_agent_demo.py

import re
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.config.llm import get_llm
from src.data.db import run_query


def extract_sql(text: str) -> str:
    """
    Extrae el SQL de un bloque de texto. Si viene dentro de ```sql ... ```,
    lo saca de ahí; si no, usa el texto completo.
    """
    code_block = re.search(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if code_block:
        return code_block.group(1).strip()
    return text.strip()


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

    return "\n".join([header_line, separator_line] + row_lines)

def sanitize_sql_for_oracle(sql: str) -> str:
    """
    Limpia la query:
    - Quita punto y coma final.
    - Opcionalmente añade FETCH FIRST n ROWS ONLY si no está.
    """
    cleaned = sql.strip()

    # Quitar ; final si lo hay
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    # Si no hay FETCH FIRST, añadimos un límite de seguridad
    lower = cleaned.lower()
    if "fetch first" not in lower:
        cleaned = f"{cleaned}\nFETCH FIRST 50 ROWS ONLY"

    return cleaned

def run_simple_sql_agent(question: str):
    llm = get_llm()

    # 1) Pedimos SOLO la query SQL
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
            f"Genera una única consulta SQL para responder a la siguiente pregunta:\n\n{question}\n\n"
            "Puedes devolverla dentro de un bloque ```sql``` si quieres."
        )
    )

    sql_response = llm.invoke([system_sql, user_sql])
    print("\n=== RESPUESTA DEL MODELO (GENERACIÓN SQL) ===")
    print(sql_response.content)

    sql_query_raw = extract_sql(sql_response.content)
    print("\n=== SQL EXTRAÍDO ===")
    print(sql_query_raw)

    sql_query = sanitize_sql_for_oracle(sql_query_raw)
    print("\n=== SQL TRAS SANEADO ===")
    print(sql_query)

    # 2) Ejecutamos el SQL contra Oracle
    try:
        rows = run_query(sql_query)
    except Exception as e:
        print("\n❌ Error ejecutando SQL contra la base de datos:")
        print(e)
        return

    print(f"\n=== Nº DE FILAS DEVUELTAS: {len(rows)} ===")
    md_table = rows_to_markdown(rows[:50])
    print("\n=== TABLA MARKDOWN (PREVISUALIZACIÓN) ===")
    print(md_table)

    # 3) Le pedimos al LLM que explique el resultado
    system_explain = SystemMessage(
        content=(
            "Eres un analista de datos retail. "
            "Explicas resultados de consultas SQL de forma clara y en castellano."
        )
    )

    explain_msg = HumanMessage(
        content=(
            f"Pregunta original del usuario:\n{question}\n\n"
            f"Consulta SQL ejecutada:\n```sql\n{sql_query}\n```\n\n"
            "Resultados (tabla en markdown):\n"
            f"{md_table}\n\n"
            "Explica de forma clara qué está pasando, resumiendo los resultados numéricos más relevantes."
        )
    )

    final_response = llm.invoke([system_explain, explain_msg])
    print("\n=== RESPUESTA FINAL AL USUARIO ===")
    print(final_response.content)



if __name__ == "__main__":
    pregunta = "Dame las ventas totales por categoría, ordenadas de mayor a menor."
    run_simple_sql_agent(pregunta)
