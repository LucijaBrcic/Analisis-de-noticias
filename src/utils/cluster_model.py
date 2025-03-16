import pickle
import pandas as pd

def apply_clustering(df_nuevo, scaler_path, encoder_path, ml_clustering_path, output_path):
    # Load the pre-trained objects
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    
    with open(encoder_path, "rb") as f:
        encoder = pickle.load(f)
    
    with open(ml_clustering_path, "rb") as f:
        rf_model = pickle.load(f)
    
    features_numericas = ['meneos', 'karma', 'positive_votes', 'anonymous_votes', 'negative_votes', 'comments']
    feature_categorica = 'category'
    
    # Check if required columns exist
    if not all(col in df_nuevo.columns for col in features_numericas + [feature_categorica]):
        raise ValueError("Faltan columnas necesarias en el DataFrame.")
    
    # Scale numerical features
    df_scaled = scaler.transform(df_nuevo[features_numericas])
    
    # Encode categorical feature
    encoded_categorias = encoder.transform(df_nuevo[[feature_categorica]])
    encoded_categorias_df = pd.DataFrame(encoded_categorias, columns=encoder.get_feature_names_out([feature_categorica]))
    
    # Combine transformed data
    df_final = pd.concat([pd.DataFrame(df_scaled, columns=features_numericas), encoded_categorias_df], axis=1)
    
    # Ensure column order matches model input
    df_final = df_final.reindex(columns=rf_model.feature_names_in_, fill_value=0)
    
    # Predict clusters
    df_nuevo["cluster"] = rf_model.predict(df_final)
    
    
    print("Predicción de clusters completada y guardada en", output_path)
    
    return df_nuevo
