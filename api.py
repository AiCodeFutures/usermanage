from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database
import uvicorn
import os
from typing import Optional

try:
    from openai import OpenAI
    _openai_available = True
except Exception:
    _openai_available = False

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
    """用户创建模型"""
    username: str
    email: str
    password: str
    remark: str | None = None
    height: float | None = None
    weight: float | None = None
    age: int | None = None

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    remark: str | None = None
    is_admin: bool | None = None
    height: float | None = None
    weight: float | None = None
    age: int | None = None

class BMIRequest(BaseModel):
    height: float  # cm
    weight: float  # kg
    age: int
    gender: Optional[str] = None  # 'male' | 'female'
    goal: Optional[str] = None    # e.g. 'fat_loss', 'muscle_gain', 'recomposition'

class BMIPlanResponse(BaseModel):
    bmi: float
    bmi_category: str
    suggestion: str
    ai_plan: Optional[str] = None

# 简单 BMI 分类
_DEF_BMI_CATEGORIES = [
    (18.5, '偏瘦'),
    (24.0, '正常'),
    (28.0, '超重'),
    (100.0, '肥胖')
]

def _calc_bmi(height_cm: float, weight_kg: float) -> float:
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError('身高体重需为正数')
    h_m = height_cm / 100.0
    return round(weight_kg / (h_m ** 2), 2)

def _bmi_category(bmi: float) -> str:
    for threshold, label in _DEF_BMI_CATEGORIES:
        if bmi < threshold:
            return label
    return '未知'

def _basic_suggestion(bmi: float, age: int, goal: Optional[str]) -> str:
    base = []
    if bmi < 18.5:
        base.append('适当增肌增重，保证充足优质蛋白与睡眠。')
    elif bmi < 24:
        base.append('维持当前体重，继续均衡饮食与规律运动。')
    elif bmi < 28:
        base.append('控制热量摄入 (建议 -300~500kcal/日) 并增加力量+有氧组合。')
    else:
        base.append('建议在医生/营养师指导下制定中长期减脂计划，优先健康。')
    if age >= 45:
        base.append('关注心血管与关节负荷，循序渐进。')
    if goal == 'muscle_gain':
        base.append('在力量训练日适度热量盈余，蛋白 1.6~2.0g/kg。')
    elif goal == 'fat_loss':
        base.append('保持蛋白 1.6g/kg+, 维持轻度热量缺口。')
    elif goal == 'recomposition':
        base.append('交替轻微盈余与轻微缺口，保证训练强度。')
    return ' '.join(base)

@app.get("/")
def index():
    return {"message": "Hello, World!"}
'''
对于app.add_api_route的参数举例(这破函数参数怎么这么多啊,根本背不过啊混蛋!)
app.add_api_route(path: str, endpoint: Callable, *, methods: List[str] = None, response_model: Type[BaseModel] = None, status_code: int = None, tags: List[str] = None, summary: str = None, description: str = None, response_description: str = None, responses: Dict = None, response_class: Type[Response] = None, deprecated: bool = None, openapi_extra: dict = None)
'''



@app.get("/users", response_model=list)
def read_users(skip: int = 0, limit: int | None = None):
    return database.get_all_users(skip=skip, limit=limit)



@app.get('/users/count')
def users_count():
    return database.get_total_users_count()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    user = database.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user

@app.post("/users", response_model=dict, status_code=201)
def create_new_user(user: UserCreate):
    try:
        new_id = database.create_user(
            user.username, user.email, user.password, user.remark,
            height=user.height, weight=user.weight, age=user.age
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建用户失败: {e}")
    return database.get_user_by_id(new_id)

@app.put("/users/{user_id}", response_model=dict)
def update_existing_user(user_id: int, user: UserUpdate):
    updated = database.update_user(
        user_id,
        username=user.username,
        email=user.email,
        password=user.password,
        remark=user.remark,
        is_admin=user.is_admin,
        height=user.height,
        weight=user.weight,
        age=user.age,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="更新失败")
    data = database.get_user_by_id(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="用户未找到")
    return data

@app.delete("/users/{user_id}", status_code=204)
def delete_existing_user(user_id: int):
    if not database.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="用户未找到")
    database.delete_user(user_id)
    return None

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post('/login')
def login(req: LoginRequest):
    user = database.authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail='邮箱或密码错误')
    return user



@app.get('/users/search')
def users_search(query: str):
    return database.search_users(query)

@app.post('/bmi/plan', response_model=BMIPlanResponse)
def generate_bmi_plan(data: BMIRequest):
    """根据 BMI 及年龄生成基础建议，并可调用 DeepSeek(OpenAI 兼容) 模型生成智能方案。
    需要设置环境变量 DEEPSEEK_API_KEY (或 OPENAI_API_KEY) 与可选 DEEPSEEK_BASE_URL。
    """
    try:
        bmi = _calc_bmi(data.height, data.weight)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    category = _bmi_category(bmi)
    suggestion = _basic_suggestion(bmi, data.age, data.goal)

    ai_plan = None
    api_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL')  # 如 https://api.deepseek.com
    # 仅在安装了 openai 包且存在 key 时尝试
    if api_key and _openai_available:
        try:
            client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
            prompt = f"""你是专业的运动营养教练。请基于以下用户数据提供中文的 7 日身材(体脂)控制方案，使用分点与表格化友好格式：\n\nBMI: {bmi} ({category})\n年龄: {data.age}\n性别: {data.gender or '未提供'}\n目标: {data.goal or '未明确'}\n身高: {data.height} cm\n体重: {data.weight} kg\n\n需包含：\n1. 核心策略概述 (热量与宏量素区间)。\n2. 每日样例三餐+加餐 (注明大致热量)。\n3. 训练安排 (力量+有氧频次与示例)。\n4. 恢复与睡眠建议。\n5. 风险与注意事项。\n请简洁分段。"""
            completion = client.chat.completions.create(
                model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                messages=[
                    {"role": "system", "content": "你是专业的营养与训练顾问。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            ai_plan = completion.choices[0].message.content.strip()
        except Exception as e:
            # 不抛出，返回基础建议即可
            ai_plan = f"AI 方案生成失败: {e}"

    return BMIPlanResponse(bmi=bmi, bmi_category=category, suggestion=suggestion, ai_plan=ai_plan)

# 删除示例调用代码，避免在导入时就执行外部请求

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)