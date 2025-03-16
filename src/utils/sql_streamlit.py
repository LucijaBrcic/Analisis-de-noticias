import streamlit as st
import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

class DataProcessor:
    def __init__(self, engine):
        self.engine = engine

    def get_existing_mapping(self, table_name, id_col, name_col):
        query = f"SELECT {id_col}, {name_col} FROM {table_name}"
        existing_data = pd.read_sql(query, self.engine)
        return dict(zip(existing_data[name_col], existing_data[id_col]))

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