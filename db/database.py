import sqlite3
import json
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "chunks.db"


def _open_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_database():
    connection = _open_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            content   TEXT NOT NULL,
            embedding TEXT NOT NULL,
            source    TEXT NOT NULL,
            title     TEXT
        )
    """)
    connection.commit()
    connection.close()


def clear_database():
    connection = _open_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM documents")
    connection.commit()
    connection.close()


def save_chunk(content, embedding, source, title=None):
    connection = _open_connection()
    cursor = connection.cursor()
    embedding_json = json.dumps(embedding)
    cursor.execute(
        "INSERT INTO documents (content, embedding, source, title) VALUES (?, ?, ?, ?)",
        (content, embedding_json, source, title)
    )
    connection.commit()
    connection.close()


def get_all_chunks():
    connection = _open_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, content, embedding, source, title FROM documents")
    rows = cursor.fetchall()
    connection.close()

    chunks = []
    for row in rows:
        chunks.append({
            "id": row[0],
            "content": row[1],
            "embedding": json.loads(row[2]),
            "source": row[3],
            "title": row[4],
        })
    return chunks


if __name__ == "__main__":
    create_database()
    clear_database()

    save_chunk(
        content="In the arena, you go counterclockwise.",
        embedding=[0.1, 0.2, 0.3],
        source="test.txt",
        title="Arena Rules",
    )

    for chunk in get_all_chunks():
        print(chunk)