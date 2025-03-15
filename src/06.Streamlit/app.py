import streamlit as st
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables
load_dotenv()
user = os.getenv("user")

# Add project path
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")

# Import the scraper class
from utils.nuevo_scraper import MeneameScraper


#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"
#----------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

st.title(page_title + " " + page_icon)


# Initialize Scraper
scraper = MeneameScraper()

# Get last scraped date
last_scraped = scraper.get_last_scraped_date()

# Display last scraped date
if last_scraped:
    st.write(f"🕒 **Última fecha de actualización:** {last_scraped}")
else:
    st.write("⚠️ No hay datos anteriores. Presiona 'Actualizar' para comenzar.")

# Button to trigger scraping
if st.button("🔄 Actualizar Datos"):
    with st.spinner("Obteniendo nuevas noticias..."):
        result = scraper.scrape()

    # Get the new last scraped date
    updated_last_scraped = scraper.get_last_scraped_date()
    
    # Display result
    if updated_last_scraped:
        st.success(f"✅ {result} **Última fecha de actualización:** {updated_last_scraped}")
    else:
        st.warning("⚠️ No se encontraron nuevas noticias.")

# Display the latest scraped data (if available)
latest_file = scraper.get_latest_scraped_file()

if latest_file:
    df = pd.read_csv(latest_file)
    st.write("📁 **Últimos datos guardados:**")
    st.dataframe(df.tail(10))  # Show last 10 rows
else:
    st.write("⚠️ No hay datos guardados todavía.")



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


