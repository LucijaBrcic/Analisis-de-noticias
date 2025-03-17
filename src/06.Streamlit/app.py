import streamlit as st
import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
user = os.getenv("user")

if user:
    sys.path.append(f"/Users/{user}/Analisis-de-noticias/src")
else:
    st.error("❌ Error: USER environment variable not found. Check your .env file.")

# Import scraper, processor, clustering, and DataProcessor
from utils.nuevo_scraper import MeneameScraper
from utils.text_processing import NewsProcessor  
import utils.cluster_model
from utils.sql_streamlit import DataProcessor 

#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(f"{page_title} {page_icon}")

# Initialize scraper and processor
scraper = MeneameScraper()
processor = NewsProcessor()

# Load database credentials
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("HOST", "localhost")
database = "meneame"

# Create connection to SQL
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{database}"

try:
    engine = create_engine(DATABASE_URL)
    st.success("✅ Conexión a la base de datos exitosa.")
except Exception as e:
    st.error(f"❌ Error al conectar con la base de datos: {e}")

# Initialize DataProcessor
data_processor = DataProcessor(engine)

# Display last scraped date
last_scraped = scraper.get_last_scraped_date()
if last_scraped:
    st.write(f"🕒 **Última fecha de actualización:** {last_scraped}")
else:
    st.write("⚠️ No hay datos anteriores. Presiona 'Actualizar' para comenzar.")

# Function to check existing news IDs
def get_existing_news_ids():
    """Fetches existing news IDs from SQL to check for duplicates."""
    query = "SELECT news_id FROM news_info_table"
    existing_news = pd.read_sql(query, engine)
    return set(existing_news["news_id"])

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

if latest_file and Path(latest_file).exists():
    try:
        df = pd.read_csv(latest_file)
        st.write("🧹 **Limpiando los datos...**")

        # Data Processing
        df_cleaned = processor.assign_province_and_community(df)
        df_cleaned = processor.categorize_news(df_cleaned)

        # Clustering
        df_clustered = utils.cluster_model.apply_clustering(
            df_cleaned,
            scaler_path="../00.data/clustering/scaler.pkl",
            encoder_path="../00.data/clustering/encoder.pkl",
            ml_clustering_path="../00.data/clustering/ml_clustering.pkl",
            output_path="../00.data/clustering/scraped_news_with_clusters.csv"
        )

        df_final = data_processor.process_dataframe(df_clustered)

        # Drop unused columns
        df_final = df_final.drop(columns=["category", "user", "provincia", "source", "comunidad", "full_story_link"], errors="ignore")
        df_final.rename(columns={"cluster": "cluster_id"}, inplace=True)

        # Get existing news IDs from the database
        existing_news_ids = get_existing_news_ids()

        # Separate new and existing data
        df_new = df_final[~df_final["news_id"].isin(existing_news_ids)]
        df_existing = df_final[df_final["news_id"].isin(existing_news_ids)]

        # Insert new data
        if not df_new.empty:
            df_new.to_sql("news_info_table", engine, if_exists="append", index=False, method="multi")
            st.success(f"✅ {len(df_new)} nuevas noticias insertadas correctamente en la base de datos.")

        # Update existing data
        if not df_existing.empty:
            with engine.begin() as conn:
                for _, row in df_existing.iterrows():
                    update_sql = text("""
                    REPLACE INTO news_info_table 
                    (news_id, title, content, meneos, clicks, karma, positive_votes, 
                    anonymous_votes, negative_votes, comments, published_date, source_link, 
                    scraped_date, cluster_id, user_id, source_id, category_id, provincia_id)
                    VALUES (:news_id, :title, :content, :meneos, :clicks, :karma, :positive_votes, 
                    :anonymous_votes, :negative_votes, :comments, :published_date, :source_link, 
                    :scraped_date, :cluster_id, :user_id, :source_id, :category_id, :provincia_id)
                    """)
                    conn.execute(update_sql, row.to_dict())

            st.success(f"✅ {len(df_existing)} noticias existentes fueron actualizadas en la base de datos.")

    except Exception as e:
        st.error(f"❌ Error al procesar los datos: {e}")

else:
    st.write("No hay datos guardados todavía.")



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


