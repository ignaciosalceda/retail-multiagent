# src/data/test_db_connection.py
from src.data.db import run_query

def main():
    sql = "SELECT COUNT(*) AS num_ventas FROM ventas"
    rows = run_query(sql)
    print(rows)

if __name__ == "__main__":
    main()
