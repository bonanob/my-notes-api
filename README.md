# my-notes-api

A note-taking API built with FastAPI — the foundation of a longer
project in AI Data / Platform Engineering.

## Stack
Python 3.12 · FastAPI · uv

## Run
\`\`\`bash
git clone https://github.com/bonanob/my-notes-api.git
cd my-notes-api
uv sync
uv run uvicorn main:app --reload
\`\`\`
Open http://localhost:8000/docs

## Status
Stage 1 (Foundation), in progress. Currently a single root endpoint;
CRUD + database coming next.