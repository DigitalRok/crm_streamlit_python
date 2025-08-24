# pages/0_Inicio.py
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path

# 1) Configuración de la página SIEMPRE primero
st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# 2) Utilidades de UI (logo en sidebar)
from ui_helpers import sidebar_logo


# 3) CSS defensivo: ocultar logos de footer si quedaron de otros intentos/páginas
st.markdown(
    """
    <style>
      /* Clases típicas que usamos antes para el footer */
      .footer-logo, .content-footer-logo, .footer_logo_center { display: none !important; }

      /* Por si hubiera un contenedor fijo en bottom con un img adentro */
      div[style*="position: fixed"][style*="bottom"] img { display: none !important; }

      /* Empujar un poco hacia arriba el contenido si hiciera falta */
      .block-container { padding-bottom: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4) Contenido principal
st.title("🏠 Inicio")
st.write("Bienvenido al CRM de Ventas & Cobranzas")

st.markdown("---")
st.subheader("Accesos rápidos")

# 5) Navegación a otras páginas
col1, col2, col3 = st.columns(3)
if hasattr(st, "page_link"):
    with col1:
        st.page_link("pages/1_Ventas.py", label="🛒 Ventas")
    with col2:
        st.page_link("pages/2_Cobranzas.py", label="💳 Cobranzas")
    with col3:
        st.page_link("pages/3_Clientes.py", label="👤 Clientes")
        
else:
    with col1:
        st.markdown("👉 [🛒 **Ventas**](./Ventas)")
    with col2:
        st.markdown("👉 [💳 **Cobranzas**](./Cobranzas)")
    with col3:
        st.markdown("👉 [👤 **Clientes**](./Clientes)")

# 6) HERO LOGO centrado en el cuerpo (UN SOLO LOGO)
HERO_PATH = Path("assets/logo_control360T.png")
# Centrado con columnas (1-2-1)
l, c, r = st.columns([1, 2, 1])
with c:
    if HERO_PATH.exists():
        st.image(str(HERO_PATH), width=420)  # <- ajustá el ancho a gusto (420–560 suele verse bien)
    else:
        st.warning(f"⚠️ No encuentro el logo: {HERO_PATH.resolve()}")

# (Opcional) Métricas
# m1, m2, m3 = st.columns(3)
# with m1: st.metric("Ventas hoy", "12")
# with m2: st.metric("Cobranza hoy", "$350.000")
# with m3: st.metric("Clientes activos", "248")

