# src/tools/test_sql_tool.py

from src.tools.sql_tool import query_retail_database


def main():
    # Ajusta el nombre de la tabla a la que tengas (p.ej. ventas, sales, etc.)
    sql = "SELECT * FROM ventas LIMIT 10;"
    result_json = query_retail_database.invoke({"sql_query": sql})
    # .invoke devuelve ya la salida del tool (en este caso, el JSON string)
    print(result_json)


if __name__ == "__main__":
    main()
