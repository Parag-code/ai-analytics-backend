# AI Analytics Backend – LLM Powered SQL Generator

An intelligent backend system that converts natural language queries into SQL using a local LLM (Ollama) and executes them securely on a database.

---

## Features

* Natural Language → SQL using LLM
* Schema-aware query generation
* Secure SQL validation (only SELECT allowed)
* Dockerized setup (plug & play)
* Automatic LLM model download (Ollama)
* Works with multiple databases (PostgreSQL, MySQL, SQLite)

---

## Tech Stack

* Python (Flask)
* SQLAlchemy
* Databases: PostgreSQL / MySQL / SQLite
* Ollama (Local LLM)
* Docker & Docker Compose

---

## Project Structure

```
AI-Analytics-Backend/
│
├── app/
│   ├── database/
│   ├── llm/
│   ├── services/
│   └── app.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── start-ollama.sh
├── .env
└── README.md
```

---

## Setup & Run

### Extract Project

```bash
unzip AI-Analytics-Backend.zip
cd AI-Analytics-Backend
```

---

### Configure Environment

Edit `.env`:

```
DB_HOST=your_host
DB_PORT=your_port
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password

OLLAMA_URL=http://ollama:11434
MODEL_NAME=deepseek-coder:1.3b
```

👉 Supports:

* PostgreSQL (default port: 5432)
* MySQL (default port: 3306)
* SQLite (use DB_NAME as file name)

---

### Run with Docker

```bash
docker compose up --build
```

---

## First Run Note

* Ollama image will be downloaded (~6GB)
* LLM model will be pulled automatically
* Initial setup may take a few minutes

---

## API Testing

### Health Check

```
GET http://localhost:5000/
```

---

### Database Test

```
GET http://localhost:5000/db-test
```

---

### Ask Query

```bash
curl -X POST http://localhost:5000/ask \
-H "Content-Type: application/json" \
-d '{"question": "how many observations"}'
```

---

## Example Output

```json
{
  "question": "how many observations",
  "generated_sql": "SELECT COUNT(*) FROM observation;",
  "rows_returned": 1,
  "result": [
    {"count": 245}
  ]
}
```

---

## Important Notes

* Only **SELECT** queries are allowed
* Database type is automatically detected at runtime

---

## How It Works

1. User sends a natural language query
2. LLM converts it into SQL
3. SQL is validated (safe queries only)
4. Query executes on connected database
5. Results are returned as JSON

---

## Example Queries

* "how many observations"
* "show latest 5 observations"
* "count observations by type"

---
