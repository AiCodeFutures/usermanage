from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

database.init_db()

app = FastAPI()

class User(BaseModel):
    id: int
    username: str
    email: str
    remark: str = None
    created_at: str

class UserCreate(BaseModel):
    username: str
    email: str
    remark: str = None

class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    remark: str = None

@app.get("/users", response_model=list)
def read_users():
    return database.get_all_users()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    user = database.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user

@app.post("/users", response_model=User)
def create_new_user(user: UserCreate):
    new_id = database.create_user(user.username, user.email, user.remark)
    new_user = database.get_user_by_id(new_id)
    return new_user

@app.put("/users/{user_id}", response_model=User)
def update_existing_user(user_id: int, user: UserUpdate):
    updated = database.update_user(user_id, user.username, user.email, user.remark)
    if not updated:
        raise HTTPException(status_code=400, detail="更新失败")
    updated_user = database.get_user_by_id(user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return updated_user

@app.delete("/users/{user_id}")
def delete_existing_user(user_id: int):
    if not database.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="用户未找到")
    database.delete_user(user_id)
    return {"detail": "删除成功"}