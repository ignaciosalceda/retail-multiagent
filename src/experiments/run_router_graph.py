# src/experiments/run_router_graph.py

from src.graphs.router_graph import build_router_graph


def main():
    app = build_router_graph()

    # Prueba 1: una pregunta claramente SQL
    question_sql = "Dame las ventas totales por categoría, ordenadas de mayor a menor."
    result_sql = app.invoke({"question": question_sql})

    print("\n=== PREGUNTA SQL ===")
    print("intent:", result_sql.get("intent"))
    print("route_reason:", result_sql.get("route_reason"))
    print("\n--- SQL ANSWER ---")
    print(result_sql.get("sql_answer", ""))
    print("\n--- SQL MARKDOWN ---")
    print(result_sql.get("sql_markdown", ""))

    # Prueba 2: una pregunta claramente docs
    question_docs = "Explícame qué tablas tiene la base de datos retail y el contexto de negocio."
    result_docs = app.invoke({"question": question_docs})

    print("\n\n=== PREGUNTA DOCS ===")
    print("intent:", result_docs.get("intent"))
    print("route_reason:", result_docs.get("route_reason"))
    print("\n--- DOCS ANSWER ---")
    print(result_docs.get("docs_answer", ""))


if __name__ == "__main__":
    main()
