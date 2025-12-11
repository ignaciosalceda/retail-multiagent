# src/experiments/run_docs_graph.py

from src.graphs.docs_agent_graph import build_docs_agent_graph


def main():
    app = build_docs_agent_graph()
    question = "Explícame qué tablas tiene la base de datos retail y qué significan sus columnas. Explícame el contexto de negocio detrás."

    result = app.invoke({"question": question})

    print("\n=== ESTADO FINAL DOCS AGENT ===")
    print("question:", result.get("question"))
    print("retrieved_docs:", len(result.get("retrieved_docs", [])))
    print("\n=== RESPUESTA ===")
    print(result.get("answer", ""))


if __name__ == "__main__":
    main()
