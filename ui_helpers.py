# ---- Pegar al comienzo de pages/0_Inicio.py (y repetir en otras páginas) ----
import streamlit as st
from pathlib import Path
import base64

def sidebar_logo(path: str = "assets/control360.png", height: int = 90):
    p = Path(path)
    if not p.exists():
        # Mensaje claro si la imagen no se encuentra
        st.sidebar.error(f"No encuentro el logo en: {p.resolve()}")
        return

    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    st.sidebar.markdown(
        f"""
        <style>
        .sidebar-logo {{
            position: fixed;
            bottom: 16px;
            left: 12px;
            right: 12px;
            text-align: center;
            z-index: 9999;
        }}
        .sidebar-logo img {{
            max-width: 85%;
            height: {height}px;
            object-fit: contain;
            opacity: 0.95;
        }}
        </style>
        <div class="sidebar-logo">
            <img src="data:image/png;base64,{b64}" />
        </div>
        """,
        unsafe_allow_html=True,
    )

# Llamá SIEMPRE al comienzo de cada página:
sidebar_logo("assets/logo_control360.png", height=90)
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# ... el resto de tu página Inicio ...

