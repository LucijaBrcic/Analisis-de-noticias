import pickle
import os
import sys
import numpy as np
import pandas as pd

# Obtener el usuario desde .env
user = os.getenv("user")
if not user:
    raise ValueError("La variable de entorno 'user' no está definida en el .env")

# Definir ruta base para los modelos de regresión
BASE_DIR = f"/Users/{user}/Analisis-de-noticias/src/00.data/clustering"

# Asegurar que la ruta de `src` está en `sys.path`
src_path = f"/Users/{user}/Analisis-de-noticias/src"
if src_path not in sys.path:
    sys.path.append(src_path)


def predecir_clicks(meneos, karma, positive_votes, anonymous_votes, negative_votes, comments, category,
                    cluster_predicho):
    """
    Predice la cantidad de clicks de una noticia dada según sus características y el cluster predicho.

    Parámetros:
    - meneos, karma, positive_votes, anonymous_votes, negative_votes, comments: características numéricas de la noticia.
    - category: Categoría de la noticia.
    - cluster_predicho: Cluster al que pertenece la noticia (0, 1 o 2).

    Retorna:
    - Número estimado de clicks.
    """
    # Definir rutas específicas del cluster
    scaler_path = os.path.join(BASE_DIR, f"regressor_scaler.pkl")
    encoder_path = os.path.join(BASE_DIR, f"regressor_encoder.pkl")
    ml_regression_model_path = os.path.join(BASE_DIR, f"ml_regression_cluster_{cluster_predicho}.pkl")

    # Verificar que los archivos existen antes de cargarlos
    for path in [scaler_path, encoder_path, ml_regression_model_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"El archivo {path} no existe. Verifica la ruta.")

    # Cargar los modelos
    with open(scaler_path, "rb") as f:
        regressor_scaler = pickle.load(f)

    with open(encoder_path, "rb") as f:
        regressor_encoder = pickle.load(f)

    with open(ml_regression_model_path, "rb") as f:
        regressor_model = pickle.load(f)

    # Escalar las variables numéricas
    features_numericas = ["meneos", "karma", "positive_votes", "anonymous_votes", "negative_votes", "comments"]
    df_input = pd.DataFrame([[meneos, karma, positive_votes, anonymous_votes, negative_votes, comments]],
                            columns=features_numericas)
    df_scaled = regressor_scaler.transform(df_input)

    # Codificar la variable categórica
    feature_categorica = "category"
    df_categoria = pd.DataFrame([[category]], columns=[feature_categorica])
    encoded_categoria = regressor_encoder.transform(df_categoria)
    encoded_categoria_df = pd.DataFrame(encoded_categoria,
                                        columns=regressor_encoder.get_feature_names_out([feature_categorica]))

    # Unir los datos transformados
    df_final = pd.concat([pd.DataFrame(df_scaled, columns=features_numericas), encoded_categoria_df], axis=1)

    # Reordenar columnas según las usadas en el entrenamiento del modelo
    expected_columns = regressor_model.feature_names_in_
    df_final = df_final.reindex(columns=expected_columns, fill_value=0)

    # Hacer la predicción
    predicted_clicks = regressor_model.predict(df_final)[0]

    return int(predicted_clicks)

