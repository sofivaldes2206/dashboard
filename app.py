import streamlit as st
import pandas as pd
from supabase import create_client

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo - Cementos", layout="wide")

st.title("📊 Inteligencia de Precios - Cementos")
st.caption("Monitoreo competitivo en ferreterías")

# -------------------------
# 🔗 CONEXIÓN SUPABASE
# -------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# 📥 TRAER DATOS
# -------------------------
try:
    res = supabase.table("Datos").select("*").execute()
    df = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# -------------------------
# VALIDACIÓN Y FORMATEO
# -------------------------
if df.empty:
    st.error("⚠️ La tabla 'Datos' está vacía o el RLS está bloqueando el acceso.")
    st.stop()

if "fecha" in df.columns:
    df["fecha"] = pd.to_datetime(df["fecha"])

# -------------------------
# FILTROS
# -------------------------
with st.sidebar:
    st.header("🎛️ Filtros")
    
    ciudades_disp = sorted(df["ciudad"].dropna().unique()) if "ciudad" in df.columns else []
    ciudad = st.multiselect("Ciudad", ciudades_disp)
    
    marcas_disp = sorted(df["marca"].dropna().unique()) if "marca" in df.columns else []
    marca = st.multiselect("Marca", marcas_disp)

if ciudad:
    df = df[df["ciudad"].isin(ciudad)]

if marca:
    df = df[df["marca"].isin(marca)]

# -------------------------
# KPIs
# -------------------------
if "precio" in df.columns:
    st.markdown("### 📌 Estado del mercado")
    col1, col2, col3, col4 = st.columns(4)

    precio_prom = df["precio"].mean()
    
    # Manejo de marca ARGOS (case insensitive)
    mask_argos = df["marca"].str.upper() == "ARGOS" if "marca" in df.columns else pd.Series([False]*len(df))
    argos = df[mask_argos]
    competencia = df[~mask_argos]

    col1.metric("Mercado", f"${int(precio_prom):,}")
    
    val_argos = argos['precio'].mean() if not argos.empty else 0
    col2.metric("ARGOS", f"${int(val_argos):,}" if val_argos > 0 else "Sin datos")
    
    val_comp = competencia['precio'].mean() if not competencia.empty else 0
    col3.metric("Competencia", f"${int(val_comp):,}" if val_comp > 0 else "Sin datos")

    if val_argos > 0 and val_comp > 0:
        diff = val_argos - val_comp
        col4.metric("Diferencia", f"${int(diff):,}")
        
        st.markdown("### 💡 Insight clave")
        if diff < 0:
            st.error("🔴 ARGOS está más barato que el mercado")
        elif diff > 0:
            st.success("🟢 ARGOS está por encima del mercado")
    else:
        col4.metric("Diferencia", "N/A")

# -------------------------
# GRÁFICOS
# -------------------------
col_left, col_right = st.columns(2)

with col_left:
    if "marca" in df.columns and "precio" in df.columns:
        st.markdown("### ⚖️ Promedio por Marca")
        st.bar_chart(df.groupby("marca")["precio"].mean())

with col_right:
    if "ciudad" in df.columns and "precio" in df.columns:
        st.markdown("### 🌍 Precios por Ciudad")
        st.bar_chart(df.groupby("ciudad")["precio"].mean())

# -------------------------
# TABLA DETALLE
# -------------------------
with st.expander("📋 Ver detalle de la tabla Datos"):
    st.dataframe(df)
