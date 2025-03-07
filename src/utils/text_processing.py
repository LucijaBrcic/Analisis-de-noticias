import pandas as pd
import numpy as np
from utils.provincias_data import PROVINCIAS_COMUNIDADES
from utils.news_category_map import news_category_map

class NewsProcessor:

    def __init__(self, provincias_comunidades=PROVINCIAS_COMUNIDADES, category_map=news_category_map):
        self.provincias_comunidades = provincias_comunidades
        self.category_lookup = {word.lower(): category for category, words in category_map.items() for word in words}

    def assign_province_and_community(self, df):
        def find_location(row):
            title = str(row["title"]) if pd.notna(row["title"]) else ""
            content = str(row["content"]) if pd.notna(row["content"]) else ""

            for comunidad, datos in self.provincias_comunidades.items():
                provincias = datos["provincias"]
                equivalencias = datos.get("equivalencias", {})

                for provincia in provincias:
                    if provincia in title or provincia in content:
                        return {"provincia": provincia, "comunidad": comunidad}

                for variante, provincia_estandar in equivalencias.items():
                    if variante in title or variante in content:
                        return {"provincia": provincia_estandar, "comunidad": comunidad}

            return {"provincia": np.nan, "comunidad": np.nan}  

        df[["provincia", "comunidad"]] = df.apply(find_location, axis=1).apply(pd.Series)

        return df

    def categorize_news(self, df):
        df["category"] = df["category"].apply(lambda x: self.category_lookup.get(x.lower(), "Otros"))
        return df

    def change_type(self, df):
        df = df.copy()  
        
        df = df.astype({
            "meneos": "uint16",
            "karma": "uint16",
            "positive_votes": "uint16",
            "negative_votes": "uint16",
            "anonymous_votes": "uint16",
            "comments": "uint16",
            "category": "category",
            "provincia": "category",
            "comunidad": "category"
        })

        df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce").astype("float32")

        df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")
        df["scraped_date"] = pd.to_datetime(df["scraped_date"], errors="coerce")

        return df 

