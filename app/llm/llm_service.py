import requests
from datetime import datetime

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "deepseek-coder:1.3b"

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


import requests
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_sql(question: str) -> str:
    """
    Generate a safe PostgreSQL SELECT query from natural language using local LLM.
    Returns a validated SQL statement.
    """

    prompt = f"""
You are a world-class PostgreSQL SQL generator.

Your job is to convert natural language questions into SQL queries.

====================
DATABASE SCHEMA
====================

{SCHEMA_DESCRIPTION}

====================
RULES
====================

1. Generate ONLY one SQL query.
2. The query MUST start with SELECT.
3. The query MUST end with a semicolon.
4. Do NOT include explanations.
5. Do NOT include comments.
6. Do NOT include markdown formatting.
7. Only use tables and columns from the schema.
8. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
9. If the question asks "how many" or "count", use COUNT(*) and DO NOT use LIMIT.
10. If the question asks for latest rows, order by REF_START_DATETIME DESC.
11. If user specifies number of rows (example: 5, 10), use LIMIT.
12. If user says "ordered by", do not assume ASC or DESC unless specified.
IMPORTANT RULE:
If the question asks "how many" or "count", generate:
SELECT COUNT(*) FROM observation;
Do NOT use LIMIT.

====================
EXAMPLES
====================

User: How many observations are there?
SQL:
SELECT COUNT(*) FROM observation;

User: Show all joint observations
SQL:
SELECT * FROM observation WHERE TYPE = 'joint';

User: Show latest 5 observations
SQL:
SELECT *
FROM observation
ORDER BY REF_START_DATETIME DESC
LIMIT 5;

User: Count observations by TYPE
SQL:
SELECT TYPE, COUNT(*)
FROM observation
GROUP BY TYPE;

====================
TASK
====================

User Question:
{question}

SQL:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 120
                }
            },
            timeout=120
        )

        if response.status_code != 200:
            raise Exception("LLM request failed")

        raw_output = response.json()["response"].strip()
        logger.info("LLM RAW OUTPUT: %s", raw_output)

    except Exception as e:
        logger.error("LLM call failed: %s", str(e))
        raise

    # --------------------------------
    # Remove markdown blocks
    # --------------------------------
    cleaned = re.sub(r"```.*?```", "", raw_output, flags=re.DOTALL).strip()

    # --------------------------------
    # Remove common prefixes
    # --------------------------------
    cleaned = re.sub(r"(?i)sql\s*statement\s*:", "", cleaned)
    cleaned = re.sub(r"(?i)here\s+is\s+the\s+sql\s*:", "", cleaned)
    cleaned = cleaned.strip()

    # --------------------------------
    # Extract SQL query
    # --------------------------------
    match = re.search(r"select\s+.*?;", cleaned, re.IGNORECASE | re.DOTALL)

    if match:
        sql = match.group(0).strip()
    else:
        match = re.search(r"select\s+.*", cleaned, re.IGNORECASE | re.DOTALL)
        if not match:
            raise Exception("Invalid SQL generated")

        sql = match.group(0).strip()

        if not sql.endswith(";"):
            sql += ";"

    sql_lower = sql.lower()

    # --------------------------------
    # Remove LIMIT from COUNT queries
    # --------------------------------
    if "count(" in sql_lower:
        sql = re.sub(r"\s+limit\s+\d+", "", sql, flags=re.IGNORECASE)

    # --------------------------------
    # Security checks
    # --------------------------------
    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create"
    ]

    if any(keyword in sql_lower for keyword in forbidden_keywords):
        raise Exception("Dangerous SQL detected")

    if not sql_lower.startswith("select"):
        raise Exception("Only SELECT queries are allowed")

    # --------------------------------
    # Normalize whitespace
    # --------------------------------
    sql = re.sub(r"\s+", " ", sql).strip()

    return sql