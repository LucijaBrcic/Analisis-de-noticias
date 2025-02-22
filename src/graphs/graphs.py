from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo de gráficos
sns.set_style("whitegrid")

# Configurar la conexión a MySQL con SQLAlchemy y mysql-connector
DB_USER = "root"
DB_PASSWORD = "Luis_1234_borras" # reemplaza tu password
DB_HOST = "localhost"
DB_NAME = "meneame"

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Crear el motor de conexión con SQLAlchemy
engine = create_engine(DATABASE_URL)

# Definir las consultas SQL
queries = {
    "karma_clicks_comunidad": """
        SELECT l.comunidad, AVG(ni.karma) AS avg_karma, AVG(ni.clicks) AS avg_clicks
        FROM news_info_table ni
        JOIN location_table l ON ni.provincia_id = l.provincia_id
        WHERE ni.karma IS NOT NULL AND ni.clicks IS NOT NULL
        GROUP BY l.comunidad
        ORDER BY avg_clicks DESC;
    """,
    "clicks_comentarios_comunidad": """
        SELECT l.comunidad, AVG(ni.clicks) AS avg_clicks, AVG(ni.comments) AS avg_comments
        FROM news_info_table ni
        JOIN location_table l ON ni.provincia_id = l.provincia_id
        WHERE ni.clicks IS NOT NULL AND ni.comments IS NOT NULL
        GROUP BY l.comunidad
        ORDER BY avg_clicks DESC;
    """,
    "karma_clicks_provincia": """
        SELECT l.provincia, AVG(ni.karma) AS avg_karma, AVG(ni.clicks) AS avg_clicks
        FROM news_info_table ni
        JOIN location_table l ON ni.provincia_id = l.provincia_id
        WHERE ni.karma IS NOT NULL AND ni.clicks IS NOT NULL
        GROUP BY l.provincia
        ORDER BY avg_clicks DESC;
    """,
    "clicks_comentarios_provincia": """
        SELECT l.provincia, AVG(ni.clicks) AS avg_clicks, AVG(ni.comments) AS avg_comments
        FROM news_info_table ni
        JOIN location_table l ON ni.provincia_id = l.provincia_id
        WHERE ni.clicks IS NOT NULL AND ni.comments IS NOT NULL
        GROUP BY l.provincia
        ORDER BY avg_clicks DESC;
    """,
    "karma_clicks_categoria": """
        SELECT c.category, (AVG(ni.clicks) / NULLIF(AVG(ni.karma), 0)) AS click_karma_ratio
        FROM news_info_table ni
        JOIN category_table c ON ni.category_id = c.category_id
        WHERE ni.karma IS NOT NULL AND ni.clicks IS NOT NULL
        GROUP BY c.category
        ORDER BY click_karma_ratio ASC
        LIMIT 10;
    """,
    "clicks_comentarios_categoria": """
        SELECT c.category, (AVG(ni.clicks) / NULLIF(AVG(ni.comments), 0)) AS click_comment_ratio
        FROM news_info_table ni
        JOIN category_table c ON ni.category_id = c.category_id
        WHERE ni.clicks IS NOT NULL AND ni.comments IS NOT NULL
        GROUP BY c.category
        ORDER BY click_comment_ratio ASC
        LIMIT 10;
    """,
}

# Crear gráficos
fig, axes = plt.subplots(3, 2, figsize=(15, 12))  # 3 filas, 2 columnas
axes = axes.flatten()  # Convertir en lista para fácil acceso

# Nombres de gráficos
titles = [
    "Relación Karma vs Clicks por Comunidad",
    "Relación Clicks vs Comentarios por Comunidad",
    "Relación Karma vs Clicks por Provincia",
    "Relación Clicks vs Comentarios por Provincia",
    "Clicks Necesarios por punto de Karma por Categoría",
    "Clicks Necesarios por Comentario por Categoría"
]

# Iterar sobre cada consulta y graficarla
for i, (key, query) in enumerate(queries.items()):
    # Obtener datos de MySQL y guardarlos en un DataFrame de pandas
    df = pd.read_sql(query, engine)

    # Extraer nombres de columnas
    x_column = df.columns[0]  # Nombre de la columna de agrupación (Comunidad, Provincia o Categoría)
    y_columns = df.columns[1:]  # Columnas de métricas

    # Graficar en el subplot correspondiente
    ax = axes[i]
    if len(y_columns) == 2:
        df.plot(x=x_column, y=y_columns.tolist(), kind="bar", ax=ax, width=0.8)
        ax.legend(["Promedio " + y_columns[0], "Promedio " + y_columns[1]])
    else:
        df.plot(x=x_column, y=y_columns[0], kind="bar", ax=ax, color='b', width=0.8)
        ax.legend(["Promedio " + y_columns[0]])

    # Personalización del gráfico
    ax.set_title(titles[i], fontsize=12)
    ax.set_xlabel(x_column, fontsize=10)
    ax.set_ylabel("Promedio", fontsize=10)
    ax.tick_params(axis='x', rotation=90)  # Rotar etiquetas en el eje X para mejor visualización

# Ajustar diseño y mostrar gráficos
plt.tight_layout()
plt.savefig("graphs.png", dpi=300, bbox_inches="tight")

# Cerrar la conexión al motor SQLAlchemy
engine.dispose()
