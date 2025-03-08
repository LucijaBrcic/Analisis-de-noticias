import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import sys


load_dotenv()

user = os.getenv("user")
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")

from utils.sql import get_engine
from utils.graphs import DataVisualizer
engine = get_engine()

query = """
    SELECT ni.news_id, ni.title, ni.content, u.user, s.source, 
        c.category, l.provincia, l.comunidad, 
        ni.meneos, ni.clicks, ni.karma, ni.comments, 
        ni.positive_votes, ni.negative_votes, ni.anonymous_votes 
    FROM news_info_table ni 
    LEFT JOIN user_table u ON ni.user_id = u.user_id 
    LEFT JOIN source_table s ON ni.source_id = s.source_id 
    LEFT JOIN category_table c ON ni.category_id = c.category_id 
    LEFT JOIN location_table l ON ni.provincia_id = l.provincia_id 
    ORDER BY RAND() LIMIT 5000
"""

df = pd.read_sql(query, engine)

visualize = DataVisualizer(df)


subpage = st.sidebar.selectbox("Selecciona un análisis:", ["Descriptive", "Correlación", "Heatmap"])


if subpage == "Descriptive":
    st.write("📊 Resumen de los datos...")

elif subpage == "Correlación":
    st.title("Correlación")
    st.write("Aquí puedes seleccionar variables y visualizar cómo se relacionan entre sí.")

    numeric_variables = ["meneos", "clicks", "karma", "comments", "positive_votes", "negative_votes", "anonymous_votes"]
    hue_options = ["None", "category", "provincia", "comunidad"]

    variable1 = st.sidebar.selectbox("Variable 1", numeric_variables)
    variable2 = st.sidebar.selectbox("Variable 2", numeric_variables)
    hue = st.sidebar.selectbox("Color By (Hue)", hue_options)

    fig = visualize.create_scatter_plot(variable1, variable2, hue)

    st.plotly_chart(fig)



elif subpage == "Heatmap": 

    st.title("Datos de Noticias")

    # Get database connection
    engine = get_engine()

    # Display the heatmap
    st.subheader("📊 Correlation Heatmap of Numerical Variables")
    heatmap_fig = visualize.create_heatmap()
    st.plotly_chart(heatmap_fig)

