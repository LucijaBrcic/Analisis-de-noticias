import streamlit as st
import os
from dotenv import load_dotenv
import sys

load_dotenv()

# Obtener usuario desde las variables de entorno
user = os.getenv("DB_USER")
if user:
    sys.path.append(f"/Users/{user}/Analisis-de-noticias/src")

# Importar la función para generar el mapa
from utils.nuevo_choropleth_map import generar_mapa
import streamlit.components.v1 as components

st.title("Mapa de Publicaciones en España")

# Selección del nivel de visualización con nombres en mayúscula
niveles_disponibles = {"Provincia": "provincia", "Comunidad": "comunidad"}
nivel_mostrar = st.radio("Seleccione el nivel de visualización:", list(niveles_disponibles.keys()))
nivel = niveles_disponibles[nivel_mostrar]  # Mapeo a la clave real usada en la función

# Diccionario para mostrar nombres más legibles en el selectbox
variables_mapeo = {
    "engagement": "Engagement (Clicks por cada 100,000 habitantes)",
    "karma_por_publicacion": "Ratio de Karma por publicación",
    "votos_positivos_por_publicacion": "Ratio de votos positivos por publicación",
    "votos_negativos_por_publicacion": "Ratio de votos negativos por publicación",
    "meneos_por_publicacion": "Ratio de meneos por publicación",
    "comentarios_por_publicacion": "Ratio de comentarios por publicación"
}

# Selección de variable con nombres legibles
variable_mostrar = st.selectbox("Seleccione la variable a visualizar:", list(variables_mapeo.values()))

# Obtener la clave interna correspondiente
variable = [k for k, v in variables_mapeo.items() if v == variable_mostrar][0]

st.write(f"Mostrando datos por {nivel_mostrar} con la variable {variable_mostrar}: ")

# Generar el mapa con la selección del usuario
mapa = generar_mapa(nivel=nivel, variable=variable)

# Guardar el mapa como HTML
map_file = "map.html"
mapa.save(map_file)

# Leer el archivo HTML y mostrarlo en Streamlit
with open(map_file, "r", encoding="utf-8") as f:
    map_html = f.read()

components.html(map_html, height=600, scrolling=False)
