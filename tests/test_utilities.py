"""
Tests para validación y utilidades del proyecto
"""

import pytest
from datetime import datetime


class TestDataValidation:
    """Tests para validación de datos"""

    def test_sql_query_validation(self):
        """Verifica que se validen correctamente queries SQL"""
        from src.tools.sql_tool import query_retail_database
        import json

        # Query válida
        result = query_retail_database.invoke({"sql_query": "SELECT 1 as col1"})
        data = json.loads(result)
        assert "rows" in data or "error" not in data

    def test_invalid_sql_detection(self):
        """Verifica que se detecten queries inválidas"""
        from src.tools.sql_tool import query_retail_database
        import json

        invalid_queries = [
            "DELETE FROM tabla",
            "DROP TABLE tabla",
            "INSERT INTO tabla VALUES (1, 2)",
            "UPDATE tabla SET col = 1",
        ]

        for query in invalid_queries:
            result = query_retail_database.invoke({"sql_query": query})
            data = json.loads(result)
            assert "error" in data


class TestDataFormatting:
    """Tests para formato de datos"""

    def test_decimal_handling(self):
        """Verifica que se manejen decimales correctamente"""
        from decimal import Decimal
        from src.tools.sql_tool import _rows_to_markdown

        rows = [
            {"price": Decimal("99.99"), "quantity": Decimal("5")},
            {"price": Decimal("15.50"), "quantity": Decimal("10")},
        ]

        result = _rows_to_markdown(rows)

        assert "99.99" in result
        assert "15.50" in result

    def test_null_value_handling(self):
        """Verifica que se manejen valores NULL correctamente"""
        from src.tools.sql_tool import _rows_to_markdown

        rows = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": None},
        ]

        result = _rows_to_markdown(rows)

        assert "Alice" in result
        assert "Bob" in result
        # None se convierte a string "None"
        assert "|" in result

    def test_datetime_handling(self):
        """Verifica que se manejen datetimes correctamente"""
        from src.tools.sql_tool import _rows_to_markdown

        rows = [
            {"id": 1, "created_at": datetime(2024, 1, 15, 10, 30, 0)},
            {"id": 2, "created_at": datetime(2024, 1, 16, 14, 45, 30)},
        ]

        result = _rows_to_markdown(rows)

        assert "2024" in result


class TestErrorHandling:
    """Tests para manejo de errores"""

    def test_database_connection_error_handling(self):
        """Verifica que se manejen errores de conexión"""
        from unittest.mock import patch
        from src.tools.sql_tool import query_retail_database
        import json

        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.side_effect = RuntimeError("Connection refused")
            result = query_retail_database.invoke({"sql_query": "SELECT 1"})
            data = json.loads(result)

            assert "error" in data
            assert "Connection refused" in data["error"]

    def test_timeout_handling(self):
        """Verifica que se manejen timeouts"""
        from unittest.mock import patch
        from src.tools.sql_tool import query_retail_database
        import json

        with patch("src.tools.sql_tool.run_query") as mock_run_query:
            mock_run_query.side_effect = TimeoutError("Query timeout after 30s")
            result = query_retail_database.invoke({"sql_query": "SELECT * FROM large_table"})
            data = json.loads(result)

            assert "error" in data


class TestPerformance:
    """Tests de rendimiento básicos"""

    def test_truncation_performance(self):
        """Verifica que truncar 1000 filas sea rápido"""
        from src.tools.sql_tool import _truncate_rows
        import time

        # Crear 10000 filas
        rows = [{"id": i, "value": f"value_{i}"} for i in range(10000)]

        start = time.time()
        result = _truncate_rows(rows, max_rows=50)
        elapsed = time.time() - start

        assert len(result) == 50
        # Debería ser casi instantáneo (< 1 segundo)
        assert elapsed < 1.0

    def test_markdown_conversion_performance(self):
        """Verifica que convertir 1000 filas a markdown sea rápido"""
        from src.tools.sql_tool import _rows_to_markdown
        import time

        rows = [
            {"id": i, "name": f"Product_{i}", "price": 99.99 + i}
            for i in range(1000)
        ]

        start = time.time()
        result = _rows_to_markdown(rows)
        elapsed = time.time() - start

        assert len(result) > 0
        # Debería ser rápido (< 1 segundo)
        assert elapsed < 1.0
