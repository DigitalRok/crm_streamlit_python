# pages/3_Clientes.py
import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db import get_engine

# ------------------ Config ------------------
st.set_page_config(page_title="Clientes", page_icon="👥", layout="wide")

# 🔒 Ocultar la solapa raíz "app" del sidebar
st.markdown("""
    <style>
      [data-testid="stSidebarNav"] li:first-child { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ✅ Logo en el sidebar (como en Ventas / Cobranzas)
st.sidebar.markdown("---")
st.sidebar.image("assets/logo_control360T.png", use_container_width=True)

st.title("👥 Clientes")

eng = get_engine()

# ------------------ Alta de cliente ------------------
with st.form("nuevo_cliente", clear_on_submit=True):
    st.subheader("Crear cliente")

    c1, c2, c3 = st.columns(3)
    with c1:
        dni = st.text_input("DNI *", value="").strip()
        nombre = st.text_input("Nombre *", value="").strip()
        apellido = st.text_input("Apellido *", value="").strip()
    with c2:
        tel_whatsapp = st.text_input("Tel. WhatsApp (+549...)", value="").strip()
        telefono = st.text_input("Teléfono alternativo", value="").strip()
        email = st.text_input("Email", value="").strip()
    with c3:
        ciudad = st.text_input("Ciudad", value="").strip()
        direccion = st.text_input("Dirección", value="").strip()

    btn_guardar = st.form_submit_button("Guardar")

    if btn_guardar:
        # Validaciones mínimas
        errores = []
        if not dni:
            errores.append("El DNI es obligatorio.")
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not apellido:
            errores.append("El apellido es obligatorio.")

        if errores:
            for e in errores:
                st.error(e)
        else:
            try:
                with eng.begin() as conn:
                    cliente_id = conn.execute(
                        text("""
                            insert into public.clientes
                                (dni, nombre, apellido, tel_whatsapp, telefono, email, ciudad, direccion)
                            values
                                (:dni, :nombre, :apellido, :tel_whatsapp, :telefono, :email, :ciudad, :direccion)
                            returning cliente_id
                        """),
                        dict(
                            dni=dni,
                            nombre=nombre,
                            apellido=apellido,
                            tel_whatsapp=tel_whatsapp or None,
                            telefono=telefono or None,
                            email=email or None,
                            ciudad=ciudad or None,
                            direccion=direccion or None,
                        )
                    ).scalar_one()
                st.success(f"Cliente creado (ID: {cliente_id}).")
            except IntegrityError as ie:
                # Clave duplicada (pgcode 23505): DNI o Email ya existe (según constraint)
                if hasattr(ie.orig, "pgcode") and ie.orig.pgcode == "23505":
                    st.error("DNI o Email ya existe en el sistema.")
                else:
                    st.error(f"Error de integridad: {ie}")
            except Exception as e:
                st.error(f"Error creando cliente: {e}")

st.markdown("---")

# ------------------ Listado / Búsqueda ------------------
st.subheader("Listado de clientes")
fcol1, fcol2 = st.columns([2, 1])
with fcol1:
    q = st.text_input("Buscar (nombre, apellido, DNI, email, whatsapp):", value="").strip()
with fcol2:
    limite = st.selectbox("Limite", [50, 100, 200, 500], index=2)  # default 200

try:
    if q:
        # Búsqueda server-side (ILIKE)
        qlike = f"%{q}%"
        sql = """
            select cliente_id, dni, nombre, apellido, tel_whatsapp, telefono, email, ciudad
            from public.clientes
            where (dni ilike :q or nombre ilike :q or apellido ilike :q or email ilike :q or tel_whatsapp ilike :q)
            order by cliente_id desc
            limit :lim
        """
        params = dict(q=qlike, lim=int(limite))
    else:
        sql = """
            select cliente_id, dni, nombre, apellido, tel_whatsapp, telefono, email, ciudad
            from public.clientes
            order by cliente_id desc
            limit :lim
        """
        params = dict(lim=int(limite))

    with eng.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay clientes para mostrar.")
except Exception as e:
    st.error(f"Error listando clientes: {e}")

