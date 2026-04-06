import requests
import os
from dotenv import load_dotenv
from services.table_relevance import detect_relevant_tables
from database.db import engine

import re
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL")

if not OLLAMA_URL:
    raise ValueError("OLLAMA_URL not set in environment")

OLLAMA_URL = OLLAMA_URL + "/api/generate"

MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-coder:1.3b")

def build_schema_description(schema, max_tables=15):

    parts = []

    for i, (table, columns) in enumerate(schema.items()):

        if i >= max_tables:
            break

        parts.append(f"\nTable: {table}")
        parts.append("Columns:")

        for col in columns[:10]:
            parts.append(f"- {col}")

    return "\n".join(parts)


def generate_sql(question: str, schema: dict) -> str:
    """
    Generate a safe SQL SELECT query compatible with the database 
    Returns a validated SQL statement.
    """
    db_type = engine.url.get_backend_name()
    relevant_tables = detect_relevant_tables(question)

    filtered_schema = {
        table: schema[table]
        for table in relevant_tables
        if table in schema
    }

    if not filtered_schema:
        filtered_schema = schema

    SCHEMA_DESCRIPTION = build_schema_description(filtered_schema)

    prompt = f"""
You are a world-class {db_type} SQL generator.
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
10. If the question asks for latest rows, order by a timestamp column if available.
11. If user specifies number of rows (example: 5, 10), use LIMIT.
12. If user says "ordered by", do not assume ASC or DESC unless specified.
13. Use SQL syntax compatible with {db_type}.

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
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"LLM request failed with status {response.status_code}")

        data = response.json()
        raw_output = data.get("response", "").strip()

        if not raw_output:
            raise Exception("Empty response from LLM")
        logger.info("LLM RAW OUTPUT: %s", raw_output)

    except Exception as e:
        logger.error("LLM call failed: %s", str(e))
        raise

    cleaned = re.sub(r"```.*?```", "", raw_output, flags=re.DOTALL).strip()

    cleaned = re.sub(r"(?i)sql\s*statement\s*:", "", cleaned)
    cleaned = re.sub(r"(?i)here\s+is\s+the\s+sql\s*:", "", cleaned)
    cleaned = cleaned.strip()

    match = re.search(
        r"(select\s+.*?;)",
        cleaned,
        re.IGNORECASE | re.DOTALL
    )

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

    if "count(" in sql_lower:
        sql = re.sub(r"\s+limit\s+\d+", "", sql, flags=re.IGNORECASE)

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create"
    ]

    for keyword in forbidden_keywords:
      if re.search(rf"\b{keyword}\b", sql_lower):
        raise Exception(f"Dangerous SQL detected: {keyword}")

    if not sql_lower.startswith("select"):
        raise Exception("Only SELECT queries are allowed")

    sql = re.sub(r"\s+", " ", sql).strip()

    if "limit" not in sql_lower and "count(" not in sql_lower:
        if db_type in ["postgresql", "mysql", "sqlite"]:
            sql = sql.rstrip(";") + " LIMIT 50;"

    logger.info(f"Generated SQL: {sql}")

    return sql