import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import math
fffffss
# Configurar la página en modo "wide"
st.set_page_config(layout="wide")

# Página principal (Landing Page)
def landing_page():
    st.title("Página Principal")
    st.write("Bienvenido a la aplicación.")

# Presentación de Datos con subnavegación
def data_presentation():
    st.title("Presentación de Datos")
    st.write("Aquí se muestran filtros, mapas, dashboard y otros gráficos.")
    
    # Subnavegación dentro de 'Presentación de Datos'
    data_option = st.sidebar.radio("Selecciona la sección de datos:", 
                                   ("Gráficos: Clicks vs Karma y Comentarios", "Otra sección"), key="data_section")
    
    if data_option == "Gráficos: Clicks vs Karma y Comentarios":

        user = "root"
        password = "password123"
        database = "meneame"
        engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost/{database}")
        
        def run_query(query):
            with engine.connect() as connection:
                return pd.read_sql(query, connection)
        
        karma_clicks_df = run_query("""
            SELECT l.comunidad, l.provincia, c.category, ni.karma, ni.clicks, ni.comments
            FROM news_info_table ni
            JOIN location_table l ON ni.provincia_id = l.provincia_id
            JOIN category_table c ON c.category_id = ni.category_id;
        """)
        
     # GRAFICO 1
        st.subheader("Clicks vs. karma y Clicks vs. comentarios")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica.")
        
        fig1, axes1 = plt.subplots(1, 2, figsize=(16,8))
        
        sns.scatterplot(data=karma_clicks_df, x="clicks", y="karma", alpha=0.5, ax=axes1[0])
        axes1[0].set_xscale("log")
        axes1[0].set_yscale("log")
        axes1[0].set_xlabel("Clicks")
        axes1[0].set_ylabel("Karma")
        axes1[0].set_title("Scatter Plot: Clicks vs Karma", fontweight="bold")
        
        sns.scatterplot(data=karma_clicks_df, x="clicks", y="comments", alpha=0.5, ax=axes1[1])
        axes1[1].set_xscale("log")
        axes1[1].set_yscale("log")
        axes1[1].set_xlabel("Clicks")
        axes1[1].set_ylabel("Comments")
        axes1[1].set_title("Scatter Plot: Clicks vs Comments", fontweight="bold")
        
        st.pyplot(fig1)
        
    #GRAFICO 2: Segmentado por provincia
        st.subheader("Clicks vs. karma y Clicks vs. comentarios por provincia")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica y segmentados por provincia.")
        
        filtered_df_prov = karma_clicks_df[karma_clicks_df["provincia"] != "Desconocido"]
        
        fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
        
        sns.scatterplot(data=filtered_df_prov, x="clicks", y="karma", hue="provincia", alpha=0.6, palette="tab10", ax=axes2[0])
        axes2[0].set_xscale("log")
        axes2[0].set_yscale("log")
        axes2[0].set_xlabel("Clicks")
        axes2[0].set_ylabel("Karma")
        axes2[0].set_title("Scatter Plot: Clicks vs Karma", fontweight="bold")
        
        sns.scatterplot(data=filtered_df_prov, x="clicks", y="comments", hue="provincia", alpha=0.6, palette="tab10", ax=axes2[1])
        axes2[1].set_xscale("log")
        axes2[1].set_yscale("log")
        axes2[1].set_xlabel("Clicks")
        axes2[1].set_ylabel("Comments")
        axes2[1].set_title("Scatter Plot: Clicks vs Comments", fontweight="bold")
        
        handles, labels = axes2[1].get_legend_handles_labels()
        fig2.legend(handles, labels, title="Provincia", bbox_to_anchor=(1.05, 1), loc="upper left")
        axes2[0].legend_.remove() 
        axes2[1].legend_.remove()
        
        st.pyplot(fig2)
        
    # GRAFICO 3: Segmentado por comunidad
        st.subheader("Clicks vs. karma y Clicks vs. comentarios por comunidad")
        st.write("Gráficos de dispersión que ilustran la relación entre clicks y karma en la parte izquierda, y entre clics y comentarios en la parte derecha, ambos en escala logarítmica y segmentados por comunidad.")
        
        filtered_df_com = karma_clicks_df[karma_clicks_df["comunidad"] != "Desconocido"]
        
        fig3, axes3 = plt.subplots(1, 2, figsize=(14, 6))
        
        sns.scatterplot(data=filtered_df_com, x="clicks", y="karma", hue="comunidad", alpha=0.6, palette="tab10", ax=axes3[0])
        axes3[0].set_xscale("log")
        axes3[0].set_yscale("log")
        axes3[0].set_xlabel("Clicks")
        axes3[0].set_ylabel("Karma")
        axes3[0].set_title("Scatter Plot: Clicks vs Karma", fontweight="bold")
        
        sns.scatterplot(data=filtered_df_com, x="clicks", y="comments", hue="comunidad", alpha=0.6, palette="tab10", ax=axes3[1])
        axes3[1].set_xscale("log")
        axes3[1].set_yscale("log")
        axes3[1].set_xlabel("Clicks")
        axes3[1].set_ylabel("Comments")
        axes3[1].set_title("Scatter Plot: Clicks vs Comments", fontweight="bold")
        
        handles, labels = axes3[1].get_legend_handles_labels()
        fig3.legend(handles, labels, title="Comunidad", bbox_to_anchor=(1.05, 1), loc="upper left")
        axes3[0].legend_.remove() 
        axes3[1].legend_.remove()
        
        st.pyplot(fig3)

    #GRAFICO 4
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


# Vista Detallada
def detailed_view():
    st.title("Vista Detallada")
    st.write("Busca y compara inmuebles.")
    # Aquí podrías incluir formularios de búsqueda y comparación.

# Menú principal en la barra lateral
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Selecciona una vista:", 
                          ("Página Principal", "Presentación de Datos", "Vista Detallada"), key="main_nav")

# Cargar la vista según la selección
if opcion == "Página Principal":
    landing_page()
elif opcion == "Presentación de Datos":
    data_presentation()
elif opcion == "Vista Detallada":
    detailed_view()
