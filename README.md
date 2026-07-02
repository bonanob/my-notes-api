# my-notes-api

A note-taking API built with FastAPI and PostgreSQL — the foundation of a
longer project in AI Data / Platform Engineering.

## Stack
Python 3.12 · FastAPI · PostgreSQL 16 · psycopg 3 · bcrypt · PyJWT · uv

## Features
- Full CRUD for notes (create, list, get, update, delete)
- PostgreSQL-backed persistence: UUID primary keys, `jsonb` metadata, timestamps
- Parameterized SQL (injection-safe); UUID path validation (422 / 404 / 200)
- Schema versioned as code in `schema.sql`

## Prerequisites
- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16 running locally (e.g. `brew services start postgresql@16`)

## Setup
```bash
git clone https://github.com/bonanob/my-notes-api.git
cd my-notes-api
uv sync

# create the database and apply the schema
createdb my_notes
psql my_notes -f schema.sql

# point the app at the database and set a JWT signing secret
echo "DATABASE_URL=postgresql://localhost/my_notes" > .env
echo "SECRET_KEY=$(uv run python -c 'import secrets; print(secrets.token_hex(32))')" >> .env
```

## Run
```bash
uv run uvicorn main:app --reload
```
Open http://localhost:8000/docs to try the endpoints.
Health check: http://localhost:8000/health/db returns `{"db":"ok","result":1}`.

## Status
Stage 1 (Foundation). CRUD complete with PostgreSQL persistence and Pydantic
response models (`NoteOut`). Auth in progress: a `users` table, `POST /register`
(bcrypt-hashed passwords), and `POST /login` (issues a JWT access token) are in
place. Next: token verification to protect routes, then a React frontend.
