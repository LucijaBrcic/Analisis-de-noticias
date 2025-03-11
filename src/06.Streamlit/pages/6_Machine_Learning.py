import streamlit as st
import os
from dotenv import load_dotenv
import sys
import matplotlib.pyplot as plt

load_dotenv()

user = os.getenv("user")
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")

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
subpage = st.radio("Selecciona un análisis:", ["Clustering", "Clasificación", "Regresión"])

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
