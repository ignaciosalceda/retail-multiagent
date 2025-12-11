# src/experiments/run_sql_graph.py

from src.graphs.sql_agent_graph import build_sql_agent_graph


def main():
    app = build_sql_agent_graph()
    question = "Dame las ventas totales por categoría, ordenadas de mayor a menor."

    result_state = app.invoke({"question": question})

    print("\n=== ESTADO FINAL DEL GRAFO ===")
    for k, v in result_state.items():
        if k in ("sql_rows",):
            print(f"{k}: {type(v)} (len={len(v)})")
        else:
            print(f"{k}: {v if len(str(v)) < 500 else str(v)[:500] + '...'}")

    print("\n=== RESPUESTA FINAL AL USUARIO ===")
    print(result_state.get("answer", ""))


if __name__ == "__main__":
    main()
