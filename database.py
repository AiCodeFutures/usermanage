import sqlite3
import os

DB_PATH = os.getenv("DATABASE_PATH") or "users.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# 以下是从 models.py 合并的 CRUD 函数
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, email, remark):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, remark) VALUES (?, ?, ?)", (username, email, remark))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_user(user_id, username=None, email=None, remark=None):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    params = []
    if username:
        fields.append("username = ?")
        params.append(username)
    if email:
        fields.append("email = ?")
        params.append(email)
    if remark:
        fields.append("remark = ?")
        params.append(remark)
    if not fields:
        conn.close()
        return False
    params.append(user_id)
    query = "UPDATE users SET " + ", ".join(fields) + " WHERE id = ?"
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True
