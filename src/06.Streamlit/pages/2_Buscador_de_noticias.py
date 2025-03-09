import streamlit as st
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

st.title("🔍 Buscador de Noticias")

load_dotenv()

@st.cache_data
def get_data():
    """Retrieve and cache data from the database."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("HOST", "localhost")
    database = "meneame"

    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

    query = """
        SELECT ni.news_id, ni.title, ni.content, u.user, s.source, c.category, 
               l.provincia, l.comunidad, ni.meneos, ni.clicks, ni.karma, ni.comments, 
               ni.positive_votes, ni.negative_votes, ni.anonymous_votes
        FROM news_info_table ni
        LEFT JOIN user_table u ON ni.user_id = u.user_id
        LEFT JOIN source_table s ON ni.source_id = s.source_id
        LEFT JOIN category_table c ON ni.category_id = c.category_id
        LEFT JOIN location_table l ON ni.provincia_id = l.provincia_id
    """
    return pd.read_sql(query, engine)

df = get_data()

# Sidebar filtros
st.sidebar.header("Filter News")

# Search bars filtros
search_news_id = st.sidebar.text_input("Search by News ID")
search_title = st.sidebar.text_input("Search by Title")
search_content = st.sidebar.text_input("Search by Content")
search_user = st.sidebar.text_input("Search by User")
search_source = st.sidebar.text_input("Search by Source")

# Dropdown filtros
category_filter = st.sidebar.selectbox("Category", ["All"] + sorted(df['category'].dropna().unique().tolist()))
province_filter = st.sidebar.selectbox("Province", ["All"] + sorted(df['provincia'].dropna().unique().tolist()))
comunidad_filter = st.sidebar.selectbox("Comunidad", ["All"] + sorted(df['comunidad'].dropna().unique().tolist()))

# Slider filtros para variables numéricas
numeric_filters = {
    "Meneos": "meneos",
    "Clicks": "clicks",
    "Karma": "karma",
    "Comments": "comments",
    "Positive Votes": "positive_votes",
    "Negative Votes": "negative_votes",
    "Anonymous Votes": "anonymous_votes"
}

numeric_ranges = {}
for label, col in numeric_filters.items():
    numeric_ranges[col] = st.sidebar.slider(
        label,
        int(df[col].min()),
        int(df[col].max()),
        (int(df[col].min()), int(df[col].max()))
    )

@st.cache_data
def filter_dataframe(df, search_news_id, search_title, search_content, search_user, search_source,
                      category_filter, province_filter, comunidad_filter, numeric_ranges):
    """Apply filters to the dataframe efficiently."""
    if search_news_id:
        df = df[df['news_id'].astype(str).str.contains(search_news_id, case=False, na=False)]
    if search_title:
        df = df[df['title'].str.contains(search_title, case=False, na=False)]
    if search_content:
        df = df[df['content'].str.contains(search_content, case=False, na=False)]
    if search_user:
        df = df[df['user'].astype(str).str.contains(search_user, case=False, na=False)]
    if search_source:
        df = df[df['source'].astype(str).str.contains(search_source, case=False, na=False)]
    if category_filter != "All":
        df = df[df['category'] == category_filter]
    if province_filter != "All":
        df = df[df['provincia'] == province_filter]
    if comunidad_filter != "All":
        df = df[df['comunidad'] == comunidad_filter]
    
    # Apply numeric filters
    for col, (min_val, max_val) in numeric_ranges.items():
        df = df[(df[col] >= min_val) & (df[col] <= max_val)]

    return df

filtered_df = filter_dataframe(df, search_news_id, search_title, search_content, search_user, search_source,
                               category_filter, province_filter, comunidad_filter, numeric_ranges)

st.write("Filtered News Data:")
st.dataframe(filtered_df)
