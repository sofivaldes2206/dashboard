import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURACIÓN DE PÁGINA 
st.set_page_config(page_title="Dashboard Ejecutivo - Cementos", layout="wide")

st.title("📊 Inteligencia de Precios - Cementos")
st.caption("Monitoreo competitivo en ferreterías")

# 2. CONEXIÓN A SUPABASE
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. EXTRACCIÓN Y LIMPIEZA DE DATOS
try:
    res = supabase.table("Datos").select("*").execute()
    df = pd.DataFrame(res.data)
    # Mapeo de tus columnas reales
    df["marca"] = df["marca_cemento1"]
    df["precio"] = pd.to_numeric(df["precio_cop1"], errors='coerce')
    df = df.dropna(subset=["marca", "precio"])
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# 4. BARRA LATERAL 
with st.sidebar:
    st.header("Filtros")
    ciudades_disp = sorted(df["ciudad"].dropna().unique())
    ciudad_sel = st.multiselect("Ciudad", ciudades_disp)
    
    marcas_disp = sorted(df["marca"].dropna().unique())
    marca_sel = st.multiselect("Marca", marcas_disp)

# Aplicar filtros
if ciudad_sel:
    df = df[df["ciudad"].isin(ciudad_sel)]
if marca_sel:
    df = df[df["marca"].isin(marca_sel)]

# 5. SECCIÓN DE MÉTRICAS (KPIs en 4 columnas)
st.markdown("### 📌 Estado del mercado")
col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    precio_prom = df["precio"].mean()
    mask_argos = df["marca"].str.contains("Argos", case=False, na=False)
    argos = df[mask_argos]
    competencia = df[~mask_argos]

    # Métrica 1: Promedio General
    col1.metric("Mercado", f"${int(precio_prom):,}")
    
    # Métrica 2: Promedio Argos
    val_argos = argos['precio'].mean() if not argos.empty else 0
    col2.metric("ARGOS", f"${int(val_argos):,}" if val_argos > 0 else "N/A")
    
    # Métrica 3: Promedio Competencia
    val_comp = competencia['precio'].mean() if not competencia.empty else 0
    col3.metric("Competencia", f"${int(val_comp):,}" if val_comp > 0 else "N/A")

    # Métrica 4: Diferencia
    if val_argos > 0 and val_comp > 0:
        diff = val_argos - val_comp
        col4.metric("Diferencia", f"${int(diff):,}", delta=int(diff), delta_color="inverse")
    else:
        col4.metric("Diferencia", "N/A")

st.divider() # Línea divisoria como en el playground

# 6. SECCIÓN DE GRÁFICOS (2 columnas)
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("### ⚖️ Promedio por Marca")
    if not df.empty:
        # Gráfico de barras simple de Streamlit
        chart_data_marca = df.groupby("marca")["precio"].mean()
        st.bar_chart(chart_data_marca, color="#0077b6")

with col_graf2:
    st.markdown("### 🌍 Precios por Ciudad")
    if not df.empty:
        chart_data_ciudad = df.groupby("ciudad")["precio"].mean()
        st.bar_chart(chart_data_ciudad, color="#00b4d8")

# 7. TABLA DE DETALLE (Al final, expandible)
with st.expander("📋 Ver detalle de la tabla"):
    st.write(df)
