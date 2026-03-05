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
    No automatic LIMIT injection.
    """

    sql_clean = sql.strip().lower()

    # Only SELECT allowed
    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    # Block dangerous keywords
    for word in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{word}\b", sql_clean):
            raise ValueError(f"Forbidden keyword detected: {word}")

    return sql.strip()