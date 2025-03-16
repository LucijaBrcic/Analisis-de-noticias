import streamlit as st
import sqlalchemy
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys
import matplotlib.pyplot as plt

load_dotenv()

user = os.getenv("user")
sys.path.append(f"/Users/{user}/Analisis-de-noticias/src")

from utils.clustering import Clustering

st.title("Machine Learning en Menéame")

# 🔹 Introductory Section
st.markdown("""
### 🔍 Predicción de Clicks en Noticias Antiguas

En la plataforma Menéame, hay noticias publicadas antes del año 2010 que **no tienen registros de clicks**.  
El objetivo de esta sección es mostrar el proceso de **predecir la cantidad de clicks** para estas noticias utilizando **técnicas de Machine Learning**.  

Para lograrlo, hemos aplicado distintos modelos de **Clustering, Clasificación y Regresión**, que puedes explorar a continuación.
""")

# 🔹 Subpage Navigation
subpage = st.radio("Selecciona un análisis:", ["Clustering", "Clasificación", "Regresión", "Predicción de Cluster"])

if subpage == "Clustering":
    st.subheader("🔍 Clustering")
    st.write("Aquí mostramos los resultados del análisis de Clustering.")

    clustering = Clustering()

    # Initialize session state for storing figures
    if "elbow_chart" not in st.session_state:
        st.session_state.elbow_chart = None
    if "barplot" not in st.session_state:
        st.session_state.barplot = None
    if "heatmap" not in st.session_state:
        st.session_state.heatmap = None

    # Generate and store Elbow Chart
    if st.button("Generar Elbow Chart"):
        st.session_state.elbow_chart = clustering.generate_elbow_chart()  # 🔹 Properly indented

    # Display stored Elbow Chart
    if st.session_state.elbow_chart:
        st.pyplot(st.session_state.elbow_chart)

    # Select number of clusters
    n_clusters = st.slider("Selecciona el número de clusters:", min_value=2, max_value=10, value=3, step=1)

    # Generate and store Barplot
    if st.button("Generar Barplots para Clusters"):
        fig, ax = plt.subplots(figsize=(15, 10))
        clustering.apply_kmeans(n_clusters)
        clustering.df_numeric.groupby(f"cluster_{n_clusters}")[['karma', 'clicks', 'negative_votes', 
                                                                'positive_votes', 'anonymous_votes', 
                                                                'meneos', 'comments']].mean().T.plot(kind='bar', ax=ax)

        plt.title(f"Mean of Each Numeric Variable by Cluster ({n_clusters} Clusters)")
        plt.xlabel("Variables")
        plt.ylabel("Mean Value")
        plt.xticks(rotation=45)

        cluster_names = {
            0: "Noticias bien recibidas",
            1: "Noticias polémicas",
            2: "Noticias estándar"
        }

        # Update legend labels
        handles, labels = plt.gca().get_legend_handles_labels()
        custom_labels = [cluster_names.get(int(label), label) for label in labels]
        plt.legend(handles, custom_labels, title="Cluster")

        st.session_state.barplot = fig

    # Display stored Barplot
    if st.session_state.barplot:
        st.pyplot(st.session_state.barplot)

    # Generate and store Heatmap
    if st.button("Generar Heatmap de Categorías por Cluster"):
        fig = clustering.plot_heatmap(n_clusters)
        if fig:
            st.session_state.heatmap = fig
        else:
            st.warning("No hay datos suficientes para generar el heatmap.")

    # Display stored Heatmap
    if st.session_state.heatmap:
        st.pyplot(st.session_state.heatmap)

elif subpage == "Clasificación":
    st.subheader("🎯 Clasificación")
    st.write("Aquí mostramos los resultados del análisis de Clasificación.")

elif subpage == "Regresión":
    st.subheader("📈 Regresión")
    st.write("Aquí mostramos los resultados del análisis de Regresión.")

elif subpage == "Predicción de Cluster":
    st.subheader("🔮 Predicción de Cluster")
    st.write("Introduce los valores de una noticia y descubre a qué cluster pertenecería.")

    load_dotenv()

    def get_engine():
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("HOST", "localhost")
        database = "meneame"
        return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

    engine = get_engine()

    query = text("""
            SELECT 
                COALESCE(MAX(meneos), 0) AS max_meneos,
                COALESCE(MAX(karma), 0) AS max_karma,
                COALESCE(MAX(positive_votes), 0) AS max_positive_votes,
                COALESCE(MAX(anonymous_votes), 0) AS max_anonymous_votes,
                COALESCE(MAX(negative_votes), 0) AS max_negative_votes,
                COALESCE(MAX(comments), 0) AS max_comments
            FROM news_info_table;
    """)

    # Ejecutar la consulta y obtener los valores
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()

    # Inicializamos valores en 0
    max_meneos, max_karma, max_positive_votes, max_anonymous_votes, max_negative_votes, max_comments = result or (
    0, 0, 0, 0, 0, 0)

    # Configurar sliders en Streamlit con mínimo en 0 y máximo desde SQL
    meneos = st.slider("Meneos", min_value=0, max_value=max_meneos, value=0)
    karma = st.slider("Karma", min_value=0, max_value=max_karma, value=0)
    positive_votes = st.slider("Votos positivos", min_value=0, max_value=max_positive_votes, value=0)
    anonymous_votes = st.slider("Votos anónimos", min_value=0, max_value=max_anonymous_votes, value=0)
    negative_votes = st.slider("Votos negativos", min_value=0, max_value=max_negative_votes, value=0)
    comments = st.slider("Comentarios", min_value=0, max_value=max_comments, value=0)

    # Selección de categoría
    CATEGORIAS_FIJAS = [
        'Crimen', 'Cuestiones Sociales', 'Deportes', 'Educación', 'Entretenimiento y Cultura',
        'Historia y Humanidades', 'Humor y Memes', 'Medioambiente y Energía',
        'Negocios y Economía', 'Otros', 'Política y Sociedad', 'Salud y Medicina',
        'Tecnología y Ciencia', 'Transporte'
    ]
    categoria = st.selectbox("Categoría", CATEGORIAS_FIJAS)

    # Botón para hacer la predicción
    if st.button("Predecir Cluster"):
        from utils.prediccion_cluster import predecir_cluster  # Importar la función

        cluster_predicho = predecir_cluster(meneos, karma, positive_votes, anonymous_votes, negative_votes, comments,
                                            categoria)
        CLUSTER_SIGNIFICADO = {
            0: "Noticias polémicas o virales",
            1: "Noticias estándar",
            2: "Noticias bien recibidas"
        }
        # Mostrar el resultado
        st.success(f"La noticia pertenece al cluster: **{CLUSTER_SIGNIFICADO[cluster_predicho]}** (Cluster {cluster_predicho})")
