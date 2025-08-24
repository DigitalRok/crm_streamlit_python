# ui_helpers.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st


# ------------------------------------------------------------------------------
# 1) Logo fijo en el sidebar (pie de barra lateral)
# ------------------------------------------------------------------------------
def sidebar_logo(path: str = "assets/logo_control360.png", height: int = 90) -> None:
    """
    Inserta un logo fijo en la parte inferior del sidebar.
    Si no encuentra el archivo, muestra un mensaje en el sidebar.
    """
    p = Path(path)
    if not p.exists():
        st.sidebar.error(f"No encuentro el logo en: {p.resolve()}")
        return

    try:
        b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    except Exception as e:
        st.sidebar.error(f"No pude leer el logo ({p}): {e}")
        return

    html = """
    <style>
    .sidebar-logo {
        position: fixed;
        bottom: 16px;
        left: 12px;
        right: 12px;
        text-align: center;
        z-index: 9999;
    }
    .sidebar-logo img {
        max-width: 85%;
        height: __HEIGHT__px;
        object-fit: contain;
        opacity: 0.95;
    }
    </style>
    <div class="sidebar-logo">
        <img src="data:image/png;base64,__B64__" />
    </div>
    """
    html = html.replace("__HEIGHT__", str(height)).replace("__B64__", b64)
    st.sidebar.markdown(html, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 2) Logo centrado en el pie del contenido principal (ajustable)
#    Esta versión NO usa f-string en el CSS (no hay que escapar llaves).
# ------------------------------------------------------------------------------
def footer_logo_center(
    path: str = "assets/logo_control360.png",
    width_px: int = 220,
    bottom_px: int = 24,
    opacity: float = 1.0,
) -> None:
    p = Path(path)
    if not p.exists():
        st.warning(f"No encuentro el logo del pie en: {p.resolve()}")
        return

    try:
        b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    except Exception as e:
        st.warning(f"No pude leer el logo del pie ({p}): {e}")
        return

    css_html = """
    <style>
    .footer-logo-center {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        bottom: __BOTTOM__px;
        z-index: 999;
        opacity: __OPACITY__;
        pointer-events: none;
    }
    .footer-logo-center img {
        width: __WIDTH__px;
        height: auto;
        filter: drop-shadow(0 1px 1px rgba(0,0,0,0.25));
    }
    </style>
    <div class="footer-logo-center">
        <img src="data:image/png;base64,__B64__" alt="Control 360" />
    </div>
    """
    css_html = (
        css_html.replace("__BOTTOM__", str(bottom_px))
        .replace("__OPACITY__", str(opacity))
        .replace("__WIDTH__", str(width_px))
        .replace("__B64__", b64)
    )
    st.markdown(css_html, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 3) Helpers para selección de plan (Ventas) – lo que ya tenías, intacto
# ------------------------------------------------------------------------------
def ensure_plan_state_defaults() -> None:
    st.session_state.setdefault("plan_id", None)
    st.session_state.setdefault("cant_cuotas", None)
    st.session_state.setdefault("tasa_nominal", None)
    st.session_state.setdefault("cft", 0.0)
    st.session_state.setdefault("dia_venc", 10)


def elegir_plan(plan_id: int, cuotas: int, tasa: float, cft: float, dia: int) -> None:
    st.session_state["plan_id"] = int(plan_id)
    st.session_state["cant_cuotas"] = int(cuotas)
    st.session_state["tasa_nominal"] = float(tasa)
    st.session_state["cft"] = float(cft)
    st.session_state["dia_venc"] = int(dia)


def reset_plan() -> None:
    for k in ("plan_id", "cant_cuotas", "tasa_nominal", "cft", "dia_venc"):
        if k in st.session_state:
            del st.session_state[k]

