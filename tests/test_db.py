"""
Tests para el módulo de base de datos (src/data/db.py)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from src.data.db import get_engine, run_query


class TestGetEngine:
    """Tests para la función get_engine"""

    def setup_method(self):
        """Limpia el estado global entre tests"""
        import src.data.db
        src.data.db._engine = None

    def test_get_engine_returns_engine(self):
        """Verifica que get_engine devuelva un objeto Engine"""
        with patch("src.data.db.get_settings") as mock_settings:
            mock_settings.return_value.oracle_sqlalchemy_url = "sqlite:///:memory:"
            engine = get_engine()
            assert engine is not None

    def test_get_engine_singleton(self):
        """Verifica que get_engine devuelve la misma instancia (singleton)"""
        with patch("src.data.db.get_settings") as mock_settings:
            mock_settings.return_value.oracle_sqlalchemy_url = "sqlite:///:memory:"
            engine1 = get_engine()
            engine2 = get_engine()
            assert engine1 is engine2


class TestRunQuery:
    """Tests para la función run_query"""

    def setup_method(self):
        """Configura un motor de base de datos en memoria para tests"""
        import src.data.db
        src.data.db._engine = None
        self.test_engine = create_engine("sqlite:///:memory:")
        # Crear tabla de prueba
        with self.test_engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_table (id INTEGER, name TEXT)"))
            conn.execute(text("INSERT INTO test_table VALUES (1, 'Alice')"))
            conn.execute(text("INSERT INTO test_table VALUES (2, 'Bob')"))
            conn.commit()

    def test_run_query_basic_select(self):
        """Verifica que run_query ejecute un SELECT básico"""
        with patch("src.data.db.get_engine", return_value=self.test_engine):
            result = run_query("SELECT * FROM test_table")
            assert len(result) == 2
            assert result[0]["name"] in ["Alice", "Bob"]

    def test_run_query_with_params(self):
        """Verifica que run_query acepte parámetros"""
        with patch("src.data.db.get_engine", return_value=self.test_engine):
            result = run_query(
                "SELECT * FROM test_table WHERE id = :id", {"id": 1}
            )
            assert len(result) == 1
            assert result[0]["id"] == 1

    def test_run_query_empty_result(self):
        """Verifica que run_query maneje resultados vacíos"""
        with patch("src.data.db.get_engine", return_value=self.test_engine):
            result = run_query("SELECT * FROM test_table WHERE id = :id", {"id": 999})
            assert result == []

    def test_run_query_returns_dicts(self):
        """Verifica que run_query devuelva lista de dicts"""
        with patch("src.data.db.get_engine", return_value=self.test_engine):
            result = run_query("SELECT * FROM test_table")
            assert isinstance(result, list)
            assert all(isinstance(row, dict) for row in result)

    def test_run_query_database_error(self):
        """Verifica que run_query lance RuntimeError en caso de error SQL"""
        with patch("src.data.db.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine
            mock_engine.connect.side_effect = SQLAlchemyError("Connection failed")

            with pytest.raises(RuntimeError, match="Database error"):
                run_query("SELECT * FROM nonexistent_table")

    def test_run_query_with_no_params(self):
        """Verifica que run_query funcione sin parámetros"""
        with patch("src.data.db.get_engine", return_value=self.test_engine):
            result = run_query("SELECT COUNT(*) as count FROM test_table")
            assert len(result) == 1
            assert result[0]["count"] == 2
