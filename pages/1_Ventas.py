# pages/1_Ventas.py
import streamlit as st
from db import get_engine
from sqlalchemy import text
import pandas as pd
from utils import add_sidebar_logo   # 👈 importa el helper del logo

# ---------------- Configuración ----------------
st.set_page_config(page_title="Ventas", page_icon="🧾", layout="wide")

# 👇 logo en el **sidebar** (igual que en Inicio)
add_sidebar_logo()

# --- Título de la página ---
st.title("🧾 Ventas")

eng = get_engine()

# ------------------------ Helpers ------------------------
def _ensure_state_defaults():
    ss = st.session_state
    ss.setdefault("venta_cliente_id", None)
    ss.setdefault("venta_plan_id", None)
    ss.setdefault("venta_dispositivo_id", None)

    ss.setdefault("venta_precio", 0.0)
    ss.setdefault("venta_descuento", 0.0)
    ss.setdefault("venta_cant_cuotas", 12)
    ss.setdefault("venta_tasa_nominal", 50.000)
    ss.setdefault("venta_cft", 0.000)
    ss.setdefault("venta_adelanto", 0.0)
    ss.setdefault("venta_dia_venc", 10)

_ensure_state_defaults()

# ------------------- Cargar catálogos --------------------
clientes, dispositivos, planes = [], [], []
disp_map = {}

try:
    with eng.connect() as conn:
        rows = conn.execute(text("""
            SELECT cliente_id, nombre, dni
            FROM public.clientes
            ORDER BY cliente_id DESC
        """)).mappings().all()
    clientes = [(f"{r['nombre']} | DNI: {r['dni']}", r["cliente_id"]) for r in rows]
except Exception as e:
    st.error(f"Error cargando clientes: {e}")

try:
    with eng.connect() as conn:
        rows = conn.execute(text("""
            SELECT dispositivo_id, nombre, descripcion, precio_base, stock, descuento
            FROM public.dispositivos
            ORDER BY dispositivo_id DESC
        """)).mappings().all()
    for r in rows:
        disp_map[r["dispositivo_id"]] = r
    dispositivos = [
        (f"{r['nombre']} — ${r['precio_base']:.2f} | stock: {r['stock']}", r["dispositivo_id"])
        for r in rows
    ]
except Exception as e:
    st.error(f"Error cargando dispositivos: {e}")

try:
    with eng.connect() as conn:
        rows = conn.execute(text("""
            SELECT plan_id, nombre
            FROM public.planes
            ORDER BY plan_id
        """)).mappings().all()
    planes = [(f"{r['nombre']}", r["plan_id"]) for r in rows]
except Exception:
    planes = []   # si la tabla no existe o falla la consulta

# Avisos si faltan catálogos
if not dispositivos:
    st.warning("No hay dispositivos cargados todavía. Cargá productos en 📦 *Productos*.")
if not clientes:
    st.warning("No hay clientes cargados todavía. Cargá clientes en 👤 *Clientes*.")

# Si no hay planes, detenemos (plan_id es NOT NULL en ventas)
if not planes:
    st.error("No hay planes configurados. Creá al menos uno en la tabla public.planes.")
    st.stop()

st.markdown("### Seleccionar datos base")

colA, colB = st.columns(2)
with colA:
    cliente_lbls = [c[0] for c in clientes] if clientes else ["—"]
    if clientes:
        idx_cli = 0
        if st.session_state["venta_cliente_id"] is not None:
            for i, (_, cid) in enumerate(clientes):
                if cid == st.session_state["venta_cliente_id"]:
                    idx_cli = i
                    break
        cli_sel = st.selectbox("Cliente", cliente_lbls, index=idx_cli, key="venta_cliente_sel")
        st.session_state["venta_cliente_id"] = clientes[cliente_lbls.index(cli_sel)][1]
    else:
        st.selectbox("Cliente", cliente_lbls, disabled=True)

with colB:
    disp_lbls = [d[0] for d in dispositivos] if dispositivos else ["—"]
    if dispositivos:
        idx_dis = 0
        if st.session_state["venta_dispositivo_id"] is not None:
            for i, (_, did) in enumerate(dispositivos):
                if did == st.session_state["venta_dispositivo_id"]:
                    idx_dis = i
                    break
        disp_sel = st.selectbox("Dispositivo", disp_lbls, index=idx_dis, key="venta_disp_sel")
        disp_id = dispositivos[disp_lbls.index(disp_sel)][1]
        if disp_id != st.session_state["venta_dispositivo_id"]:
            st.session_state["venta_dispositivo_id"] = disp_id
            fila = disp_map.get(disp_id)
            if fila:
                st.session_state["venta_precio"] = float(fila["precio_base"] or 0.0)
                st.session_state["venta_descuento"] = float(fila["descuento"] or 0.0)
    else:
        st.selectbox("Dispositivo", disp_lbls, disabled=True)

# Plan (obligatorio)
plan_lbls = [p[0] for p in planes]
idx_plan = 0
if st.session_state["venta_plan_id"] is not None:
    for i, (_, pid) in enumerate(planes):
        if pid == st.session_state["venta_plan_id"]:
            idx_plan = i
            break
plan_sel = st.selectbox("Plan", plan_lbls, index=idx_plan, key="venta_plan_sel")
st.session_state["venta_plan_id"] = planes[plan_lbls.index(plan_sel)][1]

st.markdown("---")

# ---------------- Formulario de la venta ----------------
with st.form("form_venta"):
    st.subheader("Completar condiciones de la venta")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        precio_venta = st.number_input(
            "Precio venta", min_value=0.0, step=100.0, format="%.2f",
            value=float(st.session_state["venta_precio"]), key="venta_precio_input",
        )
        st.session_state["venta_precio"] = precio_venta

    with c2:
        adelanto = st.number_input(
            "Adelanto", min_value=0.0, step=100.0, format="%.2f",
            value=float(st.session_state["venta_adelanto"]), key="venta_adelanto_input",
        )
        st.session_state["venta_adelanto"] = adelanto

    with c3:
        tasa_nominal = st.number_input(
            "Tasa nominal (%)", min_value=0.0, step=0.1, format="%.3f",
            value=float(st.session_state["venta_tasa_nominal"]), key="venta_tasa_input",
        )
        st.session_state["venta_tasa_nominal"] = tasa_nominal

    with c4:
        descuento = st.number_input(
            "Descuento (%)", min_value=0.0, step=0.5, format="%.2f",
            value=float(st.session_state["venta_descuento"]),
            help="Autocompletado desde el producto, podés editarlo.",
            key="venta_descuento_input",
        )
        st.session_state["venta_descuento"] = descuento

    c5, c6, c7 = st.columns(3)
    with c5:
        cant_cuotas = st.number_input(
            "Cant. cuotas", min_value=1, step=1,
            value=int(st.session_state["venta_cant_cuotas"]), key="venta_cuotas_input",
        )
        st.session_state["venta_cant_cuotas"] = cant_cuotas

    with c6:
        cft = st.number_input(
            "CFT (%)", min_value=0.0, step=0.1, format="%.3f",
            value=float(st.session_state["venta_cft"]), key="venta_cft_input",
        )
        st.session_state["venta_cft"] = cft

    with c7:
        dia_venc = st.number_input(
            "Día de venc.", min_value=1, max_value=28, step=1,
            value=int(st.session_state["venta_dia_venc"]), key="venta_dia_venc_input",
        )
        st.session_state["venta_dia_venc"] = dia_venc

    submitted = st.form_submit_button("Crear venta y generar cuotas")

# -------------- Crear la venta al enviar ----------------
if submitted:
    if not st.session_state["venta_cliente_id"]:
        st.error("Seleccioná un cliente.")
    elif not st.session_state["venta_dispositivo_id"]:
        st.error("Seleccioná un dispositivo.")
    elif st.session_state["venta_plan_id"] is None:
        st.error("Seleccioná un plan.")
    else:
        try:
            with eng.begin() as conn:
                venta_id = conn.execute(
                    text("""
                        INSERT INTO public.ventas
                        (cliente_id, dispositivo_id, precio_venta, adelanto, plan_id,
                         cant_cuotas, tasa_nominal, cft, dia_venc)
                        VALUES (:cli, :disp, :precio, :adelanto, :plan, :cuotas, :tasa, :cft, :dia)
                        RETURNING venta_id
                    """),
                    dict(
                        cli=int(st.session_state["venta_cliente_id"]),
                        disp=int(st.session_state["venta_dispositivo_id"]),
                        precio=float(st.session_state["venta_precio"]),
                        adelanto=float(st.session_state["venta_adelanto"]),
                        plan=int(st.session_state["venta_plan_id"]),  # ← nunca None
                        cuotas=int(st.session_state["venta_cant_cuotas"]),
                        tasa=float(st.session_state["venta_tasa_nominal"]),
                        cft=float(st.session_state["venta_cft"]),
                        dia=int(st.session_state["venta_dia_venc"]),
                    )
                ).scalar_one()

                conn.execute(text("SELECT public.gen_calendario_cuotas(:vid)"), dict(vid=int(venta_id)))
                conn.execute(
                    text("""
                        UPDATE public.dispositivos
                        SET stock = CASE WHEN stock > 0 THEN stock - 1 ELSE 0 END
                        WHERE dispositivo_id = :disp
                    """),
                    dict(disp=int(st.session_state["venta_dispositivo_id"]))
                )

            st.success(f"✅ Venta {venta_id} creada, cuotas generadas y stock actualizado.")
        except Exception as e:
            st.error(f"Error creando venta: {e}")

st.markdown("---")

# ------------------- Últimas ventas ---------------------
st.subheader("Últimas ventas")
try:
    with eng.connect() as conn:
        rows = conn.execute(text("""
            SELECT v.venta_id, v.fecha_venta, v.cliente_id, v.dispositivo_id,
                   v.precio_venta, v.cant_cuotas
            FROM public.ventas v
            ORDER BY v.venta_id DESC
            LIMIT 50
        """)).mappings().all()
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No hay ventas aún.")
except Exception as e:
    st.error(f"Error listando ventas: {e}")



