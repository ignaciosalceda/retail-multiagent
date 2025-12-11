# src/data/db.py
from typing import Any, Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.config.settings import get_settings

_settings = get_settings()
_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        db_url = _settings.oracle_sqlalchemy_url
        _engine = create_engine(db_url, echo=False, future=True)
    return _engine


def run_query(sql: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """
    Ejecuta una query SQL (SELECT) contra Oracle y devuelve lista de dicts.
    """
    engine = get_engine()
    params = params or {}
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql), params)
            rows = result.mappings().all()
            return [dict(r) for r in rows]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Database error: {e}") from e
