import pandas as pd
import geopandas as gpd
import folium
import branca
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Cargar variables de entorno
load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("HOST", "localhost")
database = "meneame"


def get_engine():
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")


# Mapeo de nombres de provincias y comunidades
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

POBLACION_PROVINCIAS = {
    "Araba/Álava": 340420,
    "Albacete": 389426,
    "Alacant/Alicante": 2_008_809,
    "Almería": 765128,
    "Asturias": 1_010_058,
    "Ávila": 159803,
    "Badajoz": 665069,
    "Barcelona": 5_924_293,
    "Burgos": 359955,
    "Cáceres": 386832,
    "Cádiz": 1_258_881,
    "Cantabria": 591546,
    "Castelló/Castellón": 620186,
    "Ceuta": 83386,
    "Ciudad Real": 492802,
    "Córdoba": 770952,
    "Cuenca": 198648,
    "Girona": 824883,
    "Granada": 940974,
    "Guadalajara": 282734,
    "Gipuzkoa/Guipúzcoa": 730835,
    "Huelva": 535836,
    "Huesca": 229346,
    "Illes Balears": 1_238_812,
    "Jaén": 618031,
    "A Coruña": 1_130_238,
    "La Rioja": 325264,
    "Las Palmas": 1_164_130,
    "León": 446326,
    "Lleida": 452296,
    "Lugo": 324520,
    "Madrid": 7_058_041,
    "Málaga": 1_778_275,
    "Melilla": 86418,
    "Murcia": 1_575_171,
    "Navarra": 680296,
    "Ourense": 304238,
    "Palencia": 158003,
    "Pontevedra": 947957,
    "Salamanca": 327120,
    "Santa Cruz De Tenerife": 1_082_002,
    "Segovia": 157299,
    "Sevilla": 1_969_075,
    "Soria": 90131,
    "Tarragona": 866708,
    "Teruel": 135513,
    "Toledo": 743810,
    "València/Valencia": 2_730_314,
    "Valladolid": 525897,
    "Bizkaia/Vizcaya": 1_162_054,
    "Zamora": 166253,
    "Zaragoza": 983347
}

POBLACION_COMUNIDADES = {
    "Andalucia": 8_637_152,
    "Aragon": 1_348_206,
    "Asturias": 1_010_058,
    "Baleares": 1_238_812,
    "Canarias": 2_246_132,
    "Cantabria": 591546,
    "Castilla-La Mancha": 2_107_420,
    "Castilla-Leon": 2_390_787,
    "Cataluña": 8_068_180,
    "Madrid": 7_058_041,
    "Valencia": 5_359_309,
    "Extremadura": 1_051_901,
    "Galicia": 2_706_953,
    "La Rioja": 325264,
    "Navarra": 680296,
    "Pais Vasco": 2_233_309,
    "Murcia": 1_575_171,
    "Ceuta": 83386,
    "Melilla": 86418
}


def generar_mapa(nivel="provincia", variable="engagement"):
    """
    Genera un mapa coroplético de España basado en la variable seleccionada.

    Args:
        nivel (str): "provincia" o "comunidad".
        variable (str): Variable a visualizar en el mapa.

    Returns:
        folium.Map: Un objeto Folium con el mapa generado.
    """
    engine = get_engine()

    # Query para extraer datos
    query = f"""
        SELECT l.{'provincia' if nivel == 'provincia' else 'comunidad'} AS region, 
               COUNT(n.news_id) AS num_publicaciones, 
               SUM(n.clicks) AS clicks,
               SUM(n.karma) AS karma,
               SUM(n.positive_votes) AS positive_votes,
               SUM(n.anonymous_votes) AS anonymous_votes,
               SUM(n.negative_votes) AS negative_votes,
               SUM(n.meneos) AS meneos,
               SUM(n.comments) AS comments
        FROM news_info_table n
        JOIN location_table l ON n.provincia_id = l.provincia_id
        GROUP BY region
    """

    df = pd.read_sql(query, engine)

    # Reemplazar nombres según el nivel
    df["region"] = df["region"].replace(MAPEO_PROVINCIAS if nivel == "provincia" else MAPEO_COMUNIDADES)
    df = df[df["region"] != "Desconocido"]

    # Añadir la columna de población
    poblacion_dict = POBLACION_PROVINCIAS if nivel == "provincia" else POBLACION_COMUNIDADES
    df["poblacion"] = df["region"].map(poblacion_dict)

    # Filtrar regiones sin población conocida
    df = df.dropna(subset=["poblacion"])

    # Calcular métricas derivadas
    df["engagement"] = df["clicks"] / (df["poblacion"] / 100_000)
    df["karma_por_publicacion"] = df["karma"] / df["num_publicaciones"]
    df["votos_positivos_por_publicacion"] = df["positive_votes"] / df["num_publicaciones"]
    df["votos_negativos_por_publicacion"] = df["negative_votes"] / df["num_publicaciones"]
    df["meneos_por_publicacion"] = df["meneos"] / df["num_publicaciones"]
    df["comentarios_por_publicacion"] = df["comments"] / df["num_publicaciones"]

    # Cargar el GeoJSON adecuado
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    geojson_file = os.path.join(BASE_DIR, "..", "00.data", "GeoJSON",
                                f"spain-{'provinces' if nivel == 'provincia' else 'communities'}.geojson")
    gdf = gpd.read_file(geojson_file)

    # Unir los datos con el GeoJSON
    gdf = gdf.merge(df, left_on="name", right_on="region", how="left").fillna(0)

    # Convertir timestamps a strings (para evitar errores en folium)
    for col in ["created_at", "updated_at"]:
        if col in gdf.columns:
            gdf[col] = gdf[col].astype(str)

    # Ajustar normalización para evitar errores
    min_value = gdf[variable].min()
    max_value = gdf[variable].max()

    if max_value > min_value:
        gdf[f"{variable}_norm"] = (gdf[variable] - min_value) / (max_value - min_value)
    else:
        gdf[f"{variable}_norm"] = 0  # Si todos los valores son iguales, evitar divisiones por 0.

    # Crear el mapa
    mapa = folium.Map(location=[40.0, -3.5], zoom_start=6)

    # Ajustar colormap correctamente
    colormap = branca.colormap.linear.YlOrRd_09.scale(min_value, max_value)
    colormap.caption = variable.replace("_", " ").capitalize()

    # Agregar capa de polígonos coloreados
    folium.GeoJson(
        gdf,
        name=f"{variable.replace('_', ' ').capitalize()} por {nivel.capitalize()}",
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"][variable]) if feature["properties"][variable] > 0 else "white",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7 if feature["properties"][variable] > 0 else 0.1,
        },
        highlight_function=lambda feature: {"fillOpacity": 1, "weight": 2, "color": "black"},
        tooltip=folium.GeoJsonTooltip(
            fields=["name", variable],
            aliases=[f"{nivel.capitalize()}:", f"{variable.replace('_', ' ').capitalize()}:"],
            localize=True, sticky=False,
            style=("font-size: 16px; font-weight: bold;")
        )
    ).add_to(mapa)

    colormap.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    return mapa