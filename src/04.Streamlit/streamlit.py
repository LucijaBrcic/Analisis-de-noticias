import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import math

# Configurar la página en modo "wide" mejorando tanto en dato como en gráficos la visualización en streamlit.

st.set_page_config(layout="wide")


user = "root"
password = "password123"
database = "meneame"
engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost/{database}")
        
#Función para conectar con la base de datos SQL y pode así hacer la selección desde las tablas, haciendo un join con la localización_table, y category_table.
        
def run_query(query):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)
    
# Página principal (Landing Page)

def landing_page():
    st.title("Página Principal")
    st.write("Bienvenido a la aplicación.")

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
                          ("Página Principal", "Presentación de Datos", "Vista Detallada"), key="main_nav")

#Cargar la vista según la selección

if opcion == "Página Principal":
    landing_page()
elif opcion == "Presentación de Datos":
    data_presentation()
elif opcion == "Vista Detallada":
    detailed_view()
