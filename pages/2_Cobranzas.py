# pages/2_Cobranzas.py
import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import date
from db import get_engine

# -------------------------------------------------
# Config
# -------------------------------------------------
st.set_page_config(page_title="Cobranzas", page_icon="💳", layout="wide")

# 🔒 Ocultar la solapa raíz "app" del menú lateral (por si aparece)
st.markdown("""
    <style>
      [data-testid="stSidebarNav"] li:first-child { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ✅ Logo en el sidebar (como en Ventas)
st.sidebar.markdown("---")
st.sidebar.image("assets/logo_control360T.png", use_container_width=True)

# Título
st.title("💳 Cobranzas")

eng = get_engine()

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def cuotas_pendientes_pairs():
    """
    Devuelve una lista de tuplas (label, cuota_id) para cuotas con saldo pendiente.
    Si hay algún problema, devuelve [].
    """
    try:
        with eng.connect() as conn:
            rows = conn.execute(text("""
                select c.cuota_id,
                       c.venta_id,
                       c.nro_cuota,
                       c.fecha_venc,
                       c.importe_cuota,
                       c.monto_pendiente,
                       coalesce(c.estado_cuota,'Pendiente') as estado
                from public.calendario_pagos c
                where (c.monto_pendiente is null or c.monto_pendiente > 0)
                order by c.fecha_venc asc, c.venta_id asc, c.nro_cuota asc
                limit 500
            """)).mappings().all()

        # (label, value) -> label visible, value usable
        return [
            (
                f"Cuota {r['nro_cuota']} — Venta {r['venta_id']} | "
                f"Vence {r['fecha_venc']} | Pendiente {r['monto_pendiente']}",
                int(r["cuota_id"])
            )
            for r in rows
        ]
    except Exception:
        return []

# -------------------------------------------------
# Bandeja de vencidas / vencen hoy / pendientes / todas
# -------------------------------------------------
st.subheader("Bandeja de cuotas")

colf1, colf2, colf3 = st.columns([1, 1, 1])
with colf1:
    filtro = st.selectbox(
        "Filtrar por",
        ["Vencen hoy", "Vencidas", "Pendientes", "Todas"],
        index=0
    )
with colf2:
    ordenar_por = st.selectbox(
        "Ordenar por",
        ["fecha_venc", "venta_id", "nro_cuota"],
        index=0
    )
with colf3:
    asc_desc = st.selectbox("Orden", ["asc", "desc"], index=0)

try:
    where_sql = ""
    params = {}

    if filtro == "Vencen hoy":
        params["today"] = date.today().isoformat()
        where_sql = "where fecha_venc = :today"
    elif filtro == "Vencidas":
        where_sql = "where estado_cuota = 'Vencida'"
    elif filtro == "Pendientes":
        where_sql = "where coalesce(monto_pendiente, importe_cuota) > 0"
    else:
        where_sql = ""  # Todas

    sql = f"""
        select cuota_id, venta_id, nro_cuota, fecha_venc, importe_cuota, 
               coalesce(estado_cuota,'Pendiente') as estado_cuota, 
               coalesce(dias_atraso,0) as dias_atraso, 
               coalesce(monto_pendiente, importe_cuota) as monto_pendiente
        from public.calendario_pagos
        {where_sql}
        order by {ordenar_por} {asc_desc}, nro_cuota asc
        limit 500
    """

    with eng.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay cuotas para el filtro seleccionado.")
except Exception as e:
    st.error(f"Error cargando bandeja: {e}")

st.markdown("---")

# -------------------------------------------------
# Registrar pago
# -------------------------------------------------
st.subheader("Registrar pago")

with st.form("registrar_pago", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    # Select de cuotas pendientes (label, value)
    pendientes = cuotas_pendientes_pairs()

    with col1:
        if pendientes:
            # selectbox con tuplas (label, value).
            sel = st.selectbox(
                "Cuota pendiente",
                pendientes,
                format_func=lambda x: x[0] if isinstance(x, tuple) else str(x)
            )
            cuota_id = sel[1] if isinstance(sel, tuple) else None
        else:
            cuota_id = st.number_input("Cuota ID", min_value=1, step=1)

        importe = st.number_input("Importe", min_value=0.0, step=1000.0, format="%.2f")

    with col2:
        metodo = st.text_input("Método (Transferencia / Efectivo / MP)", value="Transferencia")
        comp = st.text_input("Comprobante", value="")

    with col3:
        obs = st.text_input("Observación", value="")

    btn = st.form_submit_button("Aplicar pago")

    if btn:
        if not cuota_id:
            st.error("Debés seleccionar/ingresar una cuota.")
        elif importe <= 0:
            st.error("El importe debe ser mayor a 0.")
        else:
            try:
                with eng.begin() as conn:
                    result = conn.execute(
                        text("select * from public.registrar_pago(:cid, :imp, :met, :comp, :obs)"),
                        dict(cid=int(cuota_id), imp=float(importe), met=metodo, comp=comp, obs=obs)
                    ).mappings().all()
                st.success(f"Pago registrado. Resultado: {result[0] if result else 'OK'}")
            except Exception as e:
                st.error(f"Error registrando pago: {e}")

st.markdown("---")

# -------------------------------------------------
# Actualizar mora
# -------------------------------------------------
st.subheader("Actualizar mora manualmente")
st.caption("Calcula/actualiza la mora para cuotas vencidas. Útil si el job automático no corrió aún.")
if st.button("Actualizar mora ahora"):
    try:
        with eng.begin() as conn:
            conn.execute(text("select public.update_mora();"))
        st.success("Mora actualizada correctamente.")
    except Exception as e:
        st.error(f"Error actualizando mora: {e}")
