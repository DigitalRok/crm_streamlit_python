import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost:5432/crm_celulares")

_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine

def query(sql: str, params: dict | None = None):
    eng = get_engine()
    with eng.connect() as conn:
        res = conn.execute(text(sql), params or {})
        try:
            rows = res.mappings().all()
            return rows
        except Exception:
            return []

def execute(sql: str, params: dict | None = None):
    eng = get_engine()
    with eng.begin() as conn:
        res = conn.execute(text(sql), params or {})
        return res.rowcount
