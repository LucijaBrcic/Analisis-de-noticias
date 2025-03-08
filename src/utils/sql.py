import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("HOST", "localhost")
    database = "meneame"

    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
