import streamlit as st
import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.sql import text

class DataProcessor:
    def __init__(self, engine):
        self.engine = engine

    def check_existing_news(self, df):
        """Check which news IDs already exist in the database."""
        news_ids = tuple(df["news_id"].unique())  # Get unique news IDs from dataframe
        if not news_ids:  # If no news in dataframe, return empty set
            return set()
        
        query = text(f"SELECT news_id FROM news_info_table WHERE news_id IN :news_ids")
        with self.engine.connect() as connection:
            existing_news = connection.execute(query, {"news_ids": news_ids}).fetchall()
        
        return {row[0] for row in existing_news}  # Convert result to set of existing news IDs

    def insert_data(self, df):
        """Insert only new news into SQL, skipping duplicates."""
        existing_news_ids = self.check_existing_news(df)  # Get existing news from DB

        df_new = df[~df["news_id"].isin(existing_news_ids)]  # Filter out already existing news

        if df_new.empty:
            st.warning("⚠️ No hay nuevas noticias. Todos los datos ya existen en la base de datos.")
            return

        df_new.to_sql("news_info_table", self.engine, if_exists="append", index=False, method="multi")
        st.success(f"✅ {len(df_new)} nuevas noticias insertadas correctamente en la base de datos.")


    # we are getting mapping of category-category_id, user_user_id etc. to map the new data
    def get_existing_mapping(self, table_name, id_col, name_col):
        query = f"SELECT {id_col}, {name_col} FROM {table_name}"
        existing_data = pd.read_sql(query, self.engine)
        return dict(zip(existing_data[name_col], existing_data[id_col]))

    # in case there is a new instance of e.g. user, province, source, it assigns it the next biggest number
    def get_next_id(self, table_name, id_col):
        query = f"SELECT MAX({id_col}) FROM {table_name}"
        max_id = pd.read_sql(query, self.engine).iloc[0, 0]
        return 1 if pd.isna(max_id) else max_id + 1


    def process_column(self, df, column_name, table_name, id_col, name_col):
        mapping = self.get_existing_mapping(table_name, id_col, name_col)
        df[f"{id_col}"] = df[column_name].map(mapping)

        new_values = df[df[f"{id_col}"].isna()][column_name].unique()
        if len(new_values) > 0:
            st.write(f"{len(new_values)} nuevos valores detectados en {table_name}. Creando IDs...")

            next_id = self.get_next_id(table_name, id_col)
            new_ids = list(range(next_id, next_id + len(new_values)))

            new_data = pd.DataFrame({name_col: new_values, id_col: new_ids})
            new_data.to_sql(table_name, self.engine, if_exists="append", index=False)

            df = df.merge(new_data, on=column_name, how="left")
            df[f"{id_col}"] = df[f"{id_col}_x"].fillna(df[f"{id_col}_y"]).astype(int)
            df = df.drop(columns=[f"{id_col}_x", f"{id_col}_y", column_name], errors="ignore")

        return df

    def process_dataframe(self, df):
        
        df = self.process_column(df, "user", "user_table", "user_id", "user")
        df = self.process_column(df, "source", "source_table", "source_id", "source")
        df = self.process_column(df, "category", "category_table", "category_id", "category")
        df = self.process_column(df, "provincia", "location_table", "provincia_id", "provincia")

        return df

    def insert_data(self, df):
        df.to_sql("news_info_table", self.engine, if_exists="append", index=False)
        st.success("✅ **Datos enviados correctamente a la base de datos.**")