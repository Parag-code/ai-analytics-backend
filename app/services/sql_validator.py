import re

FORBIDDEN_KEYWORDS = [
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "commit",
    "rollback"
]


def validate_sql(sql: str) -> str:
    """
    Validates LLM generated SQL.
    Only SELECT queries are allowed.
    Also auto-inject LIMIT if missing.
    """

    sql_clean = sql.strip().lower()

    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    for word in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{word}\b", sql_clean):
            raise ValueError(f"Forbidden keyword detected: {word}")

    if "limit" not in sql_clean:
        sql = sql.rstrip(";") + " LIMIT 50;"

    return sql