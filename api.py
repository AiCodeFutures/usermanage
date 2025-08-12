from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import database
import uvicorn
import hashlib

# Initialize the database
database.init_db()

# --- Pydantic Models ---

class UserBase(BaseModel):
    username: str
    email: str
    remark: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    is_admin: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    remark: Optional[str] = None
    is_admin: Optional[bool] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None

class User(UserBase):
    id: int
    created_at: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: str
    password: str

# --- FastAPI App ---

app = FastAPI(
    title="User Management API",
    description="API for managing users in the user management system.",
    version="1.0.0",
)

# --- Helper Functions ---

def hash_password(password: str) -> str:
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# --- API Endpoints ---

@app.get("/", tags=["General"])
def index():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the User Management API!"}

@app.post("/login", response_model=User, tags=["Authentication"])
def login(form_data: UserLogin):
    """
    Authenticate a user. The API will hash the provided password for comparison.
    """
    user = database.get_user_by_email(form_data.email)
    if not user or not hash_password(form_data.password) == user['password']:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )
    return user

@app.get("/users", response_model=List[User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users with pagination.
    """
    users = database.get_all_users(skip=skip, limit=limit)
    return users

@app.get("/users/count", response_model=int, tags=["Users"])
def get_users_count():
    """
    Get the total number of registered users.
    """
    return database.get_total_users_count()

@app.get("/users/search", response_model=List[User], tags=["Users"])
def search_users_endpoint(query: str = Query(..., min_length=1)):
    """
    Search for users by username, email, or remark.
    """
    return database.search_users(query)

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
def read_user(user_id: int):
    """
    Retrieve a single user by their ID.
    """
    user = database.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=User, status_code=201, tags=["Users"])
def create_new_user(user: UserCreate):
    """
    Create a new user. The API will hash the password.
    """
    db_user = database.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_id = database.create_user(
        username=user.username,
        email=user.email,
        password=hashed_password,
        remark=user.remark,
        is_admin=user.is_admin,
        height=user.height,
        weight=user.weight,
        age=user.age
    )

    new_user = database.get_user_by_id(new_id)
    if not new_user:
        raise HTTPException(status_code=500, detail="Could not create user.")

    return new_user

@app.put("/users/{user_id}", response_model=User, tags=["Users"])
def update_existing_user(user_id: int, user: UserUpdate):
    """
    Update a user's information. Hashes the password if provided.
    """
    db_user = database.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.dict(exclude_unset=True)

    if 'password' in update_data and update_data['password']:
        update_data['password'] = hash_password(update_data['password'])
    else:
        update_data.pop('password', None)

    database.update_user(user_id, **update_data)

    updated_user = database.get_user_by_id(user_id)
    return updated_user

@app.delete("/users/{user_id}", status_code=204, tags=["Users"])
def delete_existing_user(user_id: int):
    """
    Delete a user by ID.
    """
    db_user = database.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    database.delete_user(user_id)
    # A 204 response must not have a body.
    return

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)