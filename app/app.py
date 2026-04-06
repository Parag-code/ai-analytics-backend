from flask import Flask, request, jsonify
from sqlalchemy import text

from database.db import test_connection, engine
from llm.llm_service import generate_sql
from services.sql_validator import validate_sql
from database.schema_loader import load_schema

app = Flask(__name__)

try:
    print("Loading schema...")
    SCHEMA_CACHE = load_schema()
    print("Schema loaded successfully")
except Exception as e:
    print(f"Schema load failed: {e}")
    SCHEMA_CACHE = {}


@app.route("/")
def health():
    return jsonify({"status": "Backend Running"})


@app.route("/db-test")
def db_test():
    try:
        result = test_connection()
        return jsonify({"database_status": f"Connected, result: {result}"})
    except Exception as e:
        return jsonify({
            "error": str(e),
            "hint": "Check database credentials in .env"
        }), 500


@app.route("/ask", methods=["POST"])
def ask():

    if not SCHEMA_CACHE:
        return jsonify({"error": "Schema not loaded"}), 500

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]

    print(f"Question: {question}")

    try:
        generated_sql = generate_sql(question, SCHEMA_CACHE)

        safe_sql = validate_sql(generated_sql)

        with engine.begin() as conn:
            result = conn.execute(text(safe_sql))
            rows = [dict(row._mapping) for row in result][:100]  # limit rows

        return jsonify({
            "question": question,
            "generated_sql": safe_sql,
            "rows_returned": len(rows),
            "result": rows
        })

    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "generated_sql": generated_sql if "generated_sql" in locals() else None
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e),
            "generated_sql": generated_sql if "generated_sql" in locals() else None,
            "hint": "Check DB connection, schema, or LLM service"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)