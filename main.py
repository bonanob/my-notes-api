from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from uuid import UUID

load_dotenv() # read .env into environment variables

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

def get_connection():
    # Open a connection; rows come back as dicts (row["col"]) instead of tuples
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


notes = []
next_id = 1

class NoteCreate(BaseModel):
    title: str
    content: str

@app.get("/")
def read_root():
    return {"message": "Hello, notes!"}

@app.post("/notes")
def create_note(note: NoteCreate):
    # global next_id
    # new_note = {"id": next_id, "title": note.title, "content": note.content}
    # notes.append(new_note)
    # next_id += 1
    # return new_note
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (title, content) VALUES (%s, %s) "
                "RETURNING id, title, content, created_at",
                (note.title, note.content),
            )
            row = cur.fetchone()
            conn.commit()
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
    }

@app.get("/notes")
def list_notes():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")
            rows = cur.fetchall()
    return [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "content": row["content"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

@app.get("/notes/{note_id}")
def get_note(note_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, content, created_at FROM notes WHERE id = %s",
                (note_id,),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


@app.put("/notes/{note_id}")
def update_note(note_id: UUID, update_note: NoteCreate):
    # for note in notes:
    #     if note["id"] == note_id:
    #         note["title"] = update_note.title
    #         note["content"] = update_note.content
    #         return note
    # raise HTTPException(status_code=404, detail="Note not found")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE notes SET title = %s, content = %s, updated_at = now() "
                "WHERE id = %s "
                "RETURNING id, title, content, created_at, updated_at",
                (update_note.title, update_note.content, str(note_id))
            )
            row = cur.fetchone()
            conn.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@app.delete("/notes/{note_id}")
def delete_note(note_id: UUID):
    # for note in notes:
    #     if note["id"] == note_id:
    #         notes.remove(note)
    #         return {"message": "Note deleted", "id": note_id}
    # raise HTTPException(status_code=404, detail="Note not found")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM notes WHERE id = %s",
                (str(note_id),),
            )
            deleted_count = cur.rowcount
            conn.commit()
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note deleted", "id": str(note_id)}


@app.get("/health/db")
def health_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
    return {"db": "ok", "result": result[0]}
