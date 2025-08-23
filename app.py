# app.py
import streamlit as st

# 1) Configuración general
st.set_page_config(page_title=" ", page_icon=None, layout="wide")

# 2) Ocultar la primera entrada del sidebar (la raíz "app")
st.markdown(
    """
    <style>
        /* Streamlit 1.48+ */
        nav[data-testid="stSidebarNav"] ul li:nth-of-type(1) { display: none !important; }
        /* Variantes para otras versiones */
        div[data-testid="stSidebarNav"] ul li:nth-of-type(1) { display: none !important; }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul li:nth-of-type(1) { display: none !important; }
        /* Ajuste de margen del listado del sidebar */
        [data-testid="stSidebarNav"] ul { margin-top: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3) Redirección inmediata a Inicio
#    Asegurate de que exista: pages/0_Inicio.py
try:
    st.switch_page("pages/0_Inicio.py")
except Exception:
    # Si la redirección falla durante una recarga, evitamos pantalla en blanco
    st.empty()



