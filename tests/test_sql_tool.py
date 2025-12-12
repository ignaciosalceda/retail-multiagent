"""
Tests para el módulo de herramientas SQL (src/tools/sql_tool.py)
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from src.tools.sql_tool import (
    query_retail_database,
    _truncate_rows,
    _rows_to_markdown,
)


class TestTruncateRows:
    """Tests para la función _truncate_rows"""

    def test_truncate_rows_no_truncation_needed(self):
        """Verifica que no se truncen filas cuando hay menos del máximo"""
        rows = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = _truncate_rows(rows, max_rows=10)
        assert result == rows
        assert len(result) == 2

    def test_truncate_rows_truncation_needed(self):
        """Verifica que se truncen filas cuando se excede el máximo"""
        rows = [{"id": i, "name": f"Person{i}"} for i in range(100)]
        result = _truncate_rows(rows, max_rows=50)
        assert len(result) == 50
        assert result == rows[:50]

    def test_truncate_rows_empty_list(self):
        """Verifica que _truncate_rows maneje listas vacías"""
        result = _truncate_rows([], max_rows=50)
        assert result == []

    def test_truncate_rows_default_max(self):
        """Verifica que el máximo por defecto sea 50"""
        rows = [{"id": i} for i in range(100)]
        result = _truncate_rows(rows)
        assert len(result) == 50


class TestRowsToMarkdown:
    """Tests para la función _rows_to_markdown"""

    def test_rows_to_markdown_basic(self):
        """Verifica que se genere tabla markdown básica"""
        rows = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ]
        result = _rows_to_markdown(rows)

        assert "| id | name | age |" in result
        assert "| --- | --- | --- |" in result
        assert "| 1 | Alice | 30 |" in result
        assert "| 2 | Bob | 25 |" in result

    def test_rows_to_markdown_empty_list(self):
        """Verifica que se retorne 'No results.' para lista vacía"""
        result = _rows_to_markdown([])
        assert result == "No results."

    def test_rows_to_markdown_single_row(self):
        """Verifica que se genere tabla markdown con una sola fila"""
        rows = [{"col1": "value1", "col2": "value2"}]
        result = _rows_to_markdown(rows)

        assert "| col1 | col2 |" in result
        assert "| value1 | value2 |" in result

    def test_rows_to_markdown_missing_values(self):
        """Verifica que se manejen valores faltantes correctamente"""
        rows = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob"},  # falta email
        ]
        result = _rows_to_markdown(rows)

        assert "| 1 | Alice | alice@example.com |" in result
        assert "| 2 | Bob |  |" in result

    def test_rows_to_markdown_various_types(self):
        """Verifica que se manejen diferentes tipos de datos"""
        rows = [{"int_val": 42, "float_val": 3.14, "str_val": "text", "bool_val": True}]
        result = _rows_to_markdown(rows)

        assert "42" in result
        assert "3.14" in result
        assert "text" in result
        assert "True" in result


class TestQueryRetailDatabase:
    """Tests para la herramienta query_retail_database"""

    def test_query_select_allowed(self):
        """Verifica que se acepten queries SELECT"""
        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.return_value = [
                {"id": 1, "name": "Product1"},
                {"id": 2, "name": "Product2"},
            ]
            # query_retail_database es un StructuredTool, accedemos a su función
            result = query_retail_database.invoke({"sql_query": "SELECT * FROM productos"})
            data = json.loads(result)

            assert "rows" in data
            assert "markdown_table" in data
            assert len(data["rows"]) == 2

    def test_query_select_uppercase_allowed(self):
        """Verifica que SELECT mayúsculas sea aceptado"""
        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.return_value = []
            result = query_retail_database.invoke({"sql_query": "SELECT id FROM table"})
            data = json.loads(result)
            assert "rows" in data

    def test_query_insert_denied(self):
        """Verifica que INSERT sea rechazado"""
        result = query_retail_database.invoke({"sql_query": "INSERT INTO productos VALUES (1, 'test')"})
        data = json.loads(result)

        assert "error" in data
        assert "Only SELECT queries are allowed" in data["error"]

    def test_query_delete_denied(self):
        """Verifica que DELETE sea rechazado"""
        result = query_retail_database.invoke({"sql_query": "DELETE FROM productos WHERE id = 1"})
        data = json.loads(result)

        assert "error" in data

    def test_query_update_denied(self):
        """Verifica que UPDATE sea rechazado"""
        result = query_retail_database.invoke({"sql_query": "UPDATE productos SET name = 'test'"})
        data = json.loads(result)

        assert "error" in data

    def test_query_drop_denied(self):
        """Verifica que DROP sea rechazado"""
        result = query_retail_database.invoke({"sql_query": "DROP TABLE productos"})
        data = json.loads(result)

        assert "error" in data

    def test_query_database_error_handling(self):
        """Verifica que se manejen errores de base de datos"""
        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.side_effect = Exception("Connection timeout")
            result = query_retail_database.invoke({"sql_query": "SELECT * FROM productos"})
            data = json.loads(result)

            assert "error" in data
            assert "Connection timeout" in data["error"]

    def test_query_return_format(self):
        """Verifica que la respuesta tenga el formato correcto"""
        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.return_value = [{"col1": "val1"}]
            result = query_retail_database.invoke({"sql_query": "SELECT * FROM table"})
            data = json.loads(result)

            assert isinstance(data, dict)
            assert "rows" in data
            assert "markdown_table" in data

    def test_query_truncation(self):
        """Verifica que se limiten a 50 filas los resultados"""
        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            rows = [{"id": i, "value": f"val{i}"} for i in range(100)]
            mock_run_query.return_value = rows
            result = query_retail_database.invoke({"sql_query": "SELECT * FROM large_table"})
            data = json.loads(result)

            assert len(data["rows"]) == 50

    def test_query_special_characters_in_values(self):
        """Verifica que se manejen caracteres especiales en los datos"""
        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.return_value = [
                {"id": 1, "text": "Valor con 'comillas' y \"dobles\""}
            ]
            result = query_retail_database.invoke({"sql_query": "SELECT * FROM table"})
            data = json.loads(result)

            assert len(data["rows"]) == 1
            assert "Valor con 'comillas'" in data["rows"][0]["text"]
