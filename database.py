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
    # 创建 users 表，如果它不存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0,
            height REAL,
            weight REAL,
            age INTEGER
        )
    """)

    # 检查并添加 is_admin 列
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'is_admin' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        conn.commit()
        print("Added 'is_admin' column to 'users' table.")

    # 检查并添加 height 列
    if 'height' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN height REAL")
        conn.commit()
        print("Added 'height' column to 'users' table.")

    # 检查并添加 weight 列
    if 'weight' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN weight REAL")
        conn.commit()
        print("Added 'weight' column to 'users' table.")

    # 检查并添加 age 列
    if 'age' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        conn.commit()
        print("Added 'age' column to 'users' table.")

    conn.commit()
    conn.close()

# 以下是从 models.py 合并的 CRUD 函数
def get_total_users_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_users(skip=0, limit=None):
    conn = get_connection()
    cursor = conn.cursor()
    if limit:
        cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (limit, skip))
    else:
        cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_users(query):
    conn = get_connection()
    cursor = conn.cursor()
    search_pattern = f"%{query}%"
    cursor.execute("SELECT * FROM users WHERE username LIKE ? OR email LIKE ? OR remark LIKE ?", (search_pattern, search_pattern, search_pattern))
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

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, email, remark, is_admin=0, height=None, weight=None, age=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password, remark, is_admin, height, \
         weight, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (username, email, "123456", remark, is_admin, height, weight, age))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def authenticate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    # 确保查询所有列，包括 is_admin
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user(user_id, username=None, email=None, remark=None, is_admin=None, height=None, weight=None, age=None):
    conn = get_connection() # 注意：这里之前是 get_db_connection()，已更正为 get_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    # if password is not None:
        # updates.append("password = ?")
        # params.append(password)
    if remark is not None:
        updates.append("remark = ?")
        params.append(remark)
    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(1 if is_admin else 0)
    if height is not None:
        updates.append("height = ?")
        params.append(height)
    if weight is not None:
        updates.append("weight = ?")
        params.append(weight)
    if age is not None:
        updates.append("age = ?")
        params.append(age)

    if not updates:
        conn.close()
        return False

    params.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True
