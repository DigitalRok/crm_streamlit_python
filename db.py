import os
from sqlalchemy import create_engine

def _db_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            import streamlit as st
            url = st.secrets["DATABASE_URL"]
        except Exception:
            url = None
    url = url or "postgresql://postgres@localhost:5432/crm_celulares"
    # Fuerza el driver psycopg3 si viene como postgresql://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

DATABASE_URL = _db_url()

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)
