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

    if user["role"] == "管理员":
        return {"role": "品牌选址"}
    
    if not user or not user.get("role"):
        # 兜底默认岗位
        return {"role": "品牌选址"}
    
    return {"role": user["role"]}
