import requests
from datetime import datetime

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "codellama:7b-instruct"

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
from datetime import datetime


def generate_sql(question: str) -> str:
    """
    Generates a safe PostgreSQL SELECT query from natural language using local LLM.
    Returns only validated SQL.
    """

    prompt = f"""
You are an expert PostgreSQL SQL generator.

{SCHEMA_DESCRIPTION}

STRICT RULES:
- Respond with ONLY a single raw SQL SELECT statement.
- No explanation.
- No comments.
- No markdown.
- Must start with SELECT.
- Must end with a semicolon.
- Only use tables and columns defined in schema.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.

User Question:
{question}

SQL:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0  # makes SQL deterministic
        }
    )

    if response.status_code != 200:
        raise Exception("LLM request failed")

    raw_output = response.json()["response"].strip()

    # -------------------------
    # 1. Remove markdown blocks
    # -------------------------
    cleaned = re.sub(r"```.*?```", "", raw_output, flags=re.DOTALL).strip()

    # -------------------------
    # 2. Extract first SELECT statement
    # -------------------------
    match = re.search(r"(SELECT[\s\S]*?;)", cleaned, re.IGNORECASE)

    if match:
        sql = match.group(1).strip()
    else:
        # Handle missing semicolon
        match = re.search(r"(SELECT[\s\S]*)", cleaned, re.IGNORECASE)
        if match:
            sql = match.group(1).strip()
            if not sql.endswith(";"):
                sql += ";"
        else:
            raise Exception("Invalid SQL generated")

    sql_lower = sql.lower()

    # -------------------------
    # 3. Safety checks
    # -------------------------
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

    # -------------------------
    # 4. Final clean output
    # -------------------------
    return sql.strip()