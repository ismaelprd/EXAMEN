import os
import hashlib
import libsql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return libsql.connect(
        database=os.environ["TURSO_DATABASE_URL"],
        auth_token=os.environ["TURSO_AUTH_TOKEN"],
    )

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row:
            return row[0] == hash_password(password)
        return False
    finally:
        conn.close()