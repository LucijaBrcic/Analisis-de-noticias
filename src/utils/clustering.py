import os
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

class Clustering:
    def __init__(self):
        self.df = self.load_data()
        self.df_clustering = self.df[['news_id', 'meneos', 'clicks', 'karma', 'positive_votes', 'negative_votes', 'anonymous_votes', 'comments', 'category']]
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

        return fig  # 🔹 Return the figure instead of plt.show()


    def apply_kmeans(self, n_clusters):
        kmeans = KMeans(n_clusters=n_clusters, init="k-means++", max_iter=300, n_init=10, random_state=42)
        labels = kmeans.fit_predict(self.df_scaled)
        self.df_numeric[f"cluster_{n_clusters}"] = labels
        self.df_clustering[f"cluster_{n_clusters}"] = labels
        return labels

    def plot_mean_barplot(self, n_clusters):
        if f"cluster_{n_clusters}" not in self.df_numeric.columns:
            self.apply_kmeans(n_clusters)
        
        columns_to_plot = ['karma', 'clicks', 'negative_votes', 'positive_votes', 'anonymous_votes', 'meneos', 'comments']
        
        df_means = self.df_numeric.groupby(f"cluster_{n_clusters}")[columns_to_plot].mean()
        df_means.T.plot(kind='bar', figsize=(15, 10), legend=True)
        
        plt.title(f"Mean of Each Numeric Variable by Cluster ({n_clusters} Clusters)")
        plt.xlabel("Variables")
        plt.ylabel("Mean Value")
        plt.xticks(rotation=45)
        plt.legend(title="Cluster")
        plt.show()

    def plot_heatmap(self, n_clusters):
        if f"cluster_{n_clusters}" not in self.df_numeric.columns:
            self.apply_kmeans(n_clusters)

        cluster_names = {
            0: "Noticias bien recibidas",
            1: "Noticias polémicas",
            2: "Noticias estándar"
        }

        # Correct grouping: categories as index (Y-axis), clusters as columns (X-axis)
        cluster_category_counts = self.df_numeric.join(self.df['category']).groupby(["category", f"cluster_{n_clusters}"], observed=True).size().unstack()

        # Normalize percentages per category (row-wise)
        cluster_category_pct = cluster_category_counts.div(cluster_category_counts.sum(axis=1), axis=0) * 100

        # Rename cluster columns using cluster names
        cluster_category_pct.columns = cluster_category_pct.columns.map(lambda x: cluster_names.get(x, f"Cluster {x}"))

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(cluster_category_pct, cmap="coolwarm", annot=True, fmt=".1f", linewidths=0.5, ax=ax)

        ax.set_title("Distribución de Categorías por Cluster (%)")
        ax.set_ylabel("Categoría")  # ✅ Categories should be on Y-axis
        ax.set_xlabel("Cluster")  # ✅ Clusters should be on X-axis
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()

        return fig  # ✅ Return figure for Streamlit            
