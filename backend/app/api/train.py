# app/api/train.py
from fastapi import APIRouter, Depends, Query, Body
from app.core.db import get_db
from utils.jwt import get_current_user  
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/train", tags=["训练"])

# coach_train_session —— 训练会话表

# 作用：一次完整的训练过程

# 字段名	    类型	        含义
# id	        bigint	        训练会话 ID
# user_id	    bigint	        用户 ID
# title	        varchar(100)	训练主题
# role_name	    varchar(50)	    AI 教练角色
# status	    tinyint	        1 进行中 / 2 已完成
# create_time	datetime	    创建时间
# update_time	datetime	    更新时间

# coach_train_round —— 训练轮次表

# 作用：训练中的每一轮对话

# 字段名	    类型	    含义
# id	        bigint	    轮次 ID
# session_id	bigint	    训练会话 ID
# user_id	    bigint	    用户 ID
# ai_question	text	    AI 提问
# user_answer	text	    用户回答
# ai_reply	    text	    AI 教练回复
# score	        int	        训练评分
# feedback	    text	    改进建议
# create_time	datetime	创建时间

class SessionCreate(BaseModel):
    role: str

@router.post("/session")
def create_train_session(
    req: SessionCreate,
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["user_id"]

    # 品牌选址、房源选址、上门服务、招商专员、选址专员

    time_text = datetime.now().strftime("%Y-%m-%d %H:%M")

    title = f"{req.role} 训练 - {time_text}"

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO coach_train_session (user_id, role_name, title, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, req.role, title, datetime.now(), datetime.now())
            )
            session_id = cursor.lastrowid

    return {
        "id": session_id,
        "title": title,
        "role_name": req.role,
        "create_time": datetime.now(),
        "update_time": datetime.now()
    }

# 定义请求体模型（核心：接收 JSON 体参数）
class RoundSave(BaseModel):
    session_id: int          # 会话ID（整数）
    ai_question: str         # AI提问
    user_text: str           # 用户回答
    ai_reply: str            # AI回复
    score: int = 0           # 评分（默认值）
    feedback: str = ""       # 评价（默认值）

@router.post("/round")
def save_train_round(
    req: RoundSave,
    current_user: dict = Depends(get_current_user)
):
    """
    保存一轮训练对话（用户 + AI + 评分）
    """

    user_id = current_user["user_id"]

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO coach_train_round
                (session_id, ai_question, user_id, user_answer, ai_reply, score, feedback, create_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    req.session_id,
                    req.ai_question,
                    user_id,
                    req.user_text,
                    req.ai_reply,
                    req.score,
                    req.feedback,
                    datetime.now()
                )
            )
            # 同步更新会话的最近活动时间（update_time）
            cursor.execute(
                """
                UPDATE coach_train_session
                SET update_time = %s
                WHERE id = %s
                """,
                (datetime.now(), req.session_id)
            )

    return {
        "msg": "训练记录已保存"
    }

@router.get("/rounds")
def get_train_rounds(
    session_id: int = Query(..., description="训练会话ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取某个 session 下的所有训练对话
    - 只允许查看自己的 session
    """

    user_id = current_user["user_id"]

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ai_question,
                    user_answer,
                    ai_reply,
                    score,
                    feedback,
                    create_time
                FROM coach_train_round
                WHERE session_id=%s AND user_id=%s
                ORDER BY id ASC
                """,
                (session_id, user_id)
            )
            records = cursor.fetchall()

    return [
        {
            "aiQuestion": r.get("ai_question"),
            "userAnswer": r.get("user_answer"),
            "aiReply": r.get("ai_reply"),
            "score": {
                "value": r["score"],
                "feedback": r["feedback"]
            } if r["score"] is not None else None
        }
        for r in records
    ]

@router.get("/session/list")
def list_train_sessions(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    role_name,
                    create_time,
                    update_time
                FROM coach_train_session
                WHERE user_id = %s
                ORDER BY update_time DESC
                """,
                (user_id,)
            )
            sessions = cursor.fetchall()

    return sessions

# @router.post("/updata")
