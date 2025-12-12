"""
Tests para el módulo de configuración (src/config/settings.py)
"""

import pytest
import os
from unittest.mock import patch

from src.config.settings import Settings, get_settings


class TestSettings:
    """Tests para la clase Settings"""

    def test_settings_instantiation(self):
        """Verifica que Settings se pueda instanciar con parámetros válidos"""
        settings = Settings(
            oracle_user="testuser",
            oracle_password="testpass",
            oracle_dsn="localhost:1521/XEPDB1",
        )
        assert settings.oracle_user == "testuser"
        assert settings.oracle_password == "testpass"
        assert settings.oracle_dsn == "localhost:1521/XEPDB1"

    def test_oracle_sqlalchemy_url_generation(self):
        """Verifica que la URL de SQLAlchemy se genere correctamente"""
        settings = Settings(
            oracle_user="retail",
            oracle_password="retail123",
            oracle_dsn="localhost:1521/XEPDB1",
        )
        expected_url = "oracle+oracledb://retail:retail123@localhost:1521/?service_name=XEPDB1"
        assert settings.oracle_sqlalchemy_url == expected_url

    def test_oracle_sqlalchemy_url_with_different_host_port(self):
        """Verifica que la URL se genere correctamente con diferentes host/puerto"""
        settings = Settings(
            oracle_user="user1",
            oracle_password="pass1",
            oracle_dsn="db-server.example.com:1522/PROD",
        )
        expected_url = "oracle+oracledb://user1:pass1@db-server.example.com:1522/?service_name=PROD"
        assert settings.oracle_sqlalchemy_url == expected_url

    @patch.dict(
        os.environ,
        {
            "ORACLE_USER": "env_user",
            "ORACLE_PASSWORD": "env_pass",
            "ORACLE_DSN": "env_host:1521/ENVDB",
        },
    )
    def test_get_settings_from_env(self):
        """Verifica que get_settings carga las variables del entorno"""
        # Limpiar cache de lru_cache
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.oracle_user == "env_user"
        assert settings.oracle_password == "env_pass"
        assert settings.oracle_dsn == "env_host:1521/ENVDB"
        # Limpiar cache para no afectar otros tests
        get_settings.cache_clear()

    @patch.dict(os.environ, {}, clear=True)
    def test_get_settings_default_values(self):
        """Verifica que get_settings usa valores por defecto si no hay env vars"""
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.oracle_user == "retail"
        assert settings.oracle_password == "retail"
        assert settings.oracle_dsn == "localhost:1521/XEPDB1"
        get_settings.cache_clear()

    def test_settings_missing_required_field(self):
        """Verifica que Settings requiere los campos obligatorios"""
        with pytest.raises(Exception):
            Settings(oracle_user="user", oracle_password="pass")
