"""
Tests para el módulo de configuración del LLM (src/config/llm.py)
"""

import pytest
from unittest.mock import patch, MagicMock

from src.config.llm import get_llm


class TestGetLLM:
    """Tests para la función get_llm"""

    @patch("src.config.llm.ChatOllama")
    def test_get_llm_returns_llm_instance(self, mock_chat_ollama):
        """Verifica que get_llm devuelva una instancia de LLM"""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        llm = get_llm()

        assert llm is not None
        mock_chat_ollama.assert_called_once()

    @patch("src.config.llm.ChatOllama")
    def test_get_llm_uses_correct_model(self, mock_chat_ollama):
        """Verifica que get_llm use el modelo especificado"""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        # Limpiar cache para este test
        get_llm.cache_clear()
        
        llm = get_llm()

        # Verificar que ChatOllama fue llamado
        assert mock_chat_ollama.called
        
        # Limpiar cache
        get_llm.cache_clear()

    @patch("src.config.llm.ChatOllama")
    def test_get_llm_singleton(self, mock_chat_ollama):
        """Verifica que get_llm devuelve la misma instancia (singleton)"""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        # Limpiar cache para este test
        get_llm.cache_clear()
        
        llm1 = get_llm()
        llm2 = get_llm()

        assert llm1 is llm2
        # ChatOllama debe ser llamado solo una vez debido al caching
        mock_chat_ollama.assert_called_once()
        
        # Limpiar cache
        get_llm.cache_clear()
