from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@postgres_db:5432/analytics"

engine = create_engine(DATABASE_URL)


def execute_query(sql: str):
    """
    Execute SQL query and return results as list of dicts
    """

    with engine.connect() as conn:
        result = conn.execute(text(sql))

        rows = [dict(row._mapping) for row in result]

    return rows