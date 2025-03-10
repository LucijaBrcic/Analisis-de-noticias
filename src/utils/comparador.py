import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class ComparadorNoticias:
    def __init__(self):
        load_dotenv()
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("HOST", "localhost")
        self.database = "meneame"
        self.engine = self.get_engine()

    def get_engine(self):
        return create_engine(f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}")

    def get_data(self, news_ids=None, category=None):
        if news_ids:
            query = f"""
                SELECT news_id, clicks, comments, karma, positive_votes, anonymous_votes, negative_votes
                FROM news_info_table
                WHERE news_id IN ({','.join(map(str, news_ids))})
            """
        elif category:
            query = f"""
                SELECT c.category, 
                       AVG(n.clicks) AS clicks, 
                       AVG(n.comments) AS comments, 
                       AVG(n.karma) AS karma,
                       AVG(n.positive_votes) AS positive_votes, 
                       AVG(n.anonymous_votes) AS anonymous_votes,
                       AVG(n.negative_votes) AS negative_votes
                FROM news_info_table n
                JOIN category_table c ON n.category_id = c.category_id
                WHERE c.category = '{category}'
                GROUP BY c.category;
            """
        else:
            raise ValueError("Debe proporcionar news_ids o una categoría.")
        
        return pd.read_sql(query, self.engine)

    def get_max_values(self):
        query = """
            SELECT MAX(clicks) AS clicks, MAX(comments) AS comments, MAX(karma) AS karma,
                   MAX(positive_votes) AS positive_votes, MAX(anonymous_votes) AS anonymous_votes,
                   MAX(negative_votes) AS negative_votes
            FROM news_info_table
        """
        return pd.read_sql(query, self.engine).iloc[0]

    def normalize_values(self, values, max_values, variables):
        return [val / max_values[var] if max_values[var] > 0 else 0 for val, var in zip(values, variables)]

    def plot_comparison_plotly(self, data1, label1, data2, label2, variables, values1, values2):
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=data1 + [data1[0]],  
            theta=variables + [variables[0]],  
            fill='toself',
            name=label1,
            text=values1,  
            hoverinfo='text',  
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatterpolar(
            r=data2 + [data2[0]],  
            theta=variables + [variables[0]],  
            fill='toself',
            name=label2,
            text=values2,  
            hoverinfo='text',  
            line=dict(color='red', width=2)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                ),
            ),
            showlegend=True,
            title="Comparación de métricas",
            width=800,
            height=800
        )
        fig.show()

    def comparar(self, entidad1, entidad2, tipo='noticia'):
        max_values = self.get_max_values()
        variables = ["clicks", "comments", "karma", "positive_votes", "anonymous_votes", "negative_votes"]

        if tipo == "noticia":
            df_news_ids = self.get_data(news_ids=[entidad1, entidad2])

            if df_news_ids.empty or len(df_news_ids) < 2:
                raise ValueError("Una o ambas noticias no existen en la base de datos.")

            data1 = self.normalize_values(df_news_ids.iloc[0][variables], max_values, variables)
            data2 = self.normalize_values(df_news_ids.iloc[1][variables], max_values, variables)

            values1 = df_news_ids.iloc[0][variables].values.tolist()
            values2 = df_news_ids.iloc[1][variables].values.tolist()

            self.plot_comparison_plotly(data1, f'Noticia {entidad1}', data2, f'Noticia {entidad2}', variables, values1, values2)

        elif tipo == "categoria":
            df1 = self.get_data(category=entidad1)
            df2 = self.get_data(category=entidad2)

            if df1.empty or df2.empty:
                raise ValueError("Una de las categorías no tiene datos disponibles.")

            data1 = self.normalize_values(df1.iloc[0][variables], max_values, variables)
            data2 = self.normalize_values(df2.iloc[0][variables], max_values, variables)

            values1 = df1.iloc[0][variables].values.tolist()
            values2 = df2.iloc[0][variables].values.tolist()

            self.plot_comparison_plotly(data1, f'Categoría {entidad1}', data2, f'Categoría {entidad2}', variables, values1, values2)
        
        else:
            raise ValueError("El tipo debe ser 'noticia' o 'categoria'.")
