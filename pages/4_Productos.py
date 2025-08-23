# pages/4_Productos.py
import streamlit as st
from sqlalchemy import text
from db import get_engine
import pandas as pd

st.set_page_config(page_title="Productos", page_icon="📦", layout="wide")
eng = get_engine()

# ---- Ocultar la solapa raíz "app" del sidebar + Logo en el sidebar ----
st.markdown("""
    <style>
      [data-testid="stSidebarNav"] li:first-child { display: none !important; }
    </style>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.image("assets/logo_control360T.png", use_container_width=True)

# ---------- Helpers ----------
def to_float(v):
    """Convierte '1.234,56' o '1234,56' o '1234.56' a float (o None)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", "")
    # Si tiene coma y punto, quito separadores de miles y dejo punto decimal
    if "," in s and s.count(",") == 1 and s.count(".") >= 1:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def fmt_money(x):
    """Formatea con miles (.) y decimales (,) -> 1.234,56"""
    try:
        return f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"

def fmt_pct(x):
    """Formatea porcentaje 12,34%"""
    try:
        return f"{float(x):.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"

def chip_num(valor, small=False):
    """Devuelve HTML para mostrar un número dentro de un 'chip' verde."""
    if isinstance(valor, (int, float)):
        txt = fmt_money(valor)
    else:
        txt = str(valor)
    cls = "badge-num badge-sm" if small else "badge-num"
    return f'<span class="{cls}">{txt}</span>'

def fetch_products():
    with eng.connect() as c:
        rows = c.execute(text(
            """
            SELECT dispositivo_id, created_at, nombre,
                   COALESCE(marca,'') as marca,
                   COALESCE(modelo,'') as modelo,
                   COALESCE(color,'') as color,
                   COALESCE(descripcion,'') as descripcion,
                   COALESCE(precio_lista,0) as precio_lista,
                   COALESCE(precio_base,0) as precio_base,
                   COALESCE(costo,0) as costo,
                   COALESCE(stock,0) as stock,
                   COALESCE(descuento_pct,0) as descuento_pct
            FROM public.dispositivos
            ORDER BY dispositivo_id DESC
            """
        )).mappings().all()
    return rows

st.session_state.setdefault("edit_id", None)

# ---------- Estilos (chips + inputs + scroll) ----------
st.markdown("""
<style>
/* CHIPS NUMÉRICOS */
.badge-num {
  background: #0E3B2E;
  color: #E6FFE6;
  border-radius: 12px;
  padding: 6px 12px;
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 120px;               /* evita recortes */
  text-align: right;
  font-weight: 600;
  line-height: 1.1;
  font-variant-numeric: tabular-nums; /* cifras tabulares (monoespaciadas) */
  letter-spacing: .2px;
}
.badge-num.badge-sm {
  min-width: 72px;
  padding: 6px 10px;
}

/* Cabezal y textos suaves */
.pill {background:#113c2b; color:#e8fff3; border-radius:8px; padding:4px 8px; text-align:center; font-weight:600;}
.soft {color:#96a3ab; font-size:12px;}
.head {font-weight:700;}

/* Inputs: alineación a la derecha y sin recortes */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
  padding-right: 12px !important;
}

/* contenedor con scroll horizontal para la grilla */
.table-wrap { overflow-x: auto; }
</style>
""", unsafe_allow_html=True)

# ---------- Título principal de la página ----------
st.title("📦 Listado de productos")

# ---------- Alta producto (encima de la grilla) ----------
st.subheader("📑 Lista de productos")
with st.expander("➕ Agregar un producto", expanded=False):
    with st.form("nuevo_prod"):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            nombre = st.text_input("Nombre", "")
            marca = st.text_input("Marca", "")
        with c2:
            modelo = st.text_input("Modelo", "")
            color  = st.text_input("Color", "")
        with c3:
            precio_lista = st.text_input("Precio lista", "0,00")
            precio_base  = st.text_input("Precio base", "0,00")
        with c4:
            costo  = st.text_input("Costo", "0,00")
            stock  = st.number_input("Stock", 0, step=1)
        descuento_pct = st.text_input("Descuento (%)", "0,00")
        descripcion   = st.text_input("Descripción", "")
        ok = st.form_submit_button("Guardar / Actualizar")

    if ok:
        try:
            params = dict(
                nombre=nombre.strip(),
                marca=marca.strip() or None,
                modelo=modelo.strip() or None,
                color=color.strip() or None,
                descripcion=descripcion.strip() or None,
                pl=to_float(precio_lista) or 0.0,
                pb=to_float(precio_base) or 0.0,
                cs=to_float(costo) or 0.0,
                st=int(stock or 0),
                dp=to_float(descuento_pct) or 0.0,
            )
            with eng.begin() as c:
                c.execute(text("""
                    INSERT INTO public.dispositivos
                      (nombre, marca, modelo, color, descripcion,
                       precio_lista, precio_base, costo, stock, descuento_pct)
                    VALUES (:nombre, :marca, :modelo, :color, :descripcion,
                            :pl, :pb, :cs, :st, :dp)
                    ON CONFLICT (nombre) DO UPDATE SET
                        marca         = EXCLUDED.marca,
                        modelo        = EXCLUDED.modelo,
                        color         = EXCLUDED.color,
                        descripcion   = EXCLUDED.descripcion,
                        precio_lista  = EXCLUDED.precio_lista,
                        precio_base   = EXCLUDED.precio_base,
                        costo         = EXCLUDED.costo,
                        stock         = EXCLUDED.stock,
                        descuento_pct = EXCLUDED.descuento_pct
                """), params)
            st.success("Producto guardado/actualizado ✅")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------- Barra edición ----------
if st.session_state["edit_id"] is not None:
    eid = st.session_state["edit_id"]
    st.subheader("🛠️ Edición de productos")
    b1,b2 = st.columns([1,1])
    if b1.button("✅ Guardar cambios", type="primary"):
        k = lambda f: st.session_state.get(f"edit_{eid}_{f}")
        try:
            params = dict(
                id=eid,
                nombre=k("nombre") or "",
                marca=k("marca") or None,
                modelo=k("modelo") or None,
                color=k("color") or None,
                descripcion=k("descripcion") or None,
                pl=to_float(k("precio_lista")) or 0.0,
                pb=to_float(k("precio_base")) or 0.0,
                cs=to_float(k("costo")) or 0.0,
                st=int(k("stock") or 0),
                dp=to_float(k("descuento_pct")) or 0.0,
            )
            with eng.begin() as c:
                c.execute(text("""
                    UPDATE public.dispositivos SET
                      nombre=:nombre, marca=:marca, modelo=:modelo, color=:color, descripcion=:descripcion,
                      precio_lista=:pl, precio_base=:pb, costo=:cs, stock=:st, descuento_pct=:dp
                    WHERE dispositivo_id=:id
                """), params)
            st.success("Cambios guardados ✅")
            st.session_state["edit_id"] = None
        except Exception as e:
            st.error(f"Error: {e}")
    if b2.button("↩️ Cancelar edición"):
        st.session_state["edit_id"] = None

st.divider()

# ---------- Tabla productos ----------
rows = fetch_products()

# Cabecera para la grilla editable
st.subheader("🧾 Edición de productos")

# Definir estructura columnas fija (igual cabecera que filas)
structure = [0.6, 1.5, 1.3, 1.3, 1.0, 2.0, 1.2, 1.2, 1.2, 0.8, 1.0, 1.5, 0.5, 0.5]
labels = ["ID","Nombre","Marca","Modelo","Color","Descripción",
          "Precio lista","Precio base","Costo","Stock","Desc.%","Creado"," "," "]

# Contenedor con scroll horizontal
st.markdown('<div class="table-wrap">', unsafe_allow_html=True)

# Cabecera
hc = st.columns(structure)
for c,t in zip(hc,labels):
    c.markdown(f"<div class='head'>{t}</div>", unsafe_allow_html=True)

# Filas
for r in rows:
    rid = r["dispositivo_id"]
    created = pd.to_datetime(r["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
    editing = (st.session_state["edit_id"] == rid)

    cols = st.columns(structure)

    # ID
    cols[0].write(f"**{rid}**")

    if editing:
        cols[1].text_input(" ", r["nombre"], key=f"edit_{rid}_nombre", label_visibility="hidden")
        cols[2].text_input(" ", r["marca"], key=f"edit_{rid}_marca", label_visibility="hidden")
        cols[3].text_input(" ", r["modelo"], key=f"edit_{rid}_modelo", label_visibility="hidden")
        cols[4].text_input(" ", r["color"], key=f"edit_{rid}_color", label_visibility="hidden")
        cols[5].text_input(" ", r["descripcion"], key=f"edit_{rid}_descripcion", label_visibility="hidden")
        cols[6].text_input(" ", fmt_money(r["precio_lista"]), key=f"edit_{rid}_precio_lista", label_visibility="hidden")
        cols[7].text_input(" ", fmt_money(r["precio_base"]),  key=f"edit_{rid}_precio_base",  label_visibility="hidden")
        cols[8].text_input(" ", fmt_money(r["costo"]),        key=f"edit_{rid}_costo",        label_visibility="hidden")
        cols[9].number_input(" ", value=int(r["stock"]), step=1, key=f"edit_{rid}_stock", label_visibility="hidden")
        cols[10].text_input(" ", str(r["descuento_pct"]).replace(".",","), key=f"edit_{rid}_descuento_pct", label_visibility="hidden")
    else:
        cols[1].write(r["nombre"])
        cols[2].write(r["marca"])
        cols[3].write(r["modelo"])
        cols[4].write(r["color"])
        cols[5].write(r["descripcion"])
        cols[6].markdown(chip_num(r["precio_lista"]),  unsafe_allow_html=True)
        cols[7].markdown(chip_num(r["precio_base"]),   unsafe_allow_html=True)
        cols[8].markdown(chip_num(r["costo"]),         unsafe_allow_html=True)
        cols[9].markdown(chip_num(int(r["stock"]), small=True), unsafe_allow_html=True)
        cols[10].markdown(chip_num(str(fmt_pct(r["descuento_pct"]))[:-1], small=True), unsafe_allow_html=True)  # 10,00

    cols[11].markdown(f"<span class='soft'>{created}</span>", unsafe_allow_html=True)

    # Acciones
    if not editing:
        if cols[12].button("✏️", key=f"edit_{rid}"):
            st.session_state["edit_id"] = rid
        if cols[13].button("🗑️", key=f"del_{rid}"):
            with eng.begin() as c:
                c.execute(text("DELETE FROM public.dispositivos WHERE dispositivo_id=:i"), {"i":rid})
            st.success("Producto eliminado 🗑️")

# Cierre del contenedor con scroll
st.markdown('</div>', unsafe_allow_html=True)

