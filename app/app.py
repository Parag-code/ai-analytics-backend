from flask import Flask, jsonify
from database.db import test_connection

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)