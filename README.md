# dashboard
📊 Inteligencia de Precios - Cementos
Este proyecto es un dashboard interactivo diseñado para el monitoreo competitivo de precios en ferreterías. Utiliza una arquitectura en la nube para centralizar datos y visualizarlos en tiempo real.

🛠️ Tecnologías Utilizadas
Streamlit: Interfaz de usuario y visualización de datos.

Supabase: Base de datos relacional (PostgreSQL) para el almacenamiento en la nube.

Pandas: Procesamiento y limpieza de datos.

Python: Lenguaje principal de desarrollo.

📋 Funcionalidades
Filtros Dinámicos: Selección por ciudad y marca para análisis específico.

Análisis de KPIs: Cálculo automático del promedio del mercado, precio de Argos, promedio de la competencia y la diferencia (gap) de precios.

Visualizaciones: Gráficos de barras comparativos por marca y por ubicación geográfica.

Auditoría de Datos: Tabla de detalle expandible para revisar registros individuales de ferreterías.

⚙️ Configuración (Para Desarrolladores)
Para que este proyecto funcione localmente, es necesario configurar los secretos de Streamlit con las credenciales de Supabase:

SUPABASE_URL

SUPABASE_KEY

📈 Próximos Pasos
Carga masiva de datos para ciudades adicionales en Antioquia.

Implementación de alertas de desviación de precios mediante IA.
