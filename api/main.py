from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import database, models

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
    users = models.get_all_users()
    return users

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    user = models.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=User)
def create_new_user(user: UserCreate):
    new_id = models.create_user(user.username, user.email, user.remark)
    new_user = models.get_user_by_id(new_id)
    return new_user

@app.put("/users/{user_id}", response_model=User)
def update_existing_user(user_id: int, user: UserUpdate):
    updated = models.update_user(user_id, user.username, user.email, user.remark)
    if not updated:
        raise HTTPException(status_code=400, detail="No field to update")
    updated_user = models.get_user_by_id(user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}")
def delete_existing_user(user_id: int):
    user = models.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    models.delete_user(user_id)
    return {"detail": "User deleted"}