import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text 

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Database environment variables are not properly set")

def build_db_url():

    # Try PostgreSQL
    try:
        url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected using PostgreSQL")
        return url
    except:
        pass

    # Try MySQL
    try:
        url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected using MySQL")
        return url
    except:
        pass

    # Try SQLite (file-based)
    try:
        url = f"sqlite:///{DB_NAME}"
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected using SQLite")
        return url
    except:
        pass

    raise Exception("Could not connect to any supported database")

DATABASE_URL = build_db_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()