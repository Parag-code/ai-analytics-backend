from flask import Flask, jsonify
from database.db import test_connection
from flask import Flask, request, jsonify
from sqlalchemy import text
from database.db import engine
from llm.llm_service import generate_sql
from services.sql_validator import validate_sql

app = Flask(__name__)

@app.route("/")
def health():
    return jsonify({"status": "Backend Running"})

@app.route("/db-test")
def db_test():
    try:
        result = test_connection()
        return jsonify({"database_status": f"Connected, result: {result}"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]

    try:
        generated_sql = generate_sql(question)

        safe_sql = validate_sql(generated_sql)

        return jsonify({
            "question": question,
            "generated_sql": safe_sql
        })

    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "generated_sql": generated_sql if "generated_sql" in locals() else None
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e),
            "generated_sql": generated_sql if "generated_sql" in locals() else None
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)