import pandas as pd
import numpy as np
from utils.provincias_data import PROVINCIAS_COMUNIDADES
from utils.news_category_map import news_category_map

class NewsProcessor:
    """
    A class to process news articles by assigning provinces, communities, and categories.
    """

    def __init__(self, provincias_comunidades=PROVINCIAS_COMUNIDADES, category_map=news_category_map):
        """
        Initialize the processor with external data dependencies.
        
        Args:
            provincias_comunidades (dict): Mapping of communities and provinces.
            category_map (dict): Mapping of categories to their associated keywords.
        """
        self.provincias_comunidades = provincias_comunidades
        self.category_lookup = {word.lower(): category for category, words in category_map.items() for word in words}

    def assign_province_and_community(self, df):
        """
        Assigns 'provincia' and 'comunidad' based on the 'title' and 'content' columns.

        Args:
            df (pd.DataFrame): DataFrame with 'title' and 'content' columns.

        Returns:
            pd.DataFrame: DataFrame with assigned 'provincia' and 'comunidad'.
        """

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

            return {"provincia": "Desconocido", "comunidad": "Desconocido"}

        df[["provincia", "comunidad"]] = df.apply(find_location, axis=1).apply(pd.Series)

        # Replace "Desconocido" with NaN
        df.replace({"provincia": "Desconocido", "comunidad": "Desconocido"}, np.nan, inplace=True)

        return df

    def categorize_news(self, df):
        """
        Maps each news article to a predefined category.

        Args:
            df (pd.DataFrame): DataFrame with a 'category' column.

        Returns:
            pd.DataFrame: DataFrame with updated category values.
        """
        df["category"] = df["category"].apply(lambda x: self.category_lookup.get(x.lower(), "Otros"))
        return df
