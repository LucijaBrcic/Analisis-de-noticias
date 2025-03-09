import pandas as pd
import geopandas as gpd
import folium
import branca
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("HOST", "localhost")
database = "meneame"

def get_engine():
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Mappings for province and community name adjustments
MAPEO_PROVINCIAS = {
    "Santa Cruz de Tenerife": "Santa Cruz De Tenerife"
}

MAPEO_COMUNIDADES = {
    "Castilla y León": "Castilla-Leon",
    "Islas Baleares": "Baleares",
    "Andalucía": "Andalucia",
    "Comunidad Valenciana": "Valencia",
    "Aragón": "Aragon",
    "Castilla La Mancha": "Castilla-La Mancha",
    "País Vasco": "Pais Vasco"
}

def generar_mapa(nivel="provincia"):
    """
    Generates a choropleth map of Spain based on the number of news publications.
    
    Args:
        nivel (str): "provincia" or "comunidad" to choose between provinces or autonomous communities.

    Returns:
        folium.Map: A Folium map object with a choropleth layer.
    """
    engine = get_engine()

    query = """
        SELECT l.provincia, COUNT(n.news_id) AS num_publicaciones, 
               SUM(n.clicks + n.karma + n.positive_votes + n.anonymous_votes + n.negative_votes + n.comments) AS engagement
        FROM news_info_table n
        JOIN location_table l ON n.provincia_id = l.provincia_id
        GROUP BY l.provincia
    """ if nivel == "provincia" else """
        SELECT l.comunidad, COUNT(n.news_id) AS num_publicaciones, 
               SUM(n.clicks + n.karma + n.positive_votes + n.anonymous_votes + n.negative_votes + n.comments) AS engagement
        FROM news_info_table n
        JOIN location_table l ON n.provincia_id = l.provincia_id
        GROUP BY l.comunidad
    """

    df = pd.read_sql(query, engine)

    # Ensure Timestamp Columns Are Converted to Strings in df
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)

    agrupacion = "provincia" if nivel == "provincia" else "comunidad"
    df = df[df[agrupacion] != "Desconocido"]
    df[agrupacion] = df[agrupacion].replace(MAPEO_PROVINCIAS if nivel == "provincia" else MAPEO_COMUNIDADES)

    # Load the correct GeoJSON file
    geojson_file = f"../00.data/GeoJSON/spain-{'provinces' if nivel == 'provincia' else 'communities'}.geojson"
    gdf = gpd.read_file(geojson_file)

    # Ensure Timestamp Columns Are Converted to Strings in gdf
    for col in gdf.columns:
        if pd.api.types.is_datetime64_any_dtype(gdf[col]):
            gdf[col] = gdf[col].astype(str)

    # Merge DataFrames
    gdf = gdf.merge(df, left_on="name", right_on=agrupacion, how="left").fillna(0)
    gdf["publicaciones_norm"] = gdf["num_publicaciones"] / gdf["num_publicaciones"].max()

    # Create the map
    mapa = folium.Map(location=[40.0, -3.5], zoom_start=6)
    colormap = branca.colormap.linear.YlOrRd_09.scale(0, 1)
    colormap.caption = "Número de Publicaciones"

    folium.GeoJson(
        gdf,
        name=f"Publicaciones por {nivel.capitalize()}",
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["publicaciones_norm"]),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        highlight_function=lambda feature: {"fillOpacity": 1, "weight": 2, "color": "black"},
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "num_publicaciones", "engagement"],
            aliases=[f"{nivel.capitalize()}:", "Publicaciones:", "Engagement:"],
            localize=True, sticky=False,
            style=("font-size: 16px; font-weight: bold;")
        )
    ).add_to(mapa)

    colormap.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    return mapa