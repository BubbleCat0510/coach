from fastapi import APIRouter, Depends
from utils.jwt import get_current_user
from app.core.db import get_db

router = APIRouter(prefix="/user", tags=["用户"])

@router.post("/nickname")
def get_nickname(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    
    # 从数据库查询用户昵称
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT nickname FROM coach_user WHERE id = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()

    nickname = user["nickname"] if user and user.get("nickname") else "匿名用户"
    
    return {"nickname": nickname}

@router.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    print("current_user:", current_user)
    user_id = current_user.get("user_id")
    print("user_id:", user_id)
    
    # 从数据库查询用户完整信息
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, nickname as name, role, create_time as createdAt 
                FROM coach_user 
                WHERE id = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()
            print("查询结果:", user)
    
    if user:
        # 转换时间格式
        if user.get("createdAt"):
            user["createdAt"] = user["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
        print("返回结果:", user)
        return {
            "msg": "已登录",
            "user": user
        }
    else:
        return {
            "msg": "用户不存在",
            "user": None
        }

# 新增：获取当前用户的岗位
@router.get("/role")  # 建议用 GET（查询操作），POST 适合提交数据
def get_user_role(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    
    # 从数据库查询用户岗位
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT role FROM coach_user WHERE id = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()

    # 直接返回数据库中的值，即使是空值
    return {"role": user.get("role") if user else None}

# 获取用户列表（管理员权限）
@router.get("/list")
def get_user_list(current_user: dict = Depends(get_current_user)):
    # 从数据库查询所有用户
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, nickname as name, role, create_time as createdAt 
                FROM coach_user
                ORDER BY id ASC
                """
            )
            users = cursor.fetchall()
    
    # 转换为前端需要的格式
    user_list = []
    for user in users:
        user_list.append({
            "id": user["id"],
            "username": user["username"],
            "name": user["name"] or "",
            "role": user["role"] if user["role"] is not None else "",
            "createdAt": user["createdAt"].strftime("%Y-%m-%d %H:%M:%S") if user["createdAt"] else ""
        })
    
    return {"users": user_list}

# 更新用户角色
@router.post("/update-role")
def update_user_role(role: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    
    # 更新用户角色
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE coach_user 
                SET role = %s 
                WHERE id = %s
                """,
                (role, user_id)
            )
            conn.commit()
    
    return {"success": True, "message": "角色更新成功"}

# 添加用户
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    name: str
    password: str
    role: int  # 改为 int 类型

@router.post("/create")
def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    import hashlib
    
    # 哈希密码
    hashed_password = hashlib.md5(user.password.encode()).hexdigest()
    
    # 插入新用户
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO coach_user (username, password, nickname, role, status)
                VALUES (%s, %s, %s, %s, 1)
                """,
                (user.username, hashed_password, user.name, user.role)
            )
            conn.commit()
    
    return {"success": True, "message": "用户添加成功"}

class UserUpdate(BaseModel):
    name: str
    password: str = None

# 更新用户
@router.post("/update")
def update_user(user: UserUpdate, current_user: dict = Depends(get_current_user)):
    import hashlib
    user_id = current_user.get("user_id")
    
    # 更新用户信息
    with get_db() as conn:
        with conn.cursor() as cursor:
            if user.password:
                # 哈希密码
                hashed_password = hashlib.md5(user.password.encode()).hexdigest()
                # 更新昵称和密码
                cursor.execute(
                    """
                    UPDATE coach_user 
                    SET nickname = %s, password = %s
                    WHERE id = %s
                    """,
                    (user.name, hashed_password, user_id)
                )
            else:
                # 只更新昵称
                cursor.execute(
                    """
                    UPDATE coach_user 
                    SET nickname = %s
                    WHERE id = %s
                    """,
                    (user.name, user_id)
                )
            conn.commit()
    
    return {"success": True, "message": "用户更新成功"}

class UserDelete(BaseModel):
    id: int

# 删除用户
@router.post("/delete")
def delete_user(user: UserDelete, current_user: dict = Depends(get_current_user)):
    # 删除用户
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM coach_user 
                WHERE id = %s
                """,
                (user.id,)
            )
            conn.commit()
    
    return {"success": True, "message": "用户删除成功"}
