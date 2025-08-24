# utils.py
from pathlib import Path
import streamlit as st

def add_sidebar_logo():
    """
    Intenta mostrar un logo en el sidebar.
    Si no existe o hay error, NO rompe la app (muestra un texto).
    """
    try:
        base = Path(__file__).resolve().parent
        candidates = [
            base / "assets" / "logo.png",
            base / "logo.png",
            base.parent / "assets" / "logo.png",
            Path("assets/logo.png"),
            Path("logo.png"),
        ]
        for p in candidates:
            if p.exists():
                st.sidebar.image(str(p), use_container_width=True)
                return
    except Exception:
        pass

    # Fallback seguro
    st.sidebar.markdown("### Control 360°")

