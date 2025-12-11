# src/experiments/run_master_graph.py

from src.graphs.master_graph import build_master_graph


def main():
    app = build_master_graph()

    question = (
        "Quiero entender qué categoría vende más en términos de importe total y "
        "además que me expliques el contexto de negocio de esas categorías."
    )

    result = app.invoke({"question": question})

    print("\n=== ESTADO FINAL MASTER GRAPH ===")
    print("intent:", result.get("intent"))
    print("route_reason:", result.get("route_reason"))
    print("\n--- SQL ANSWER ---")
    print(result.get("sql_answer", ""))
    print("\n--- DOCS ANSWER ---")
    print(result.get("docs_answer", ""))
    print("\n--- REPORT MARKDOWN ---")
    print(result.get("report_markdown", "")[:800], "...")
    print("\n--- PDF PATH ---")
    print(result.get("pdf_path", ""))


if __name__ == "__main__":
    main()