import sqlite3
from datetime import datetime

def get_connection():
    conn = sqlite3.connect("users.db")
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

def main():
    init_db()  # 初始化数据库及表
    print("欢迎使用用户管理系统")
    while True:
        print("\n选项：")
        print("1. 列出所有用户")
        print("2. 添加用户")
        print("3. 更新用户")
        print("4. 删除用户")
        print("5. 退出")
        choice = input("请输入选项: ")
        if choice == "1":
            users = get_all_users()
            print("用户列表:")
            for user in users:
                print(user)
        elif choice == "2":
            username = input("请输入用户名: ")
            email = input("请输入邮箱: ")
            remark = input("请输入备注: ")
            new_id = create_user(username, email, remark)
            print(f"用户已添加，ID: {new_id}")
        elif choice == "3":
            try:
                user_id = int(input("请输入要更新的用户ID: "))
            except ValueError:
                print("请输入正确的数字！")
                continue
            username = input("请输入新用户名（留空不更新）: ")
            email = input("请输入新邮箱（留空不更新）: ")
            remark = input("请输入新备注（留空不更新）: ")
            username = username if username.strip() != "" else None
            email = email if email.strip() != "" else None
            remark = remark if remark.strip() != "" else None
            updated = update_user(user_id, username, email, remark)
            if updated:
                print("用户已更新")
            else:
                print("更新失败，没有更新的字段或用户不存在")
        elif choice == "4":
            try:
                user_id = int(input("请输入要删除的用户ID: "))
            except ValueError:
                print("请输入正确的数字！")
                continue
            if delete_user(user_id):
                print("用户已删除")
            else:
                print("删除失败，用户可能不存在")
        elif choice == "5":
            print("退出系统")
            break
        else:
            print("无效选项，请重试")

if __name__ == "__main__":
    main()
