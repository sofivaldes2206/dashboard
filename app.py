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
clientes = supabase.table("clientes").select("*").execute().data
precios = supabase.table("precios").select("*").execute().data

clientes = pd.DataFrame(clientes)
precios = pd.DataFrame(precios)

# 🔍 DEBUG (puedes borrar luego)
st.write("Clientes:", clientes.head())
st.write("Precios:", precios.head())

# -------------------------
# VALIDACIÓN
# -------------------------
if clientes.empty or precios.empty:
    st.error("⚠️ No hay datos. Revisa Supabase (RLS o tablas vacías)")
    st.stop()

# -------------------------
# UNIÓN
# -------------------------
df = precios.merge(clientes, left_on="cliente_id", right_on="id")

# -------------------------
# FILTROS
# -------------------------
with st.sidebar:
    st.header("🎛️ Filtros")
    ciudad = st.multiselect("Ciudad", sorted(df["ciudad"].dropna().unique()))
    marca = st.multiselect("Marca", sorted(df["marca"].dropna().unique()))

if ciudad:
    df = df[df["ciudad"].isin(ciudad)]

if marca:
    df = df[df["marca"].isin(marca)]

# -------------------------
# KPIs
# -------------------------
st.markdown("### 📌 Estado del mercado")

col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    precio_prom = df["precio"].mean()
    argos = df[df["marca"] == "ARGOS"]
    competencia = df[df["marca"] != "ARGOS"]

    col1.metric("Mercado", f"${int(precio_prom):,}")
    col2.metric("ARGOS", f"${int(argos['precio'].mean()):,}" if not argos.empty else "Sin datos")
    col3.metric("Competencia", f"${int(competencia['precio'].mean()):,}" if not competencia.empty else "Sin datos")

    if not argos.empty and not competencia.empty:
        diff = argos["precio"].mean() - competencia["precio"].mean()
        col4.metric("Diferencia", f"${int(diff):,}")
    else:
        col4.metric("Diferencia", "N/A")

# -------------------------
# INSIGHT
# -------------------------
st.markdown("### 💡 Insight clave")

if not df.empty and not argos.empty and not competencia.empty:
    if diff < 0:
        st.error("🔴 ARGOS está más barato que el mercado → posible pérdida de margen")
    elif diff > 0:
        st.success("🟢 ARGOS está por encima del mercado → oportunidad de rentabilidad")
    else:
        st.info("🟡 ARGOS alineado al mercado")
else:
    st.info("No hay suficientes datos")

# -------------------------
# GRÁFICOS
# -------------------------
st.markdown("### ⚖️ Comparación por marca")
st.bar_chart(df.groupby("marca")["precio"].mean())

st.markdown("### 🌍 Precios por ciudad")
st.bar_chart(df.groupby("ciudad")["precio"].mean())

# -------------------------
# TENDENCIA
# -------------------------
st.markdown("### 📈 Tendencia")

df["fecha"] = pd.to_datetime(df["fecha"])
st.line_chart(df.set_index("fecha")["precio"])

# -------------------------
# RANKING
# -------------------------
st.markdown("### 🏆 Ranking de marcas")
ranking = df.groupby("marca")["precio"].mean().sort_values()
st.dataframe(ranking)

# -------------------------
# TABLA
# -------------------------
with st.expander("📋 Ver detalle"):
    st.dataframe(df)
