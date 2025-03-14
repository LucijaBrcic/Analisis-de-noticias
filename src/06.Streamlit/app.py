import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
import sys

load_dotenv()
user = os.getenv("user")
sys.path.append(f"/Users/{user}/Analisis-de-noticias/src")

from utils.nuevo_scraper import MeneameScraper


#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"
#----------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

st.title(page_title + " " + page_icon)

scraper = MeneameScraper()

# Display last scraped date
last_scraped = scraper.get_last_scraped_date()
if last_scraped:
    st.write(f"🕒 Última fecha de actualización: **{last_scraped}**")
else:
    st.write("⚠️ No hay datos anteriores. Haz clic en 'Actualizar' para comenzar.")

# Button to trigger scraping
if st.button("🔄 Actualizar Datos"):
    with st.spinner("Obteniendo nuevas noticias..."):
        result = scraper.scrape()

    updated_last_scraped = scraper.get_last_scraped_date()
    st.success(f"✅ {result} Última fecha de actualización: **{updated_last_scraped}**")



# Introduction
st.markdown(
    """
    Esta aplicación te permitirá explorar y analizar noticias de [Menéame](https://www.meneame.net/) de una forma interactiva e intuitiva.  
    📊 **Visualiza datos** | 🔍 **Explora noticias** | 🤖 **Haz predicciones**  
    """
)

# Divider
st.markdown("---")

# Sections Overview
st.header("🗂 Secciones Disponibles")

# Using columns for better layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Página Principal")
    st.write("Resumen general de las noticias más destacadas.")

    st.subheader("🔍 Buscador de noticias")
    st.write("Explora noticias y busca información específica.")

    st.subheader("📈 Presentación de Datos")
    st.write("Visualización de gráficos y estadísticas clave.")



with col2:
    st.subheader("⚖️ Comparador de Fuentes")
    st.write("Compara noticias según su fuente y credibilidad.")

    st.subheader("🗺️ Choropleth Map")  
    st.write("Visualiza la distribución geográfica de las noticias de Menéame con un mapa interactivo de colores, permitiendo identificar tendencias regionales de forma intuitiva.")

    st.subheader("👥 Acerca de Nosotros")
    st.write("Información sobre el equipo de desarrollo.")

# Final Message
st.markdown(
    """
    ---
    🎯 **Explora, analiza y descubre tendencias en Menéame con esta aplicación.**  
    ¡Esperamos que disfrutes la experiencia! 🚀
    """
)


