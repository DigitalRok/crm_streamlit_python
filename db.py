# db.py
import os
from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def _from_env_or_secrets():
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            import streamlit as st
            url = st.secrets["DATABASE_URL"]
        except Exception:
            url = None
    return url or "postgresql://postgres@localhost:5432/crm_celulares"

def _to_pg8000(url: str) -> str:
    # Normaliza esquema y driver → pg8000
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql+pg8000://" + url[len("postgresql+psycopg://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+pg8000://" + url[len("postgresql://"):]
    # Ajusta querystring: pg8000 usa ?ssl=true (no sslmode)
    p = urlparse(url)
    qs = dict(parse_qsl(p.query))
    qs.pop("sslmode", None)
    qs.setdefault("ssl", "true")
    url = urlunparse(p._replace(query=urlencode(qs)))
    return url

DATABASE_URL = _to_pg8000(_from_env_or_secrets())

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)
