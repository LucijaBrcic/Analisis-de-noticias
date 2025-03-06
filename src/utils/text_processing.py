import pandas as pd
import numpy as np
from utils.provincias_data import PROVINCIAS_COMUNIDADES
from utils.news_category_map import news_category_map

def asignar_provincia_comunidad(df):
    def find_location(row):
        title = str(row["title"]) if pd.notna(row["title"]) else ""
        content = str(row["content"]) if pd.notna(row["content"]) else ""

        for comunidad, datos in PROVINCIAS_COMUNIDADES.items():
            provincias = datos["provincias"]
            equivalencias = datos.get("equivalencias", {})

            for provincia in provincias:
                if provincia in title or provincia in content:
                    return {"provincia": provincia, "comunidad": comunidad}

            for variante, provincia_estandar in equivalencias.items():
                if variante in title or variante in content:
                    return {"provincia": provincia_estandar, "comunidad": comunidad}

        return {"provincia": "Desconocido", "comunidad": "Desconocido"}

    df[["provincia", "comunidad"]] = df.apply(find_location, axis=1).apply(pd.Series)

    df.replace({"provincia": "Desconocido", "comunidad": "Desconocido"}, np.nan, inplace=True)



def categorize_news(df):
    category_lookup = {word.lower(): category for category, words in news_category_map.items() for word in words}

    def map_category(category):
        return category_lookup.get(category.lower(), "Otros")

    df["category"] = df["category"].apply(map_category)
