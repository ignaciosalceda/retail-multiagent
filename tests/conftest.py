"""
Configuración de pytest para los tests del proyecto
"""

import pytest
import os
import sys

# Asegurarse de que el directorio raíz del proyecto está en PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))


@pytest.fixture(scope="session")
def test_db_url():
    """Proporciona una URL de base de datos en memoria para tests"""
    return "sqlite:///:memory:"


@pytest.fixture
def mock_settings():
    """Proporciona un objeto Settings mockeado para tests"""
    from unittest.mock import MagicMock
    from src.config.settings import Settings

    settings = MagicMock(spec=Settings)
    settings.oracle_user = "test_user"
    settings.oracle_password = "test_pass"
    settings.oracle_dsn = "localhost:1521/XEPDB1"
    return settings


@pytest.fixture
def mock_llm():
    """Proporciona un objeto LLM mockeado para tests"""
    from unittest.mock import MagicMock

    llm = MagicMock()
    llm.invoke.return_value.content = '{"intent": "sql", "reason": "test"}'
    return llm


def pytest_configure(config):
    """Hook de configuración de pytest"""
    # Aquí se pueden agregar configuraciones globales si es necesario
    pass
