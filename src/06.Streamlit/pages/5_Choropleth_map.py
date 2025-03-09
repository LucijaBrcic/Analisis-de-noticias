import streamlit as st
import os
from dotenv import load_dotenv
import sys
load_dotenv()

user = os.getenv("user")
sys.path.append(f"/Users/{user}/Projects/Analisis-de-noticias/src")
from utils.nuevo_choropleth_map import generar_mapa
import streamlit.components.v1 as components

st.title("Mapa de Publicaciones en España")

nivel = st.radio("Seleccione el nivel de visualización:", ("provincia", "comunidad"))

st.write(f"Mostrando datos por {nivel.capitalize()}:")
mapa = generar_mapa(nivel=nivel)

map_file = "map.html"
mapa.save(map_file)

with open(map_file, "r", encoding="utf-8") as f:
    map_html = f.read()

components.html(map_html, height=600, scrolling=False)
