from sqlalchemy import text
from database.db import engine

SCHEMA_CACHE = None


def load_schema():
    """
    Load database schema dynamically and cache it
    """

    global SCHEMA_CACHE

    if SCHEMA_CACHE is not None:
        return SCHEMA_CACHE

    print("Loading schema from database...")

    query = """
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """

    schema = {}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))

            for row in result:
                table = row.table_name
                column = row.column_name

                if table not in schema:
                    schema[table] = []

                schema[table].append(column)

        SCHEMA_CACHE = schema

        return SCHEMA_CACHE

    except Exception as e:
        raise Exception(f"Schema loading failed: {str(e)}")