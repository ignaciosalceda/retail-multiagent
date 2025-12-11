# src/experiments/run_report_graph.py

from src.graphs.report_agent_graph import build_report_agent_graph

def main():
    app = build_report_agent_graph()

    test_state = {
        "question": "Dame las ventas por categoría y explícamelo con contexto.",
        "intent": "mixed",
        "sql_answer": "La categoría con más ventas es Limpieza con 220.326 €.",
        "sql_markdown": "| categoria | total |\n|---|---|\n| Limpieza | 220326 |",
        "docs_answer": "La categoría Limpieza incluye productos domésticos esenciales."
    }

    result = app.invoke(test_state)

    print("\n=== MARKDOWN GENERADO ===\n")
    print(result.get("report_markdown"))

    print("\n=== PDF GENERADO ===")
    print(result.get("pdf_path"))

if __name__ == "__main__":
    main()
