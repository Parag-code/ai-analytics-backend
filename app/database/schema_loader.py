from sqlalchemy import inspect
from database.db import engine

SCHEMA_CACHE = None

def load_schema():
    """
    Universal schema loader (PostgreSQL, MySQL, SQLite)
    """

    global SCHEMA_CACHE

    if SCHEMA_CACHE is not None:
        return SCHEMA_CACHE

    print("Loading schema from database...")

    schema = {}

    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        for table in tables:
            columns = inspector.get_columns(table)
            schema[table] = [col["name"] for col in columns]

        if not schema:
            raise Exception("No tables found in database")

        SCHEMA_CACHE = schema
        return SCHEMA_CACHE

    except Exception as e:
        raise Exception(f"Schema loading failed: {str(e)}")