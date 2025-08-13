# 项目分析报告 (GEMINI.md)

## 1. 项目概述

本项目是一个用户管理系统，结合了后端 API 和前端 Web 界面。

- **后端**: 使用 `FastAPI` 框架构建 RESTful API，负责处理用户数据的增、删、改、查（CRUD）逻辑。
- **前端**: 使用 `Streamlit` 构建一个交互式的 Web 管理界面，用户可以通过该界面直观地管理用户数据。
- **数据库**: 使用 `SQLite` 作为数据存储，通过 `database.py` 模块进行所有数据库操作。

系统分为两个主要部分：
1.  **API 服务 (`api.py`)**: 提供了一系列 HTTP 端点（endpoints）来操作用户数据。
2.  **Web 应用 (`main.py`)**: 一个面向用户的图形界面，它通过调用上述 API 来实现其功能。

## 2. 项目结构分析

```
/
├── api.py            # FastAPI 后端应用，定义所有 API 端点。
├── main.py           # Streamlit 前端应用，提供用户管理界面。
├── database.py       # 数据库模块，封装了所有与 SQLite 相关的操作。
├── requirements.txt  # 项目依赖的 Python 包。
├── startapi.sh       # 启动 FastAPI 服务的便捷脚本。
├── test.http         # 用于测试 API 端点的 HTTP 请求集合。
├── README.md         # 项目的基本介绍和使用说明。
├── 项目任务.md       # 项目的开发需求和任务列表。
└── db/               # (推测) 存放 SQLite 数据库文件的目录。
```

### 文件功能详解:

- **`api.py`**:
    - 使用 `FastAPI` 创建 Web 服务。
    - 定义了 `/users` 相关的所有 RESTful API 端点，包括获取、创建、更新和删除用户。
    - 使用 `Pydantic` 模型 (`User`, `UserCreate`, `UserUpdate`) 进行数据验证和序列化。
    - 在启动时调用 `database.init_db()` 来确保数据库和表已创建。

- **`main.py`**:
    - 使用 `Streamlit` 构建前端 UI。
    - 通过 `requests` 库与 `api.py` 提供的 API 进行通信。
    - 实现了用户登录、注册、展示、添加、更新、搜索和删除等功能。
    - 包含管理员权限 (`is_admin`) 的逻辑，部分操作（如删除用户）仅对管理员开放。

- **`database.py`**:
    - 负责所有与 `users.db` 数据库的交互。
    - `init_db()`: 初始化数据库，创建 `users` 表，并能动态地向表中添加新列（如 `is_admin`, `height` 等），具有良好的扩展性。
    - 提供了完整的 CRUD 函数（`create_user`, `get_all_users`, `update_user`, `delete_user` 等）。
    - 连接配置从环境变量 `DATABASE_PATH` 读取，如果未设置则默认为 `users.db`。

- **`项目任务.md`**:
    - 清晰地定义了项目的目标、技术栈和功能需求。
    - 是理解项目初始设计意图的重要文件。

- **`startapi.sh`**:
    - 内容为 `uvicorn api:app --reload`。
    - 这是启动 FastAPI 开发服务器的标准命令，`--reload` 参数使其在代码变更后能自动重启，非常适合开发环境。

## 3. 核心功能与逻辑

### a. 数据模型

- **数据库层面**: `users` 表包含 `id`, `username`, `email`, `password`, `remark`, `created_at`, `is_admin`, `height`, `weight`, `age` 等字段。
- **API 层面**: `Pydantic` 模型确保了 API 请求和响应的数据结构和类型正确性。

### b. 认证流程

1.  **注册**: `main.py` 收集用户信息，通过 `POST /users` API 创建新用户。密码被直接发送到后端。
2.  **登录**: `main.py` 收集邮箱和密码，通过 `POST /login` API 进行验证。
3.  **会话管理**: 登录成功后，`main.py` 使用 `st.session_state` 在 Streamlit 中维持用户的登录状态，并保存用户名、用户ID和管理员状态。

### c. 前后端交互

- 前端 (`main.py`) 完全依赖后端 (`api.py`) 提供的数据接口。
- 所有在界面上的操作（如列表展示、添加用户）都会转换成对相应 API 端点的 HTTP 请求。
- 这种前后端分离的架构使得项目结构清晰，易于维护和扩展。例如，可以为这个 API 开发一个完全不同的前端（如移动 App）而无需改动后端代码。

## 4. 如何运行项目

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **启动后端 API 服务**:
    在终端中运行 `startapi.sh` 脚本。
    ```bash
    sh startapi.sh
    ```
    服务将启动在 `http://127.0.0.1:8000`。

3.  **启动前端管理界面**:
    在另一个终端中运行 `main.py`。
    ```bash
    streamlit run main.py
    ```
    应用将在浏览器中打开。

## 5. 潜在的改进点

- **安全性**:
    - 目前密码在注册时以明文形式发送到后端，并且在数据库中似乎是明文存储（或固定为 "123456"）。应在后端对密码进行哈希处理和加盐存储。
    - API 端点没有保护，任何人都可以调用。应引入如 OAuth2 的认证机制来保护 API。
- **配置管理**:
    - API URL 在 `main.py` 中是硬编码的。虽然有 `os.getenv` 作为备选，但可以考虑使用 `.env` 文件来统一管理环境变量。
- **数据库迁移**:
    - `database.py` 中的 `init_db` 函数通过 `PRAGMA table_info` 来动态添加列。这在开发初期很方便，但对于生产环境，使用更专业的数据库迁移工具（如 Alembic）会是更健壮的选择。
