from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo de gráficos
sns.set_style("whitegrid")

# Configurar la conexión a MySQL con SQLAlchemy y mysql-connector
DB_USER = "root"
DB_PASSWORD = "Luis_1234_borras"  # Reemplaza con tu password
DB_HOST = "localhost"
DB_NAME = "meneame"

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Crear el motor de conexión con SQLAlchemy
engine = create_engine(DATABASE_URL)

# Consulta SQL para obtener datos agrupados por provincia, comunidad y categoría
query = """
    SELECT l.provincia AS segment, l.comunidad AS community, c.category AS category, 
           AVG(ni.karma) AS avg_karma, AVG(ni.clicks) AS avg_clicks, AVG(ni.comments) AS avg_comments
    FROM news_info_table ni
    JOIN location_table l ON ni.provincia_id = l.provincia_id
    JOIN category_table c ON c.category_id = ni.category_id
    WHERE 
          ni.karma IS NOT NULL 
          AND ni.clicks IS NOT NULL 
          AND ni.comments IS NOT NULL
    GROUP BY l.provincia, l.comunidad, ni.category_id;
"""

# Obtener datos y guardarlos en un DataFrame
df = pd.read_sql(query, engine)

# Verificar si hay datos
if df.empty:
    print("No hay datos disponibles.")
else:
    # Crear figura con seis subgráficos
    fig, axes = plt.subplots(2, 3, figsize=(30, 12))

    # Gráfico 1: Relación Clicks vs Karma por Provincia
    sns.scatterplot(
        data=df, x="avg_clicks", y="avg_karma", hue="segment", palette="viridis", s=100, alpha=0.8, ax=axes[0, 0]
    )
    axes[0, 0].set_xlabel("Promedio Clicks", fontsize=12)
    axes[0, 0].set_ylabel("Promedio Karma", fontsize=12)
    axes[0, 0].set_title("Clicks vs Karma por Provincia", fontsize=14)
    axes[0, 0].legend(title="Provincia")

    # Gráfico 2: Relación Clicks vs Comentarios por Provincia
    sns.scatterplot(
        data=df, x="avg_clicks", y="avg_comments", hue="segment", palette="plasma", s=100, alpha=0.8, ax=axes[0, 1]
    )
    axes[0, 1].set_xlabel("Promedio Clicks", fontsize=12)
    axes[0, 1].set_ylabel("Promedio Comentarios", fontsize=12)
    axes[0, 1].set_title("Clicks vs Comentarios por Provincia", fontsize=14)
    axes[0, 1].legend(title="Provincia")

    # Gráfico 3: Relación Clicks vs Karma por Comunidad
    sns.scatterplot(
        data=df, x="avg_clicks", y="avg_karma", hue="community", palette="coolwarm", s=100, alpha=0.8, ax=axes[0, 2]
    )
    axes[0, 2].set_xlabel("Promedio Clicks", fontsize=12)
    axes[0, 2].set_ylabel("Promedio Karma", fontsize=12)
    axes[0, 2].set_title("Clicks vs Karma por Comunidad", fontsize=14)
    axes[0, 2].legend(title="Comunidad")

    # Gráfico 4: Relación Clicks vs Comentarios por Comunidad
    sns.scatterplot(
        data=df, x="avg_clicks", y="avg_comments", hue="community", palette="magma", s=100, alpha=0.8, ax=axes[1, 0]
    )
    axes[1, 0].set_xlabel("Promedio Clicks", fontsize=12)
    axes[1, 0].set_ylabel("Promedio Comentarios", fontsize=12)
    axes[1, 0].set_title("Clicks vs Comentarios por Comunidad", fontsize=14)
    axes[1, 0].legend(title="Comunidad")

    # Gráfico 5: Relación Clicks vs Karma por Categoría
    sns.scatterplot(
        data=df, x="avg_clicks", y="avg_karma", hue="category", palette="cubehelix", s=100, alpha=0.8, ax=axes[1, 1]
    )
    axes[1, 1].set_xlabel("Promedio Clicks", fontsize=12)
    axes[1, 1].set_ylabel("Promedio Karma", fontsize=12)
    axes[1, 1].set_title("Clicks vs Karma por Categoría", fontsize=14)
    axes[1, 1].legend(title="Categoría")

    # Gráfico 6: Relación Clicks vs Comentarios por Categoría
    sns.scatterplot(
        data=df, x="avg_clicks", y="avg_comments", hue="category", palette="Set2", s=100, alpha=0.8, ax=axes[1, 2]
    )
    axes[1, 2].set_xlabel("Promedio Clicks", fontsize=12)
    axes[1, 2].set_ylabel("Promedio Comentarios", fontsize=12)
    axes[1, 2].set_title("Clicks vs Comentarios por Categoría", fontsize=14)
    axes[1, 2].legend(title="Categoría")

    # Ajustar diseño
    plt.tight_layout()

    plt.savefig("graphs.png", dpi=300, bbox_inches="tight")

    plt.show()

# Cerrar la conexión al motor SQLAlchemy
engine.dispose()
