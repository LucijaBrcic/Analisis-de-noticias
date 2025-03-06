import numpy as np
import joblib
import pandas as pd
import os
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Configuración de la conexión a la base de datos
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("HOST", "localhost")
DB_NAME = "meneame"
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

print("Conectado a la base de datos")

# Cargar los datos desde la base de datos
query_news = "SELECT * FROM news_info_table"
df_news = pd.read_sql(query_news, engine)

# Seleccionar características relevantes
features = ['category_id', 'meneos', 'karma', 'positive_votes', 'negative_votes', 'comments', 'published_date']
df_selected = df_news[features + ['clicks']]  # Incluimos 'clicks' como la variable objetivo

# 1. Preprocesamiento de datos
df_selected = df_selected.dropna()

# Extraer características útiles de 'published_date'
df_selected['published_date'] = pd.to_datetime(df_selected['published_date'])
df_selected['day_of_week'] = df_selected['published_date'].dt.dayofweek  # Día de la semana (0: lunes, 6: domingo)
df_selected['month'] = df_selected['published_date'].dt.month  # Mes (1: enero, 12: diciembre)
df_selected['year'] = df_selected['published_date'].dt.year  # Año

# Eliminar la columna 'published_date' original
df_selected.drop('published_date', axis=1, inplace=True)

# Crear nuevas características numéricas
df_selected['votes_ratio'] = df_selected['positive_votes'] / (df_selected['negative_votes'] + 1)  # +1 para evitar división por cero
df_selected['votes_diff'] = df_selected['positive_votes'] - df_selected['negative_votes']
df_selected['interaction'] = df_selected['meneos'] * df_selected['karma']

# Verificar los tipos de datos
print(df_selected.dtypes)

# 2. Dividir los datos
X = df_selected.drop('clicks', axis=1)
y = df_selected['clicks']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Ajuste de hiperparámetros con RandomizedSearchCV
param_dist = {
    'n_estimators': [100, 200, 300, 400],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}

model = RandomForestRegressor(random_state=42)
random_search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_dist,
    n_iter=20,
    cv=5,
    scoring='neg_mean_squared_error',
    random_state=42,
    n_jobs=-1,  # Usar todos los núcleos disponibles
    verbose=10  # Aumentar el nivel de verbosidad para monitorear el progreso
)

# Entrenar el modelo con búsqueda de hiperparámetros
print("Iniciando la búsqueda de hiperparámetros...")
random_search.fit(X_train, y_train)

# Mejores hiperparámetros encontrados
print("Mejores hiperparámetros:", random_search.best_params_)

# 4. Entrenar el modelo con los mejores hiperparámetros
best_model = random_search.best_estimator_
best_model.fit(X_train, y_train)

# 5. Evaluación del modelo
y_pred = best_model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Error Cuadrático Medio (MSE): {mse}')
print(f'Error Absoluto Medio (MAE): {mae}')
print(f'Coeficiente de Determinación (R²): {r2}')

# 6. Análisis de residuales
residuals = y_test - y_pred
print("Residuales (media):", np.mean(residuals))
print("Residuales (desviación estándar):", np.std(residuals))

# 7. Guardar el modelo mejorado
joblib.dump(best_model, 'modelo_entrenado_mejorado.pkl')
print("Modelo guardado como 'modelo_entrenado_mejorado.pkl'")