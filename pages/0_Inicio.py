# pages/0_Inicio.py
import streamlit as st
import os

st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# --- Logo en sidebar ---
logo_path = "assets/logo_control360T.png"  # asegurate que exista assets/control360.png

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo en assets/logo_control360T.png")

# --- Título ---
st.title("🏠 Inicio")
st.write("Bienvenido al CRM de Ventas & Cobranzas")

st.markdown("---")
st.subheader("Accesos rápidos")
col1, col2, col3 = st.columns(3)
col1.markdown("👉 🛒 **Ventas**")
col2.markdown("👉 💳 **Cobranzas**")
col3.markdown("👉 👤 **Clientes**")
