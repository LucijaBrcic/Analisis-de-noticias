import os
import sys
import pickle
from dotenv import load_dotenv
import numpy as np
import pandas as pd

load_dotenv()

# Obtener el usuario desde .env
user = os.getenv("user")

BASE_DIR = f"/Users/{user}/Analisis-de-noticias/src/00.data/clustering"

if not user:
    raise ValueError("La variable de entorno user no está definida en el .env")

# Cargar los modelos guardados
src_path = f"/Users/{user}/Analisis-de-noticias/src"
if src_path not in sys.path:
    sys.path.append(src_path)

# Definir rutas de los modelos
scaler_path = os.path.join(BASE_DIR, "scaler.pkl")
encoder_path = os.path.join(BASE_DIR, "encoder.pkl")
ml_clustering_path = os.path.join(BASE_DIR, "ml_clustering.pkl")

# Verificar existencia de archivos antes de cargarlos
for path in [scaler_path, encoder_path, ml_clustering_path]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"El archivo {path} no existe. Verifica la ruta.")

# Cargar los modelos
with open(scaler_path, "rb") as f:
    scaler = pickle.load(f)

with open(encoder_path, "rb") as f:
    encoder = pickle.load(f)

with open(ml_clustering_path, "rb") as f:
    rf_model = pickle.load(f)

# Lista de categorías fijas
CATEGORIAS_FIJAS = [
    'Crimen', 'Cuestiones Sociales', 'Deportes', 'Educación', 'Entretenimiento y Cultura',
    'Historia y Humanidades', 'Humor y Memes', 'Medioambiente y Energía',
    'Negocios y Economía', 'Otros', 'Política y Sociedad', 'Salud y Medicina',
    'Tecnología y Ciencia', 'Transporte'
]

# Features utilizadas en el modelo
features_numericas = ['meneos', 'karma', 'positive_votes', 'anonymous_votes', 'negative_votes', 'comments']
feature_categorica = 'category'

def predecir_cluster(meneos, karma, positive_votes, anonymous_votes, negative_votes, comments, categoria):
    """Predice el cluster de una noticia basada en sus características."""

    # Convertir datos a formato DataFrame
    df_input = pd.DataFrame([[meneos, karma, positive_votes, anonymous_votes, negative_votes, comments, categoria]],
                            columns=features_numericas + [feature_categorica])

    # Escalar valores numéricos
    df_scaled = scaler.transform(df_input[features_numericas])

    # Manejar el OneHotEncoder para evitar errores por categorías faltantes
    # Crear DataFrame temporal con todas las categorías
    df_dummy = pd.DataFrame({feature_categorica: CATEGORIAS_FIJAS})

    # Aplicar el encoder con la fila de entrada agregada
    encoded_categorias = encoder.transform(pd.concat([df_dummy, df_input[[feature_categorica]]]))

    # Convertir a DataFrame y eliminar las filas dummy
    encoded_categorias_df = pd.DataFrame(encoded_categorias[-1:],
                                         columns=encoder.get_feature_names_out([feature_categorica]))

    # Unir los datos transformados
    df_final = pd.concat([pd.DataFrame(df_scaled, columns=features_numericas), encoded_categorias_df], axis=1)

    # Asegurar que las columnas coinciden con las del modelo
    df_final = df_final.reindex(columns=rf_model.feature_names_in_, fill_value=0)

    # Hacer la predicción
    cluster_predicho = rf_model.predict(df_final)[0]

    return cluster_predicho

