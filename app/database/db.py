from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@postgres_db:5432/analytics"

engine = create_engine(DATABASE_URL)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()

def create_tables():
    with engine.connect() as conn:

        conn.execute(text("DROP TABLE IF EXISTS session_observation"))
        conn.execute(text("DROP TABLE IF EXISTS observation"))

        conn.execute(text("""
            CREATE TABLE observation (
                REFOBS_ID TEXT,
                TYPE TEXT,
                REF_START_DATETIME TEXT,
                REF_END_DATETIME TEXT,
                ALONG_TRACK_TIME_OFFSET BIGINT,
                LSAR_SQUINT_TIME_OFFSET BIGINT,
                SSAR_SQUINT_TIME_OFFSET BIGINT,
                LSAR_JOINT_OP_TIME_OFFSET BIGINT,
                SSAR_JOINT_OP_TIME_OFFSET BIGINT,
                PRIORITY TEXT,
                CMD_LSAR_START_DATETIME TEXT,
                CMD_LSAR_END_DATETIME TEXT,
                CMD_SSAR_START_DATETIME TEXT,
                CMD_SSAR_END_DATETIME TEXT,
                LSAR_PATH TEXT,
                SSAR_PATH TEXT,
                LSAR_CONFIG_ID BIGINT,
                SSAR_CONFIG_ID BIGINT,
                DATATAKE_ID TEXT,
                SEGMENT_DATATAKE_ON_SSR TEXT,
                OBS_SUPPORT TEXT,
                INTRODUCED_IN TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE session_observation (
                SESS_ID TEXT,
                REFOBS_ID TEXT
            )
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_session
            ON session_observation(SESS_ID)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_obsid
            ON session_observation(REFOBS_ID)
        """))

        conn.commit()