import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime
import os
from dotenv import load_dotenv
import plotly.express as px
import numpy as np
import plotly.figure_factory as ff
import sys
load_dotenv()

user = os.getenv("user")
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")

from utils.nuevo_choropleth_map import generar_mapa
import streamlit.components.v1 as components
import streamlit as st

#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"
#----------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("HOST", "localhost")
database="meneame"

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

query = "SELECT ni.news_id, ni.title, ni.content, u.user, s.source, c.category, l.provincia, l.comunidad, ni.meneos, ni.clicks, ni.karma, ni.comments, ni.positive_votes, ni.negative_votes, ni.anonymous_votes FROM news_info_table ni " \
        "LEFT JOIN user_table u ON ni.user_id = u.user_id " \
        "LEFT JOIN source_table s ON ni.source_id = s.source_id " \
        "LEFT JOIN category_table c ON ni.category_id = c.category_id " \
        "LEFT JOIN location_table l ON ni.provincia_id = l.provincia_id"
df = pd.read_sql(query, engine)

# Sidebar navigation
st.sidebar.title("Navegación")
# Adjust sidebar width
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 350px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

menu_options = ["Página Principal", "Presentación de Datos", "Vista Detallada", "Comparador de Fuentes", "Mapa choropleth"]
page = st.sidebar.radio("Selecciona una página:", menu_options)

# Top navigation bar
st.markdown(
    """
    <style>
        .topnav {
            background-color: #002f6c;
            overflow: hidden;
            padding: 10px;
        }
        .topnav a {
            float: left;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
            font-size: 17px;
        }
        .topnav .dropdown {
            float: right;
            overflow: hidden;
        }
        .topnav .dropdown .dropbtn {
            font-size: 17px;
            border: none;
            outline: none;
            color: white;
            padding: 14px 16px;
            background-color: inherit;
            font-family: inherit;
            margin: 0;
        }
        .topnav .dropdown-content {
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
        }
        .topnav .dropdown-content a {
            float: none;
            color: black;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            text-align: left;
        }
        .topnav .dropdown:hover .dropdown-content {
            display: block;
        }
    </style>
    <div class="topnav">
        <a href="#">Página Principal</a>
        <a href="#">Presentación de Datos</a>
        <a href="#">Vista Detallada</a>
        <a href="#">Comparador de Fuentes</a>
        <div class="dropdown">
            <button class="dropbtn">☰</button>
            <div class="dropdown-content">
                <a href="#">Página Principal</a>
                <a href="#">Presentación de Datos</a>
                <a href="#">Vista Detallada</a>
                <a href="#">Comparador de Fuentes</a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Page content
if page == "Página Principal":
    st.header("Bienvenido al análisis de noticias")
    st.write("Explora los datos y analiza tendencias en las noticias.")

    # Sidebar filtros
    st.sidebar.header("Filter News")

    # Search bars filtros
    search_news_id = st.sidebar.text_input("Search by News ID")
    search_title = st.sidebar.text_input("Search by Title")
    search_content = st.sidebar.text_input("Search by Content")
    search_user = st.sidebar.text_input("Search by User")
    search_source = st.sidebar.text_input("Search by Source")

    # Dropdown filtros
    category_filter = st.sidebar.selectbox("Category", ["All"] + sorted(df['category'].dropna().unique().tolist()))
    province_filter = st.sidebar.selectbox("Province", ["All"] + sorted(df['provincia'].dropna().unique().tolist()))
    comunidad_filter = st.sidebar.selectbox("Comunidad", ["All"] + sorted(df['comunidad'].dropna().unique().tolist()))

    # Slider filtros para variables numericas
    meneos_range = st.sidebar.slider("Meneos", int(df['meneos'].min()), int(df['meneos'].max()), (int(df['meneos'].min()), int(df['meneos'].max())))
    clicks_range = st.sidebar.slider("Clicks", int(df['clicks'].min()), int(df['clicks'].max()), (int(df['clicks'].min()), int(df['clicks'].max())))
    karma_range = st.sidebar.slider("Karma", int(df['karma'].min()), int(df['karma'].max()), (int(df['karma'].min()), int(df['karma'].max())))
    comments_range = st.sidebar.slider("Comments", int(df['comments'].min()), int(df['comments'].max()), (int(df['comments'].min()), int(df['comments'].max())))
    positive_range = st.sidebar.slider("Positive Votes", int(df['positive_votes'].min()), int(df['positive_votes'].max()), (int(df['positive_votes'].min()), int(df['positive_votes'].max())))
    negative_range = st.sidebar.slider("Negative Votes", int(df['negative_votes'].min()), int(df['negative_votes'].max()), (int(df['negative_votes'].min()), int(df['negative_votes'].max())))
    anonymous_range = st.sidebar.slider("Anonymous Votes", int(df['anonymous_votes'].min()), int(df['anonymous_votes'].max()), (int(df['anonymous_votes'].min()), int(df['anonymous_votes'].max())))


    def filter_dataframe(df):
        if search_news_id:
            df = df[df['news_id'].astype(str).str.contains(search_news_id, case=False, na=False)]
        if search_title:
            df = df[df['title'].str.contains(search_title, case=False, na=False)]
        if search_content:
            df = df[df['content'].str.contains(search_content, case=False, na=False)]
        if search_user:
            df = df[df['user'].astype(str).str.contains(search_user, case=False, na=False)]
        if search_source:
            df = df[df['source'].astype(str).str.contains(search_source, case=False, na=False)]
        if category_filter != "All":
            df = df[df['category'] == category_filter]
        if province_filter != "All":
            df = df[df['provincia'] == province_filter]
        if comunidad_filter != "All":
            df = df[df['comunidad'] == comunidad_filter]
        df = df[(df['meneos'] >= meneos_range[0]) & (df['meneos'] <= meneos_range[1])]
        df = df[(df['clicks'] >= clicks_range[0]) & (df['clicks'] <= clicks_range[1])]
        df = df[(df['karma'] >= karma_range[0]) & (df['karma'] <= karma_range[1])]
        df = df[(df['comments'] >= comments_range[0]) & (df['comments'] <= comments_range[1])]
        df = df[(df['positive_votes'] >= positive_range[0]) & (df['positive_votes'] <= positive_range[1])]
        df = df[(df['negative_votes'] >= negative_range[0]) & (df['negative_votes'] <= negative_range[1])]
        df = df[(df['anonymous_votes'] >= anonymous_range[0]) & (df['anonymous_votes'] <= anonymous_range[1])]
        return df

    filtered_df = filter_dataframe(df)

    st.write("Filtered News Data:")
    st.dataframe(filtered_df)

elif page == "Presentación de Datos":
    st.header("Datos de Noticias")

    numeric_variables = ["meneos", "clicks", "karma", "comments", "positive_votes", "negative_votes", "anonymous_votes"]

    variable1 = st.sidebar.selectbox("Variable 1", numeric_variables)
    variable2 = st.sidebar.selectbox("Variable 2", numeric_variables)

    segment_option = st.sidebar.selectbox("Segmentar por:", ["None", "category", "provincia", "comunidad"])

    # heatmap

    st.sidebar.subheader("Correlación entre variables numéricas")
    numeric_variables = ["meneos", "clicks", "karma", "comments", "positive_votes", "negative_votes", "anonymous_votes"]
    corr_matrix = df[numeric_variables].corr()
    z = np.array(corr_matrix)
    x = ["AV" if col == "anonymous_votes" else "NV" if col == "negative_votes" else "PV" if col == "positive_votes" else "C" if col == "comments" else "K" if col == "karma" else "CL" if col == "clicks" else "M" if col == "meneos" else col for col in corr_matrix.columns]
    y = ["AV" if row == "anonymous_votes" else "NV" if row == "negative_votes" else "PV" if row == "positive_votes" else "C" if row == "comments" else "K" if row == "karma" else "CL" if row == "clicks" else "M" if row == "meneos" else row for row in corr_matrix.index]

    heatmap_fig = ff.create_annotated_heatmap(z, x=x, y=y, colorscale='Viridis', showscale=True, annotation_text=None, colorbar=dict(thickness=5))

    heatmap_fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.sidebar.plotly_chart(heatmap_fig)

    color_param = segment_option if segment_option != "None" else None

    fig1 = px.scatter(df, x=variable1, y=variable2, title=f'{variable1} vs {variable2} (Log-Transformed)', labels={f'{variable1}': f'Log({variable1})', f'{variable2}': f'Log({variable1})'}, log_x=True, log_y=True, color=color_param)

    st.plotly_chart(fig1)

elif page == "Vista Detallada":
    st.header("Vista Detallada de Noticias")
    st.write("Selecciona una noticia para ver más información detallada.")

elif page == "Comparador de Fuentes":
    st.header("Comparador de Fuentes")

elif page == "Mapa choropleth":

    st.title("Mapa de Publicaciones en España")

    # Select province or community level
    nivel = st.radio("Seleccione el nivel de visualización:", ("provincia", "comunidad"))

    # Generate the map
    st.write(f"Mostrando datos por {nivel.capitalize()}:")
    mapa = generar_mapa(nivel=nivel)

    # Save the map as an HTML file
    map_file = "map.html"
    mapa.save(map_file)

    # Read the HTML content and display it
    with open(map_file, "r", encoding="utf-8") as f:
        map_html = f.read()

    # Embed the HTML in Streamlit
    components.html(map_html, height=600, scrolling=False)
