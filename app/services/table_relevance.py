from sqlalchemy import text
from database.db import engine

TABLE_CACHE = None


def get_all_tables():

    global TABLE_CACHE

    if TABLE_CACHE is not None:
        return TABLE_CACHE

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        TABLE_CACHE = [row.table_name for row in result]

    return TABLE_CACHE


def detect_relevant_tables(question: str):

    question = question.lower()

    tables = get_all_tables()

    relevant_tables = []

    for table in tables:

        words = table.split("_")

        for word in words:
            if word in question:
                relevant_tables.append(table)
                break

    if not relevant_tables:
        return tables

    return relevant_tables