import pandas as pd
import mysql.connector

#Este fichero deberia ser la union del 1,2,3 de la carpeta csvs...

df = pd.read_csv("meneame_scraped_final.csv")
df.head()

#Quitar duplicados y mostrar con la función.

df = df.drop_duplicates()
df = df.dropna()
df.shape

#Conector SQL.

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password", # reemplaza tu password aqui
    database="meneame"
)
cursor = conn.cursor()

#Cargar el CSV
#df = pd.read_csv("meneame_scraped_final.csv", encoding="utf-8")

#Insertar datos en la base de datos

for _, row in df.iterrows():
    try:
        # 🔹 Insertar categoría si no existe
        
        cursor.execute("SELECT category_id FROM category_table WHERE category = %s", (row["category"],))
        category_result = cursor.fetchone()
        if category_result:
            category_id = category_result[0]
        else:
            cursor.execute("INSERT INTO category_table (category) VALUES (%s)", (row["category"],))
            conn.commit()
            category_id = cursor.lastrowid

        # 🔹 Insertar usuario si no existe
        
        cursor.execute("SELECT user_id FROM user_table WHERE user = %s", (row["user"],))
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
        else:
            cursor.execute("INSERT INTO user_table (user) VALUES (%s)", (row["user"],))
            conn.commit()
            user_id = cursor.lastrowid

        # 🔹 Insertar fuente si no existe, hacemos la verificación "source" en la tabla dentro de la base de datos.
        
        cursor.execute("SELECT source_id FROM source_table WHERE source = %s", (row["source"],))
        source_result = cursor.fetchone()
        if source_result:
            source_id = source_result[0]
        else:
            cursor.execute("INSERT INTO source_table (source) VALUES (%s)", (row["source"],))
            conn.commit()
            source_id = cursor.lastrowid

        # 🔹 Insertar provincia si no existe, aseguramos que "provincia y comunidad existe" con la función cursor executive().
        
        cursor.execute("SELECT provincia_id FROM location_table WHERE provincia = %s", (row["provincia"],))
        provincia_result = cursor.fetchone()
        if provincia_result:
            provincia_id = provincia_result[0]
        else:
            cursor.execute("INSERT INTO location_table (provincia, comunidad) VALUES (%s, %s)",
                           (row["provincia"], row["comunidad"]))
            conn.commit()
            provincia_id = cursor.lastrowid

        # 🔹 Insertar noticia en la tabla principal con la función cursor.executive().
        
        cursor.execute("""
            INSERT INTO news_info_table 
            (news_id, title, full_story_link, content, category_id, meneos, clicks, karma, positive_votes, 
            anonymous_votes, negative_votes, comments, published_date, scraped_date, 
            user_id, source_id, provincia_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row["news_id"], row["title"], row["full_story_link"], row["content"], category_id, row["meneos"],
            row["clicks"], row["karma"], row["positive_votes"], row["anonymous_votes"],
            row["negative_votes"], row["comments"], row["published_date"], row["scraped_date"],
            user_id, source_id, provincia_id
        ))

        # Confirmar cambios
        
        conn.commit()

    except Exception as e:
        print(f"❌ Error insertando noticia {row['news_id']}: {e}")

#Cerrar conexión

cursor.close()
conn.close()
print("✅ Base de datos poblada exitosamente.")













