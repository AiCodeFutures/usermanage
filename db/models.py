from db.database import get_connection

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username: str, email: str, remark: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, remark) VALUES (?, ?, ?)",
        (username, email, remark)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_user(user_id: int, username: str = None, email: str = None, remark: str = None):
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
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True

def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True