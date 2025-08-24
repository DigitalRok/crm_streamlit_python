import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except Exception:
        DATABASE_URL = None

DATABASE_URL = DATABASE_URL or "postgresql://postgres@localhost:5432/crm_celulares"

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)
