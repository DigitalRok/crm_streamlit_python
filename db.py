# db.py
import os
from sqlalchemy import create_engine

# Intenta leer de variable de entorno; si no, de Streamlit secrets; si no, localhost
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st  # disponible en Streamlit Cloud
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except Exception:
        DATABASE_URL = None

DATABASE_URL = DATABASE_URL or "postgresql://postgres@localhost:5432/crm_celulares"

def get_engine():
    # sslmode lo toma de la URL (?sslmode=require)
    return create_engine(DATABASE_URL, pool_pre_ping=True)
