from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# 环境导入 -- 需要在工具前导入，防止功能函数无法使用
from dotenv import load_dotenv
load_dotenv()

# 功能导入
from utils.jwt import create_token
from app.api import user, train, ai, exam
from app.core import db

app = FastAPI()

app.include_router(user.router)
app.include_router(train.router)
app.include_router(ai.router)
app.include_router(exam.router)

# ===== CORS 配置（必须加，浏览器规范要求：必须先 OPTIONS）=====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 前端地址
    ],
    allow_credentials=True,
    allow_methods=["*"],        # 允许所有方法（包括 OPTIONS）
    allow_headers=["*"],        # 允许所有请求头
)


class LoginReq(BaseModel):
    username: str
    password: str
    role: str = "employee"

@app.post("/login")
def login(req: LoginReq):
    with db.get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password, role
                FROM coach_user
                WHERE username = %s
                """,
                (req.username)
            )
            user = cursor.fetchone()

    # 1️⃣ 用户不存在
    if not user:
        return {
            "success": False,
            "message": "账号或密码错误"            
        }

    # 2️⃣ 密码不匹配
    if user["password"] != req.password:
        return {
            "success": False,
            "message": "账号或密码错误"
        }

    # 3️⃣ 角色验证
    print("User data:", user)
    user_role = user.get("role", "employee")
    print("User role:", user_role)
    if req.role == "admin" and user_role != "管理员":
        # 用户选择管理员角色但数据库中不是管理员
        return {
            "success": False,
            "message": "权限不足，无法以管理员身份登录"
        }

    # 4️⃣ 登录成功，生成 token
    token = create_token({
        "user_id": user["id"],
        "username": user["username"],
        "role": user_role
    })

    return {
        "success": True,
        "token": token,
        "role": user_role
    }

# uvicorn main:app --host 0.0.0.0 --port 8001

# conda activate kefu
