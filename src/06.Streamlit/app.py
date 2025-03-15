import streamlit as st
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
from pathlib import Path

# Load environment variables
load_dotenv()
user = os.getenv("user")

# Add project path
sys.path.append(f"/Users/{user}/Analisis-de-noticias/src")

# Import scraper and processor
from utils.nuevo_scraper import MeneameScraper
from utils.text_processing import NewsProcessor  # Import the text processing class

#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"
#----------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

st.title(page_title + " " + page_icon)

# Initialize scraper and processor
scraper = MeneameScraper()
processor = NewsProcessor()

# Define path for cleaned data
processed_data_dir = Path("../00.data/preprocesado")
processed_data_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
processed_file_path = processed_data_dir / "meneame_procesado.csv"

# Display last scraped date
last_scraped = scraper.get_last_scraped_date()
if last_scraped:
    st.write(f"🕒 **Última fecha de actualización:** {last_scraped}")
else:
    st.write("⚠️ No hay datos anteriores. Presiona 'Actualizar' para comenzar.")

# Button to trigger scraping
if st.button("🔄 Actualizar Datos"):
    with st.spinner("Obteniendo nuevas noticias..."):
        result = scraper.scrape()

    updated_last_scraped = scraper.get_last_scraped_date()

    if updated_last_scraped:
        st.success(f"✅ {result} **Última fecha de actualización:** {updated_last_scraped}")
    else:
        st.warning("⚠️ No se encontraron nuevas noticias.")

# Get the latest scraped file
latest_file = scraper.get_latest_scraped_file()

if latest_file:
    df = pd.read_csv(latest_file)
    print(df.columns)  # Check what columns are present

    # Run the cleaning process
    st.write("🧹 **Limpiando los datos...**")
    df_cleaned = processor.assign_province_and_community(df)
    df_cleaned = processor.categorize_news(df_cleaned)
    df_cleaned = processor.change_type(df_cleaned)

    # Save cleaned data separately
    df_cleaned.to_csv(processed_file_path, index=False)
    
    st.write(f"✅ **Datos limpios guardados en:** {processed_file_path}")
    st.write("📁 **Últimos datos limpios:**")
    st.dataframe(df_cleaned.tail(10))

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


