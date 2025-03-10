import streamlit as st
import os
from dotenv import load_dotenv
import sys
import pandas as pd
import plotly.graph_objects as go

# Load environment variables
load_dotenv()
user = os.getenv("user")
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")

# Import the ComparadorNoticias class
from utils.comparador import ComparadorNoticias

# Initialize the ComparadorNoticias class
comparador = ComparadorNoticias()

# Fetch category list for dropdown menu (Preload for faster loading)
@st.cache_data
def get_category_list():
    engine = comparador.get_engine()
    query = "SELECT DISTINCT category FROM category_table"
    df = pd.read_sql(query, engine)
    return df["category"].sort_values().tolist()

category_options = get_category_list()

# Streamlit App Layout
st.title("🕵️ Comparador de Noticias y Categorías")

# Select comparison type
option = st.radio("Selecciona una opción:", ["Comparador de Noticias", "Comparador de Categorías"])

# Comparison for News
if option == "Comparador de Noticias":
    st.subheader("📰 Comparar Noticias por ID")

    col1, col2 = st.columns(2)
    with col1:
        noticia1 = st.text_input("Ingrese el ID de la primera noticia")
    with col2:
        noticia2 = st.text_input("Ingrese el ID de la segunda noticia")

    if st.button("Comparar Noticias"):
        if noticia1 and noticia2:
            try:
                noticia1, noticia2 = int(noticia1), int(noticia2)
                df_news = comparador.get_data(news_ids=[noticia1, noticia2])

                if df_news.empty or len(df_news) < 2:
                    st.error("Una o ambas noticias no existen en la base de datos.")
                else:
                    max_values = comparador.get_max_values()
                    variables = ["clicks", "comments", "karma", "positive_votes", "anonymous_votes", "negative_votes"]

                    data1 = comparador.normalize_values(df_news.iloc[0][variables], max_values, variables)
                    data2 = comparador.normalize_values(df_news.iloc[1][variables], max_values, variables)

                    values1 = df_news.iloc[0][variables].values.tolist()
                    values2 = df_news.iloc[1][variables].values.tolist()

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=data1 + [data1[0]],
                        theta=variables + [variables[0]],
                        fill='toself',
                        name=f'Noticia {noticia1}',
                        text=values1,
                        hoverinfo='text',
                        line=dict(color='blue', width=2)
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=data2 + [data2[0]],
                        theta=variables + [variables[0]],
                        fill='toself',
                        name=f'Noticia {noticia2}',
                        text=values2,
                        hoverinfo='text',
                        line=dict(color='red', width=2)
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=True,
                        title="Comparación de Noticias",
                        width=700,
                        height=600
                    )

                    st.plotly_chart(fig)

                    # Show news details underneath
                    selected_columns = ["news_id", "title", "content", "user", "source", "provincia", "comunidad"]
                    st.subheader("📰 Detalles de las Noticias Comparadas")
                    st.dataframe(df_news[selected_columns])

            except ValueError:
                st.error("Por favor, ingrese valores numéricos válidos para los IDs de noticias.")
        else:
            st.warning("Por favor, ingrese ambos IDs de noticias antes de comparar.")


# Comparison for Categories
elif option == "Comparador de Categorías":
    st.subheader("📊 Comparar Categorías")

    col1, col2 = st.columns(2)
    with col1:
        categoria1 = st.selectbox("Seleccione la primera categoría", category_options)
    with col2:
        categoria2 = st.selectbox("Seleccione la segunda categoría", category_options)

    if st.button("Comparar Categorías"):
        if categoria1 and categoria2:
            try:
                df1 = comparador.get_data(category=categoria1)
                df2 = comparador.get_data(category=categoria2)

                if df1.empty or df2.empty:
                    st.error("Una de las categorías no tiene datos disponibles.")
                else:
                    max_values = comparador.get_max_values()
                    variables = ["clicks", "comments", "karma", "positive_votes", "anonymous_votes", "negative_votes"]

                    data1 = comparador.normalize_values(df1.iloc[0][variables], max_values, variables)
                    data2 = comparador.normalize_values(df2.iloc[0][variables], max_values, variables)

                    values1 = df1.iloc[0][variables].values.tolist()
                    values2 = df2.iloc[0][variables].values.tolist()

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=data1 + [data1[0]],
                        theta=variables + [variables[0]],
                        fill='toself',
                        name=f'Categoría {categoria1}',
                        text=values1,
                        hoverinfo='text',
                        line=dict(color='blue', width=2)
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=data2 + [data2[0]],
                        theta=variables + [variables[0]],
                        fill='toself',
                        name=f'Categoría {categoria2}',
                        text=values2,
                        hoverinfo='text',
                        line=dict(color='red', width=2)
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=True,
                        title="Comparación de Categorías",
                        width=700,
                        height=600
                    )

                    st.plotly_chart(fig)

            except ValueError:
                st.error("Error al comparar las categorías. Verifique los nombres ingresados.")
        else:
            st.warning("Por favor, seleccione ambas categorías antes de comparar.")
