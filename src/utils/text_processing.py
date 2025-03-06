import pandas as pd
import numpy as np
from utils.provincias_data import PROVINCIAS_COMUNIDADES

def asignar_provincia_comunidad(df):
    """
    Assigns 'provincia' and 'comunidad' based on the 'title' and 'content' columns.
    If 'Desconocido' is assigned, it replaces it with NaN.

    Args:
        df (pd.DataFrame): DataFrame containing 'title' and 'content' columns.

    Returns:
        pd.DataFrame: The updated DataFrame with 'provincia' and 'comunidad' columns.
    """
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

    # Apply function to all rows
    df[["provincia", "comunidad"]] = df.apply(find_location, axis=1).apply(pd.Series)

    # Replace "Desconocido" with NaN
    df.replace({"provincia": "Desconocido", "comunidad": "Desconocido"}, np.nan, inplace=True)

    return df
