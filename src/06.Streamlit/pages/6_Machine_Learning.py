import streamlit as st
import pickle
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import seaborn as sns
import plotly.figure_factory as ff

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
subpage = st.radio("Selecciona un análisis:", ["Clustering", "Clasificación", "Regresión", "Predicción de Noticias"])

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
    # 📌 Definir ruta de datos
    DATA_PATH = "src/00.data/clustering"

    st.subheader("🎯 Clasificación")
    st.write("Aquí mostramos los resultados del análisis de Clasificación.")


    # 📌 Cargar archivos necesarios
    def load_pickle(file_path):
        """Carga un archivo pickle si existe, sino devuelve None."""
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            st.error(f"❌ No se encontró el archivo `{file_path}`.")
            return None


    # Cargar datos
    y_test = load_pickle(os.path.join(DATA_PATH, "y_test.pkl"))
    y_pred = load_pickle(os.path.join(DATA_PATH, "y_pred.pkl"))
    cm = load_pickle(os.path.join(DATA_PATH, "confusion_matrix.pkl"))
    df_numeric = load_pickle(os.path.join(DATA_PATH, "df_numeric.pkl"))
    cluster_counts = load_pickle(os.path.join(DATA_PATH, "cluster_counts.pkl"))
    df_cluster_means = load_pickle(os.path.join(DATA_PATH, "df_cluster_means.pkl"))
    cluster_category_pct = load_pickle(os.path.join(DATA_PATH, "cluster_category_pct.pkl"))

    # 📌 1️⃣ Distribución de Noticias por Cluster
    if cluster_counts is not None:
        st.markdown("### 📌 Distribución de Noticias por Cluster")

        fig, ax = plt.subplots()
        cluster_counts.plot(kind="bar", color=["red", "blue", "green"], ax=ax)
        ax.set_xticks(range(len(cluster_counts.index)))
        ax.set_xticklabels(cluster_counts.index, rotation=45)
        ax.set_ylabel("Cantidad de Noticias")
        ax.set_title("Distribución de Noticias por Cluster")

        st.pyplot(fig)

    # 📌 2️⃣ Características Promedio por Cluster
    if df_cluster_means is not None:
        st.markdown("### 📊 Características Promedio por Cluster")
        st.dataframe(df_cluster_means.style.format("{:.2f}"))

    # 📌 3️⃣ Explicación de los Clusters
    st.markdown("### 🔎 Explicación de los Clusters")
    st.write("""
    #### Cluster 0 → Noticias Polémicas o Virales 🔥  
    - Menos numeroso, pero con la media más alta de **clicks**, **votos anónimos** y **comentarios**.  
    - Genera una gran interacción, pero también es el grupo con más **votos negativos**.  

    #### Cluster 1 → Noticias Estándar 📰  
    - Es el cluster más numeroso con gran diferencia.  
    - Tiene el menor número de **meneos y clicks**, un **karma medio** y los **votos positivos y negativos más bajos**.  
    - Recibe la menor cantidad de **comentarios**, lo que sugiere menor interacción.  

    #### Cluster 2 → Noticias Bien Recibidas 🌟  
    - Recibe la mayor cantidad de **meneos** y tiene el **karma más alto**.  
    - Los **votos positivos y anónimos** son los más altos, con una cantidad significativa de **comentarios**.  
    - Representa las noticias populares y apreciadas dentro de la comunidad.  
    """)

    # 📌 4️⃣ Distribución de Categorías por Cluster (%)
    if cluster_category_pct is not None:
        st.markdown("### 📊 Distribución de Categorías por Cluster (%)")

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(cluster_category_pct, cmap="coolwarm", annot=True, fmt=".1f", linewidths=0.5, ax=ax)
        ax.set_title("Distribución de Categorías por Cluster (%)")
        ax.set_ylabel("Cluster")
        ax.set_xlabel("Categoría")

        st.pyplot(fig)

    # 📌 5️⃣ Matriz de Confusión
    if cm is not None:
        st.markdown("### 🔥 Matriz de Confusión")
        labels = ["Cluster 0 - Noticias polémicas", "Cluster 1 - Noticias estándar",
                  "Cluster 2 - Noticias bien recibidas"]

        fig = ff.create_annotated_heatmap(
            z=cm,
            x=labels,
            y=labels,
            colorscale="Blues",
            showscale=True
        )

        fig.update_layout(title="Matriz de Confusión", xaxis=dict(title="Predicho"), yaxis=dict(title="Real"))
        st.plotly_chart(fig, use_container_width=True)

    # 📌 6️⃣ Reporte de Clasificación
    if y_test is not None and y_pred is not None:
        st.markdown("### 📊 Reporte de Clasificación")
        report_dict = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose()
        st.dataframe(report_df.style.format({"precision": "{:.2f}", "recall": "{:.2f}", "f1-score": "{:.2f}"}))


elif subpage == "Regresión":
    st.subheader("📈 Regresión")
    st.write("Aquí mostramos los resultados del análisis de Regresión.")

elif subpage == "Predicción de Noticias":
    st.subheader("🔮 Predicción de Noticias")
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
    if st.button("Predecir Cluster y Clicks"):
        from utils.prediccion_cluster import predecir_cluster  # Importar la función
        from utils.prediccion_regresion import predecir_clicks  # Importar la función de regresión

        # **1️⃣ Predecir Cluster**
        cluster_predicho = predecir_cluster(meneos, karma, positive_votes, anonymous_votes, negative_votes, comments,
                                            categoria)

        CLUSTER_SIGNIFICADO = {
            0: "Noticias polémicas o virales",
            1: "Noticias estándar",
            2: "Noticias bien recibidas"
        }

        # **2️⃣ Predecir Clicks usando el Cluster obtenido**
        predicted_clicks = predecir_clicks(meneos, karma, positive_votes, anonymous_votes, negative_votes, comments,
                                           categoria, cluster_predicho)

        # **3️⃣ Mostrar los resultados**
        st.success(
            f"La noticia pertenece al cluster: **{CLUSTER_SIGNIFICADO[cluster_predicho]}** (Cluster {cluster_predicho})")
        st.markdown(f"🔮 Se estima que la noticia recibirá aproximadamente **{int(predicted_clicks):,} clicks**.")