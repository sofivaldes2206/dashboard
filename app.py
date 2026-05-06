import streamlit as st
import pandas as pd
from supabase import create_client

# -------------------------
# CONFIGURACIÓN
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo - Cementos", layout="wide")

st.title("📊 Inteligencia de Precios - Cementos")
st.caption("Monitoreo competitivo en ferreterías")

# -------------------------
# CONEXIÓN
# -------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# TRAER Y LIMPIAR DATOS
# -------------------------
try:
    res = supabase.table("Datos").select("*").execute()
    df_raw = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

if df_raw.empty:
    st.error("⚠️ La tabla 'Datos' está vacía.")
    st.stop()

# Mapeo y limpieza inicial
df_raw["marca"] = df_raw["marca_cemento1"]
df_raw["precio"] = pd.to_numeric(df_raw["precio_cop1"], errors='coerce')
# IMPORTANTE: Solo trabajamos con filas que tengan precio y marca para los KPIs
df = df_raw.dropna(subset=["marca", "precio"]).copy()

# -------------------------
# FILTROS (SIDEBAR)
# -------------------------
with st.sidebar:
    st.header("🎛️ Filtros")
    
    # Extraemos opciones únicas de lo que sí tiene datos
    ciudades_disp = sorted(df["ciudad"].unique()) if "ciudad" in df.columns else []
    ciudad_sel = st.multiselect("Ciudad", ciudades_disp)
    
    marcas_disp = sorted(df["marca"].unique())
    marca_sel = st.multiselect("Marca", marcas_disp)

# Aplicar filtros
if ciudad_sel:
    df = df[df["ciudad"].isin(ciudad_sel)]
if marca_sel:
    df = df[df["marca"].isin(marca_sel)]

# -------------------------
# VISUALIZACIÓN
# -------------------------
if df.empty:
    st.warning("🔎 No hay datos que coincidan con estos filtros. Intenta con otra combinación.")
else:
    # KPIs
    st.markdown("### 📌 Estado del mercado")
    col1, col2, col3, col4 = st.columns(4)
    
    precio_prom = df["precio"].mean()
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
        col4.metric("Diferencia", f"${int(diff):,}", delta=int(diff), delta_color="inverse")
    else:
        col4.metric("Diferencia", "N/A")

    # Gráficos
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### ⚖️ Promedio por Marca")
        st.bar_chart(df.groupby("marca")["precio"].mean())
    with col_right:
        st.markdown("### 🌍 Precios por Ciudad")
        st.bar_chart(df.groupby("ciudad")["precio"].mean())

# Detalle siempre visible al final
with st.expander("📋 Ver detalle de la tabla"):
    st.dataframe(df)
