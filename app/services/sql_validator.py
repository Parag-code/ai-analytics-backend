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

    sql_original = sql.strip()
    sql_clean = sql_original.lower()

    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    if sql_clean.count(";") > 1 or not sql_clean.endswith(";"):
        raise ValueError("Invalid SQL termination.")

    if "--" in sql_clean or "/*" in sql_clean:
        raise ValueError("SQL comments are not allowed.")

    for word in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{word}\b", sql_clean):
            raise ValueError(f"Forbidden keyword detected: {word}")

    if re.search(r"\binto\b", sql_clean):
        raise ValueError("SELECT INTO is not allowed.")

    danger_patterns = [
        r"\bxp_",
        r"\bpg_",
    ]

    for pattern in danger_patterns:
        if re.search(pattern, sql_clean):
            raise ValueError("Suspicious SQL pattern detected.")

    return re.sub(r"\s+", " ", sql_original).strip()