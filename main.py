from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from uuid import UUID
from datetime import datetime
import bcrypt

def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:72]          # 72바이트로 안전하게 자름
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")                      # DB엔 문자열로 저장

def verify_password(password: str, password_hash: str) -> bool:
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(pw_bytes, password_hash.encode("utf-8"))

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

class NoteOut(BaseModel):
    id: UUID
    title: str
    content: str | None
    metadata: dict
    created_at: datetime
    updated_at: datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: UUID
    email: str
    created_at: datetime


@app.get("/")
def read_root():
    return {"message": "Hello, notes!"}

@app.post("/notes", response_model=NoteOut)
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
                "RETURNING id, title, content, metadata, created_at, updated_at",
                (note.title, note.content),
            )
            row = cur.fetchone()
            conn.commit()
    return row

@app.get("/notes", response_model=list[NoteOut])
def list_notes():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, content, metadata, created_at, updated_at FROM notes ORDER BY created_at DESC")
            rows = cur.fetchall()
    return rows

@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, content, metadata, created_at, updated_at FROM notes WHERE id = %s",
                (note_id,),
            )
            row = cur.fetchall()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return row


@app.put("/notes/{note_id}", response_model=NoteOut)
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
                "RETURNING id, title, content, metadata, created_at, updated_at",
                (update_note.title, update_note.content, str(note_id))
            )
            row = cur.fetchone()
            conn.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return row


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

@app.post("/register", response_model=UserOut)
def register(user: UserCreate):
    hashed = hash_password(user.password)

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash)"
                "VALUES (%s, %s) "
                "RETURNING id, email, created_at",
                (user.email, hashed)
            )
            row = cur.fetchone()
            conn.commit()
            return row
