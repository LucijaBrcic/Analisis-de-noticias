import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime
import os
from dotenv import load_dotenv
import pymysql
import seaborn as sns



#---------------SETTINGS-----------------
page_title = "Análisis de noticias"
page_icon = ":newspaper:"
layout = "wide"
#----------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

#years = [datetime.today().year, datetime.today().year + 1]
#months = list(calendar.month_name[1:])
categories = ["All"] + ["News", "Sports", "Entertainment"]
provinces = ["All"] + ["Province1", "Province2"]

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("HOST", "localhost")
database="meneame"

engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost/{database}")
        
        
def run_query(query):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)
    
# Página principal (Landing Page)

def landing_page():

    st.title("Página Principal")

    df = run_query("""
        SELECT n.news_id, n.title, n.content, c.category, n.meneos, n.clicks, n.karma, n.comments, n.positive_votes, n.anonymous_votes, n.negative_votes, s.source, n.source_link, n.published_date, u.user, l.provincia, l.comunidad 
        FROM news_info_table n
        JOIN category_table c ON n.category_id = c.category_id
        JOIN location_table l ON n.provincia_id = l.provincia_id
        JOIN user_table u ON n.user_id = u.user_id
        JOIN source_table s ON n.source_id = s.source_id
    """)
    st.dataframe(df)
    max_click = df['clicks'].max()
    min_click = df['clicks'].min()

    st.header("Filter data")

    with st.form("entry form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Category:", categories, key="category")
        #col2.selectbox("Select Month:", months, key="month")
        #col3.selectbox("Select Year:", years, key="year")
        col2.selectbox("Select province:", provinces, key="province")

        user_input = st.text_input("Search for user:", key="user")

        clicks_range = st.slider(
            "Select clicks range:",
            min_value=min_click,
            max_value=max_click,
            value=(int(min_click), int(max_click//2)),
            key="clicks_range"
        )

        submitted = st.form_submit_button("Filter")
    
        if submitted:
            st.write("Filtering for user:", user_input)

            #Clicks
            lower_clicks, upper_clicks = clicks_range

            where_clauses = [f"clicks BETWEEN {lower_clicks} AND {upper_clicks}"]

            if selected_category != "All":
                where_clauses.append(f"category = '{selected_category}'")
            if selected_month != "All":
                where_clauses.append(f"month = '{selected_month}'")
            if selected_year != "All":
                where_clauses.append(f"year = '{selected_year}'")
            if selected_province != "All":
                where_clauses.append(f"provincia = '{selected_province}'")
            if user_input:
                where_clauses.append(f"user LIKE '%{user_input}%'")

            where_sql = " AND ".join(where_clauses)

            query = f"""
            SELECT n.news_id, n.title, n.content, c.category, n.meneos, n.clicks, n.karma, n.comments, 
                   n.positive_votes, n.anonymous_votes, n.negative_votes, s.source, n.source_link, 
                   n.published_date, n.scraped_date, u.user, l.provincia, l.comunidad 
            FROM news_info_table n
            JOIN category_table c ON n.category_id = c.category_id
            JOIN location_table l ON n.provincia_id = l.provincia_id
            JOIN user_table u ON n.user_id = u.user_id
            JOIN source_table s ON n.source_id = s.source_id
            WHERE {where_sql}
            """
            
            st.write("SQL Query:")
            st.code(query)
            
            # Execute the query to get only filtered data
            filtered_data = run_query(query)
            st.write("Filtered Data:")
            st.dataframe(filtered_data)

            
#Presentación de Datos con subnavegación, mostrando en varias partes, también mapas Dashboard y demás gráficos.

def data_presentation():
    st.title("Presentación de Datos")
    st.write("Aquí se muestran filtros, mapas, dashboard y otros gráficos.")
    
    #Subnavegación dentro de 'Presentación de Datos' mostrando Cliks vs. Karma y comentarios.
    
    data_option = st.sidebar.radio("Selecciona la sección de datos:", 
                                   ("Gráficos descriptivos", "Gráficos: Clicks vs Karma y Comentarios"), key="data_section")
    
    if data_option == "Gráficos descriptivos":
    #GRAPH 1
        
        df_category = run_query("""
            SELECT c.category, COUNT(n.news_id) AS news_count
            FROM news_info_table n
            JOIN category_table c ON n.category_id = c.category_id
            GROUP BY 1
            ORDER BY 2 DESC;
        """)
        st.subheader("Distribución de varias métricas por categoría con Plotly")

        # List of continuous variables to plot
        continuous_variables = [
            'meneos', 'clicks', 'karma', 'comments', 
            'positive_votes', 'anonymous_votes', 'negative_votes'
        ]

        # Set up subplot grid dimensions (2 columns)
        cols = 2
        rows = math.ceil(len(continuous_variables) / cols)

        # Create a subplot figure with titles for each subplot
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[f"Distribución de {var}" for var in continuous_variables]
        )

        # Loop through each variable and create a boxplot in its subplot
        for i, var in enumerate(continuous_variables):
            # Retrieve data for the given variable per category
            query = run_query(f"""
                SELECT c.category, n.{var}
                FROM news_info_table n
                JOIN category_table c ON n.category_id = c.category_id;
            """)
            
            # Determine subplot position
            row = i // cols + 1
            col = i % cols + 1

            # Get unique categories
            unique_categories = query['category'].unique()
            
            # For each category, add a box trace to the subplot
            for category in unique_categories:
                data = query[query['category'] == category][var]
                fig.add_trace(
                    go.Box(
                        y=data,
                        name=category,
                        boxmean=True,
                        marker=dict(color='lightblue'),
                        showlegend=(i == 0)
                    ),
                    row=row,
                    col=col
                )
            
            # Optionally, update x- and y-axis titles for clarity
            fig.update_xaxes(title_text="Categoría", row=row, col=col)
            fig.update_yaxes(title_text=var, row=row, col=col)

        # Update layout settings for overall figure with larger dimensions
        fig.update_layout(
            height=800 * rows,  # Increase height based on the number of rows
            width=1200,         # Set a wider width
            title_text="Distribución de métricas por categoría",
            boxmode='group'
        )

        # Render the Plotly figure in Streamlit using the container's width
        st.plotly_chart(fig, use_container_width=True)




        st.subheader("Numero de noticias por categoria")
        
        ax = df_category.plot(kind='bar',x='category', y='news_count', legend=False, figsize=(6,4))
        fig = ax.get_figure()
        st.pyplot(fig)

        st.subheader("Promedio de varias metricas por categoria")
        def barplot(ax, var):
            query = run_query(f"SELECT c.category, AVG(n.{var}) AS average_{var} FROM news_info_table n JOIN category_table c ON n.category_id = c.category_id GROUP BY n.category_id ORDER BY 2 DESC;")

            query.set_index("category", inplace=True)

            query.plot(kind='bar', color='royalblue', edgecolor='black', alpha=0.8, ax=ax, legend=False)

            ax.set_title(f"Promedio de {var} por categoría", fontsize=12, fontweight='bold')
            ax.set_xlabel("Categoría", fontsize=10)
            ax.set_ylabel(f"Promedio de {var}", fontsize=10)
            ax.tick_params(axis='x', rotation=90)

        continuous_variables = ['meneos', 'clicks', 'karma', 'comments', 'positive_votes', 'anonymous_votes', 'negative_votes']

        cols = 2
        rows = math.ceil(len(continuous_variables) / cols)

        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))

        axes = axes.flatten()

        for i, var in enumerate(continuous_variables):
            barplot(axes[i], var)

        for j in range(i+1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        st.pyplot(fig)
        
    if data_option == "Gráficos: Clicks vs Karma y Comentarios":


        
        karma_clicks_df = run_query("""
            SELECT l.comunidad, l.provincia, c.category, ni.karma, ni.clicks, ni.comments
            FROM news_info_table ni
            JOIN location_table l ON ni.provincia_id = l.provincia_id
            JOIN category_table c ON c.category_id = ni.category_id;
        """)
        
     #GRAFICO 1  Cliks vs Karma y Clicks vs. Comentarios.
        
        st.subheader("Clicks vs. karma y Clicks vs. comentarios")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica.")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        sns.scatterplot(data=karma_clicks_df, x="clicks", y="karma", alpha=0.5, ax=axes[0])
        axes[0].set_xscale("log")
        axes[0].set_yscale("log")
        axes[0].set_xlabel("Clicks")
        axes[0].set_ylabel("Karma")
        axes[0].set_title("Scatter Plot: Clicks vs Karma")

        sns.scatterplot(data=karma_clicks_df, x="clicks", y="comments", alpha=0.5, ax=axes[1])
        axes[1].set_xscale("log")
        axes[1].set_yscale("log")
        axes[1].set_xlabel("Clicks")
        axes[1].set_ylabel("Comments")
        axes[1].set_title("Scatter Plot: Clicks vs Comments")

        st.pyplot(fig)
        
    #GRAFICO 2: Segmentado por provincia Clicks vs. Comentarios por provincia.
        
        st.subheader("Clicks vs. karma y Clicks vs. comentarios por provincia")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica y segmentados por provincia.")
        
        filtered_df = karma_clicks_df[karma_clicks_df["provincia"] != "Desconocido"]

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        sns.scatterplot(data=filtered_df, x="clicks", y="karma", hue="provincia", alpha=0.6, palette="tab10", ax=axes[0])
        axes[0].set_xscale("log") 
        axes[0].set_yscale("log")
        axes[0].set_xlabel("Clicks")
        axes[0].set_ylabel("Karma")
        axes[0].set_title("Scatter Plot: Clicks vs Karma")

        sns.scatterplot(data=filtered_df, x="clicks", y="comments", hue="provincia", alpha=0.6, palette="tab10", ax=axes[1])
        axes[1].set_xscale("log")
        axes[1].set_yscale("log")
        axes[1].set_xlabel("Clicks")
        axes[1].set_ylabel("Comments")
        axes[1].set_title("Scatter Plot: Clicks vs Comments")

        handles, labels = axes[1].get_legend_handles_labels()
        fig.legend(handles, labels, title="Provincia", bbox_to_anchor=(1.05, 1), loc="upper left")
        axes[0].legend_.remove() 
        axes[1].legend_.remove()
        
        st.pyplot(fig)
        
    #GRAFICO 3: Segmentado por comunidad Clicks vs. Karma y Clicks vs. Comentarios.
        
        st.subheader("Clicks vs. karma y Clicks vs. comentarios por comunidad")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica y segmentados por comunidad.")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        sns.scatterplot(data=filtered_df, x="clicks", y="karma", hue="comunidad", alpha=0.6, palette="tab10", ax=axes[0])
        axes[0].set_xscale("log") 
        axes[0].set_yscale("log")
        axes[0].set_xlabel("Clicks")
        axes[0].set_ylabel("Karma")
        axes[0].set_title("Scatter Plot: Clicks vs Karma")

        sns.scatterplot(data=filtered_df, x="clicks", y="comments", hue="comunidad", alpha=0.6, palette="tab10", ax=axes[1])
        axes[1].set_xscale("log")
        axes[1].set_yscale("log")
        axes[1].set_xlabel("Clicks")
        axes[1].set_ylabel("Comments")
        axes[1].set_title("Scatter Plot: Clicks vs Comments")

        handles, labels = axes[1].get_legend_handles_labels()
        fig.legend(handles, labels, title="Comunidad", bbox_to_anchor=(1.05, 1), loc="upper left")
        axes[0].legend_.remove() 
        axes[1].legend_.remove()
        
        st.pyplot(fig)

    #GRAFICO 4 Cliks vs Karma y Cliks vs. y Cliks vs. Comentarios por Categoría.
        
        st.subheader("Clicks vs. karma y Clicks vs. comentarios por categoria")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica y segmentados por categoria.")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        sns.scatterplot(data=karma_clicks_df, x="clicks", y="karma", hue="category", alpha=0.6, palette="tab10", ax=axes[0])
        axes[0].set_xscale("log") 
        axes[0].set_yscale("log")
        axes[0].set_xlabel("Clicks")
        axes[0].set_ylabel("Karma")
        axes[0].set_title("Scatter Plot: Clicks vs Karma")

        sns.scatterplot(data=karma_clicks_df, x="clicks", y="comments", hue="category", alpha=0.6, palette="tab10", ax=axes[1])
        axes[1].set_xscale("log")
        axes[1].set_yscale("log")
        axes[1].set_xlabel("Clicks")
        axes[1].set_ylabel("Comments")
        axes[1].set_title("Scatter Plot: Clicks vs Comments")

        handles, labels = axes[1].get_legend_handles_labels()
        fig.legend(handles, labels, title="Category", bbox_to_anchor=(1.05, 1), loc="upper left")
        axes[0].legend_.remove() 
        axes[1].legend_.remove()

        st.pyplot(fig)

    else:
        st.write("Sección no disponible aún.")

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))


#Vista Detallada en tres "Vista Detallada, Busca y compara inmuebles".

def detailed_view():
    st.title("Vista Detallada")
    st.write("Busca y compara inmuebles.")
    # Aquí podrías incluir formularios de búsqueda y comparación.

#Menú principal en la barra lateral en 3 parte "Pagina Principal, Presentación de datos, Vista detallada".

st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Selecciona una vista:", 
                          ("Página Principal", "Presentación de Datos", "Vista Detallada", "Comparador de Fuentes", "Predicciones"), key="main_nav")

#Cargar la vista según la selección



# Crear las métricas
def calcular_metricas_comparaciones(df):
    # Número total de noticias por fuente
    total_news_by_source = df['source'].value_counts().reset_index()
    total_news_by_source.columns = ['source', 'total_news']

    # Frecuencia de publicación (noticias por día)
    df['date'] = df['published_date'].dt.date
    news_per_day = df.groupby(['source', 'date']).size().reset_index(name='news_per_day')
    avg_news_per_day = news_per_day.groupby('source')['news_per_day'].mean().reset_index()

    # Aceptación de las noticias (karma promedio por fuente)
    avg_karma_by_source = df.groupby('source')['karma'].mean().reset_index()

    # Engagement (comentarios y clicks promedio por fuente)
    avg_comments_by_source = df.groupby('source')['comments'].mean().reset_index()
    avg_clicks_by_source = df.groupby('source')['clicks'].mean().reset_index()

    return {
        'total_news': total_news_by_source,
        'avg_news_per_day': avg_news_per_day,
        'avg_karma': avg_karma_by_source,
        'avg_comments': avg_comments_by_source,
        'avg_clicks': avg_clicks_by_source
    }


def source_comparison():
    # Cargar las tablas
    news_info = run_query("SELECT * FROM news_info_table")
    source_table = run_query("SELECT * FROM source_table")

    # Unir las tablas en base a source_id
    df = pd.merge(news_info, source_table, on='source_id')

    # Convertir la fecha a datetime
    df['published_date'] = pd.to_datetime(df['published_date'])

    # Calcular todas las métricas
    metricas = calcular_metricas_comparaciones(df)

    # Título de la aplicación
    st.title('Comparador de Fuentes de Noticias')

    # Selectbox para elegir la métrica
    opciones = {
        'Número total de noticias': 'total_news',
        'Frecuencia de publicación (noticias por día)': 'avg_news_per_day',
        'Aceptación de las noticias (karma promedio)': 'avg_karma',
        'Engagement (comentarios promedio)': 'avg_comments',
        'Engagement (clicks promedio)': 'avg_clicks'
    }

    seleccion = st.selectbox(
        'Selecciona una métrica para comparar:',
        list(opciones.keys())
    )

    # Seleccionar la métrica correspondiente
    metrica_seleccionada = opciones[seleccion]
    datos_metricas = metricas[metrica_seleccionada]

    # Ordenar los datos según la métrica seleccionada
    datos_metricas = datos_metricas.nlargest(10, datos_metricas.columns[1])

    # Mostrar el gráfico
    st.header(f'{seleccion} - TOP 10')
    st.bar_chart(datos_metricas.set_index('source'))


def predictions():
    # Cargar el modelo entrenado
    model = joblib.load('src/03_01.ML/modelo_entrenado_mejorado.pkl')

    # Título de la aplicación
    st.title('Predicción de Clicks en Noticias')

    # Cargar datos (puedes cargarlos desde un archivo o desde la base de datos)
    # Aquí asumimos que tienes un archivo CSV con los datos
    st.write("Tenemos un fichero de ejemplo en la carpeta 04.Streamlit llamado sample_uploadcsv_to_predict.csv")

    uploaded_file = st.file_uploader("Sube un archivo CSV con los datos", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Mostrar los datos cargados
        st.write("Datos cargados:")
        st.write(df)

        # Seleccionar características relevantes (deben coincidir con las usadas en el entrenamiento)
        features = ['category_id', 'meneos', 'karma', 'positive_votes', 'negative_votes', 'comments', 'day_of_week', 'month', 'year', 'votes_ratio', 'votes_diff', 'interaction']
        df_selected = df[features]

        # Realizar predicciones
        predictions = model.predict(df_selected)

        # Añadir las predicciones al DataFrame
        df['predicted_clicks'] = predictions

        # Mostrar las predicciones
        st.write("Predicciones de Clicks:")
        st.write(df[['category_id', 'meneos', 'karma', 'predicted_clicks']])

        # Gráfico de predicciones vs valores reales (si tienes los valores reales)
        if 'clicks' in df.columns:
            st.write("Gráfico de Predicciones vs Valores Reales:")
            fig, ax = plt.subplots()
            sns.scatterplot(x=df['clicks'], y=df['predicted_clicks'], ax=ax)
            ax.set_xlabel('Clicks Reales')
            ax.set_ylabel('Clicks Predichos')
            ax.set_title('Predicciones vs Valores Reales')
            st.pyplot(fig)

        # Gráfico de distribución de predicciones
        st.write("Distribución de Predicciones de Clicks:")
        fig, ax = plt.subplots()
        sns.histplot(df['predicted_clicks'], kde=True, ax=ax)
        ax.set_xlabel('Clicks Predichos')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Distribución de Predicciones de Clicks')
        st.pyplot(fig)

        # Gráfico de predicciones por categoría
        st.write("Predicciones de Clicks por Categoría:")
        fig, ax = plt.subplots()
        sns.boxplot(x='category_id', y='predicted_clicks', data=df, ax=ax)
        ax.set_xlabel('Categoría')
        ax.set_ylabel('Clicks Predichos')
        ax.set_title('Predicciones de Clicks por Categoría')
        st.pyplot(fig)

    else:
        st.write("Por favor, sube un archivo CSV para comenzar.")


if opcion == "Página Principal":
    landing_page()
elif opcion == "Presentación de Datos":
    data_presentation()
elif opcion == "Vista Detallada":
    detailed_view()
elif opcion == "Comparador de Fuentes":
    source_comparison()
elif opcion == "Predicciones":
    predictions()
