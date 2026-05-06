import streamlit as st
import pandas as pd
from supabase import create_client

# -------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo - Cementos", layout="wide")

st.title("📊 Inteligencia de Precios - Cementos")
st.caption("Monitoreo competitivo en ferreterías")

# -------------------------
# CONEXIÓN A SUPABASE
# -------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# EXTRACCIÓN DE DATOS
# -------------------------
try:
    res = supabase.table("Datos").select("*").execute()
    df = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# -------------------------
# VALIDACIÓN Y LIMPIEZA
# -------------------------
if df.empty:
    st.error("⚠️ La tabla 'Datos' está vacía.")
    st.stop()

# Mapeo de columnas según la estructura de la base de datos
df["marca"] = df["marca_cemento1"]
df["precio"] = pd.to_numeric(df["precio_cop1"], errors='coerce')

if "fecha" in df.columns:
    df["fecha"] = pd.to_datetime(df["fecha"])

# Eliminar registros sin información crítica
df = df.dropna(subset=["marca", "precio"])

# -------------------------
# PANEL DE FILTROS (SIDEBAR)
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
# INDICADORES CLAVE (KPIs)
# -------------------------
st.markdown("### 📌 Estado del mercado")
col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    precio_prom = df["precio"].mean()
    
    # Análisis específico para Argos frente a competencia
    mask_argos = df["marca"].str.contains("Argos", case=False, na=False)
    argos = df[mask_argos]
    competencia = df[~mask_argos]

    col1.metric("Mercado", f"${int(precio_prom):,}")
    
    val_argos = argos['precio'].mean() if not argos.empty else 0
    col2.metric("ARGOS", f"${int(val_argos):,}" if val_argos > 0 else "N/A")
    
    val_comp = competencia['precio'].mean() if not competencia.empty else 0
    col3.metric("Competencia", f"${int(val_comp):,}" if val_comp > 0 else "N/A")

    if val_argos > 0 and val_comp > 0:
        diff = val_argos - val_comp
        col4.metric("Diferencia", f"${int(diff):,}")
    else:
        col4.metric("Diferencia", "N/A")

# -------------------------
# SECCIÓN DE GRÁFICOS
# -------------------------
col_left, col_right = st.columns(2)

if not df.empty:
    with col_left:
        st.markdown("### ⚖️ Promedio por Marca")
        st.bar_chart(df.groupby("marca")["precio"].mean())

    with col_right:
        if "ciudad" in df.columns:
            st.markdown("### 🌍 Precios por Ciudad")
            st.bar_chart(df.groupby("ciudad")["precio"].mean())

# -------------------------
# DETALLE DE TABLA
# -------------------------
with st.expander("📋 Ver detalle de la tabla Datos"):
    st.dataframe(df)
