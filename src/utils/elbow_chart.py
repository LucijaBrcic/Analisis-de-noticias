import os
import numpy as np
import pandas as pd 
import pickle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

class ElbowChart:
    def __init__(self):
        self.df = self.load_data()
        self.df_numeric = self.df[['meneos', 'clicks', 'karma', 'positive_votes', 'negative_votes', 'anonymous_votes', 'comments']]
        self.scaler = MinMaxScaler()
        self.df_scaled = self.scaler.fit_transform(self.df_numeric)

    def load_data(self):
        directorio_base = os.path.abspath(os.path.join(os.getcwd(), "../.."))
        directorio_pkl = os.path.join(directorio_base, "src", "00.data", "preprocesado")

        if not os.path.exists(directorio_pkl):
            raise FileNotFoundError(f"El directorio no existe: {directorio_pkl}")

        archivos_pkl = [f for f in os.listdir(directorio_pkl) if f.startswith("meneame_procesado_") and f.endswith(".pkl")]

        if not archivos_pkl:
            raise ValueError("No se encontraron archivos .pkl en el directorio.")

        df_lista = []

        for archivo in archivos_pkl:
            ruta_archivo = os.path.join(directorio_pkl, archivo)
            try:
                with open(ruta_archivo, "rb") as f:
                    df_lista.append(pickle.load(f))
            except Exception as e:
                print(f"Error al cargar {archivo}: {e}")

        if df_lista:
            df = pd.concat(df_lista, ignore_index=True)
            df = df[df["clicks"].notna()]
            return df
        else:
            raise ValueError("No se cargaron DataFrames.")

    def generate_elbow_chart(self, max_clusters=10):
        os.environ["LOKY_MAX_CPU_COUNT"] = "4"

        wcss = []

        for i in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=i, init="k-means++", max_iter=300, n_init=10, random_state=42)
            kmeans.fit(self.df_scaled)
            wcss.append(kmeans.inertia_)

        fig, ax = plt.subplots()
        ax.plot(range(1, max_clusters + 1), wcss, marker='o')
        ax.set_title('The Elbow Method')
        ax.set_xlabel('Number of Clusters')
        ax.set_ylabel('WCSS')

        return fig
