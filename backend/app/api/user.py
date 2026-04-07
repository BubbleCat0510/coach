from fastapi import APIRouter, Depends
from utils.jwt import get_current_user
from app.core.db import get_db

router = APIRouter(prefix="/user", tags=["用户"])

# coach_user —— 用户表

# 作用：系统用户、员工主体

# 字段名	    类型	        含义
# id	        bigint	        用户唯一 ID
# username	    varchar(50)	    登录账号
# password	    varchar(255)	登录密码（哈希）
# nickname	    varchar(50)	    昵称
# role	        varchar(20)	    岗位 / 角色
# status	    tinyint	        状态：1 正常 / 0 禁用
# create_time	datetime	    创建时间

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
    print("当前用户信息：", current_user)
    return {
        "msg": "已登录",
        "user": current_user
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
            "role": user["role"] or "",
            "createdAt": user["createdAt"].strftime("%Y-%m-%d %H:%M:%S") if user["createdAt"] else ""
        })
    
    return {"users": user_list}

# 更新用户角色
@router.post("/update-role")
def update_user_role(role: str, current_user: dict = Depends(get_current_user)):
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
