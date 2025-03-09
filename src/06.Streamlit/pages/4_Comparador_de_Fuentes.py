import streamlit as st
import os
from dotenv import load_dotenv
import sys
load_dotenv()

user = os.getenv("user")
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")
from utils.comparador_de_noticias import NewsAnalyzer

st.title("Comparación de Noticias o Categorías")

analyzer = NewsAnalyzer()
option = st.radio("Seleccione el tipo de comparación", ["Noticias", "Categorías"])

graph_placeholder = st.empty()

if option == "Noticias":
    col1, col2 = st.columns(2)
    with col1:
        news_id1 = st.text_input("Ingrese el ID de la primera noticia")
    with col2:
        news_id2 = st.text_input("Ingrese el ID de la segunda noticia")
    
    compare_button = st.button("Comparar")

    if compare_button and news_id1 and news_id2:
        try:
            fig = analyzer.comparar_plotly(category1, category2, tipo="categoria")

            if isinstance(fig, go.Figure):  # Check if the returned value is a Plotly Figure
                graph_placeholder.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Error: No se pudo generar la gráfica. Verifique los datos seleccionados.")

        except ValueError as e:
            st.error(str(e))

elif option == "Categorías":
    categories = analyzer.get_categories()
    col1, col2 = st.columns(2)
    with col1:
        category1 = st.selectbox("Seleccione la primera categoría", categories)
    with col2:
        category2 = st.selectbox("Seleccione la segunda categoría", categories)
    
    compare_button = st.button("Comparar")

    if compare_button and category1 and category2:
        try:
            fig = analyzer.comparar_plotly(category1, category2, tipo="categoria")
            graph_placeholder.plotly_chart(fig)
        except ValueError as e:
            st.error(str(e))
