"""
Tests de integración para los flujos principales del proyecto
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestRouterGraph:
    """Tests para el router graph (src/graphs/router_graph.py)"""

    @patch("src.graphs.router_graph.get_llm")
    def test_router_node_sql_intent(self, mock_get_llm):
        """Verifica que el router detecte intención SQL"""
        from src.graphs.router_graph import router_node, GlobalState

        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps(
            {"intent": "sql", "reason": "request contains metrics"}
        )
        mock_get_llm.return_value = mock_llm

        state: GlobalState = {
            "question": "¿Cuáles fueron las ventas totales en 2023?"
        }
        result = router_node(state)

        assert result["intent"] == "sql"
        assert "route_reason" in result

    @patch("src.graphs.router_graph.get_llm")
    def test_router_node_docs_intent(self, mock_get_llm):
        """Verifica que el router detecte intención docs"""
        from src.graphs.router_graph import router_node, GlobalState

        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps(
            {"intent": "docs", "reason": "request is about definitions"}
        )
        mock_get_llm.return_value = mock_llm

        state: GlobalState = {
            "question": "¿Qué es una región de ventas?"
        }
        result = router_node(state)

        assert result["intent"] == "docs"

    @patch("src.graphs.router_graph.get_llm")
    def test_router_node_invalid_response_fallback(self, mock_get_llm):
        """Verifica que el router haga fallback a 'docs' si hay error"""
        from src.graphs.router_graph import router_node, GlobalState

        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "Invalid JSON response"
        mock_get_llm.return_value = mock_llm

        state: GlobalState = {"question": "Test question"}
        result = router_node(state)

        # Debe hacer fallback a 'docs'
        assert result["intent"] == "docs"
        assert "route_reason" in result


class TestSQLFlow:
    """Tests para el flujo SQL"""

    @patch("src.graphs.router_graph._sql_app")
    def test_sql_flow_node(self, mock_sql_app):
        """Verifica que sql_flow_node invoque el graph correcto"""
        from src.graphs.router_graph import sql_flow_node, GlobalState

        mock_sql_app.invoke.return_value = {
            "answer": "Total ventas: 100000",
            "sql_markdown": "| Ventas |\n| --- |\n| 100000 |",
        }

        state: GlobalState = {"question": "¿Total de ventas?"}
        result = sql_flow_node(state)

        assert "sql_answer" in result
        assert result["sql_answer"] == "Total ventas: 100000"


class TestDocsFlow:
    """Tests para el flujo de documentos"""

    @patch("src.graphs.router_graph._docs_app")
    def test_docs_flow_node(self, mock_docs_app):
        """Verifica que docs_flow_node invoque el graph correcto"""
        from src.graphs.router_graph import docs_flow_node, GlobalState

        mock_docs_app.invoke.return_value = {
            "answer": "Una región es una división geográfica...",
        }

        state: GlobalState = {"question": "¿Qué es una región?"}
        result = docs_flow_node(state)

        assert "docs_answer" in result
        assert "división geográfica" in result["docs_answer"]


class TestMasterGraph:
    """Tests para el master graph"""

    def test_global_state_type_definition(self):
        """Verifica que GlobalState esté correctamente definido"""
        from src.graphs.router_graph import GlobalState

        # GlobalState debe ser un TypedDict
        assert hasattr(GlobalState, "__annotations__")
        required_keys = ["question", "intent"]
        for key in required_keys:
            assert key in GlobalState.__annotations__
