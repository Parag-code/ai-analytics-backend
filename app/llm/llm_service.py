import requests
from datetime import datetime

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "tinyllama"

SCHEMA_DESCRIPTION = """
Database Schema:

Table: observation
Columns:
- REFOBS_ID (text)
- TYPE (text)
- REF_START_DATETIME (text)
- REF_END_DATETIME (text)
- ALONG_TRACK_TIME_OFFSET (bigint)
- LSAR_SQUINT_TIME_OFFSET (bigint)
- SSAR_SQUINT_TIME_OFFSET (bigint)
- LSAR_JOINT_OP_TIME_OFFSET (bigint)
- SSAR_JOINT_OP_TIME_OFFSET (bigint)
- PRIORITY (text)
- CMD_LSAR_START_DATETIME (text)
- CMD_LSAR_END_DATETIME (text)
- CMD_SSAR_START_DATETIME (text)
- CMD_SSAR_END_DATETIME (text)
- LSAR_PATH (text)
- SSAR_PATH (text)
- LSAR_CONFIG_ID (integer)
- SSAR_CONFIG_ID (integer)
- DATATAKE_ID (text)
- SEGMENT_DATATAKE_ON_SSR (text)
- OBS_SUPPORT (text)
- INTRODUCED_IN (text)

Table: session_observation
Columns:
- SESS_ID (text)
- REFOBS_ID (text)

Important:
REF_START_DATETIME format example:
2026-047T04:58:00.8437897
"""


def generate_sql(question: str) -> str:
    """
    Generates SQL query from natural language using local LLM.
    """

    today = datetime.utcnow().strftime("%Y-%m-%d")

    prompt = f"""
You are an expert PostgreSQL SQL generator.

{SCHEMA_DESCRIPTION}

Examples:

User: How many observations are there?
SQL: SELECT COUNT(*) FROM observation;

User: Show all joint type observations
SQL: SELECT * FROM observation WHERE TYPE = 'joint';

User: Count observations grouped by TYPE
SQL: SELECT TYPE, COUNT(*) FROM observation GROUP BY TYPE;

STRICT RULES:
- Output ONLY SQL
- Output ONE SELECT statement
- NO explanation
- NO markdown
- MUST start with SELECT
- MUST end with semicolon
- NEVER use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE

User: {question}
SQL:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        raise Exception("LLM request failed")

    sql = response.json()["response"].strip()

# Remove markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()

# Extract only first SELECT statement
    import re
    match = re.search(r"select .*?;", sql, re.IGNORECASE | re.DOTALL)
    if match:
      sql = match.group(0).strip()
    else:
      raise Exception("Invalid SQL generated")

    return sql