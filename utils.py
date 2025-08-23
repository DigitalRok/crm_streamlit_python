# utils.py
import streamlit as st
from pathlib import Path

def add_sidebar_logo(path: str = "assets/logo_control360T.png"):
    """Muestra el logo en el sidebar (parte inferior)."""
    if Path(path).exists():
        st.sidebar.markdown("---")
        st.sidebar.image(path, use_container_width=True)
    else:
        # Evita romper la app si el archivo no está
        st.sidebar.markdown("---")
        st.sidebar.caption("⚠️ Logo no encontrado")

