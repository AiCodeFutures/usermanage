from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database
import models

database.init_db()

app = FastAPI()

class User(BaseModel):
    """
    用户模型类

    这是一个基于 Pydantic BaseModel 的用户数据模型，用于定义用户的基本属性和数据结构。

    Attributes:
        id (int): 用户的唯一标识符，主键
        username (str): 用户名，用于用户登录和识别
        email (str): 用户的电子邮箱地址
        remark (str, optional): 用户备注信息，可选字段，默认为 None
        created_at (str): 用户创建时间，以字符串格式存储

    Note:
        该模型继承自 Pydantic 的 BaseModel，提供了自动的数据验证、序列化和反序列化功能。
        所有字段都会根据类型注解进行自动验证。

    Example:
        创建用户实例：
        >>> user = User(
        ...     id=1,
        ...     username="john_doe",
        ...     email="john@example.com",
        ...     remark="测试用户",
        ...     created_at="2023-01-01T00:00:00"
        ... )
    """
    id: int
    username: str
    email: str
    remark: str = None
    created_at: str

class UserCreate(BaseModel):
    """用户创建模型

    用于创建新用户时的数据验证和传输。

    Attributes:
        username (str): 用户名
        email (str): 邮箱地址
        remark (str, optional): 备注信息，默认为None
    """
    username: str
    email: str
    remark: str = None

class UserUpdate(BaseModel):
    """
    用户更新模型类。

    用于更新用户信息的数据模型，包含用户名、邮箱和备注字段。
    所有字段都是可选的，可以单独或组合更新。

    Attributes:
        username (str, optional): 用户名
        email (str, optional): 邮箱地址
        remark (str, optional): 备注信息
    """
    username: str = None
    email: str = None
    remark: str = None

@app.get("/users", response_model=list)
def read_users():
    """
    获取所有用户列表

    Returns:
        list: 包含所有用户信息的列表
    """
    return models.get_all_users()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    user = models.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
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
        raise HTTPException(status_code=400, detail="更新失败")
    updated_user = models.get_user_by_id(user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return updated_user

@app.delete("/users/{user_id}")
def delete_existing_user(user_id: int):
    if not models.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="用户未找到")
    models.delete_user(user_id)
    return {"detail": "删除成功"}