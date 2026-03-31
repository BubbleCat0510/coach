from fastapi import APIRouter, Depends
from app.core.db import get_db
from utils.jwt import get_current_user
from datetime import datetime
import json

router = APIRouter(prefix="/exam", tags=["Exam"])

# coach_exam_session —— 测试会话表（核心）

# 作用：一次正式能力测试

# 字段名	    类型	    含义
# id	        bigint	    测试会话 ID
# user_id	    bigint	    用户 ID
# exam_mode	    varchar(30)	测试模式（专项/综合/模拟）
# status	    tinyint	    1 进行中 / 2 已结束 / 3 已评分
# total_score	int	        总分（评分后生成）
# exam_rules	json	    测试规则快照
# create_time	datetime	创建时间
# finish_time	datetime	测试结束时间

# coach_exam_round —— 测试轮次表（原始记录）

# 作用：测试中每一轮的原始作答

# 字段名	        类型	    含义
# id	            bigint	    测试轮次 ID
# exam_session_id	bigint	    测试会话 ID
# user_id	        bigint	    用户 ID
# round_no	        int	        第几轮
# dimension	        varchar(50)	能力维度
# ai_question	    text	    AI 考题
# answer_analysis	text	    答案解析（AI生成）
# ai_reply	        text	    标准答案（AI生成）
# user_answer	    text	    用户回答
# round_score	    int	        单轮题目得分（如2/4/10/0）
# create_time	    datetime	创建时间

# coach_exam_score —— 测试评分表（维度级）

# 作用：测试结束后的能力评分结果

# 字段名	        类型	    含义
# id	            bigint	    评分 ID
# exam_session_id	bigint	    测试会话 ID
# dimension	        varchar(50)	能力维度
# score	            int	        维度得分（0–100）
# comment	        text	    评估评语

# coach_exam_report —— 测试总结报告表

# 作用：测试结果的管理视图摘要

# 字段名	        类型	    含义
# id	            bigint	    报告 ID
# exam_session_id	bigint	    测试会话 ID
# summary	        text	    综合能力总结
# strengths	        text	    优势能力
# weaknesses	    text	    短板能力
# created_time	    datetime	生成时间

# 开始考试
@router.post("/start")
def start_exam(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    exam_mode = data.get("exam_mode")

    # 简化：按模式生成规则
    rules = {
        "specialized": ["需求理解", "逻辑拆解"],
        "comprehensive": ["需求理解", "逻辑拆解", "技术设计"],
        "simulation": ["综合能力"]
    }

    dimensions = rules.get(exam_mode, ["逻辑拆解"])

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO coach_exam_session
                (user_id, exam_mode, status, exam_rules)
                VALUES (%s, %s, 1, %s)
                """,
                (user_id, exam_mode, json.dumps(dimensions))
            )
            conn.commit()
            session_id = cursor.lastrowid

    return {
        "session_id": session_id,
        "dimensions": dimensions
    }

# 记录结束时间
@router.post("/record_end_time")
def record_end_time(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE coach_exam_session
                SET finish_time=%s
                WHERE id=%s
                """,
                (datetime.now(), data.get("session_id"))
            )
            conn.commit()

    return {"success": True}

# 提交答案
@router.post("/answer")
def submit_answer(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    session_id = data.get("session_id")
    round_answers = data.get("round_answers", [])
    
    # 1. 校验会话状态（仅进行中的考试可提交）
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM coach_exam_session WHERE id=%s AND user_id=%s", (session_id, user_id))
            session = cursor.fetchone()
            if not session or session["status"] != 1:
                return {"success": False, "msg": "考试已结束/不存在，无法提交"}
            
            # 2. 批量更新每轮的用户答案和耗时（解析字段已存在，无需操作）
            total_score = 0  # 临时计算总分
            for item in round_answers:
                round_no = item.get("round_no")
                if not isinstance(round_no, int):
                    raise ValueError(f"round_no 非法: {round_no}")

                dimension = item.get("dimension") or "综合能力"
                ai_question = item.get("ai_question", "")
                scenario = item.get("scenario", "") # 场景字段（如果有）
                answer_analysis = item.get("answer_analysis", "")
                ai_reply = item.get("ai_reply", "")
                round_score = int(item.get("round_score", 0))

                user_answer = item.get("answer")

                # ✅ 关键修复点：强制字符串化
                if user_answer is not None and not isinstance(user_answer, str):
                    user_answer = json.dumps(user_answer, ensure_ascii=False)

                cursor.execute("""
                    SELECT id FROM coach_exam_round
                    WHERE exam_session_id=%s AND user_id=%s AND round_no=%s
                """, (session_id, user_id, round_no))

                exists = cursor.fetchone()

                if exists:
                    cursor.execute("""
                        UPDATE coach_exam_round
                        SET
                            dimension=%s,
                            ai_question=%s,
                            answer_analysis=%s,
                            ai_reply=%s,
                            user_answer=%s,
                            round_score=%s,
                            scenario=%s
                        WHERE exam_session_id=%s
                        AND user_id=%s
                        AND round_no=%s
                    """, (
                        dimension,
                        ai_question,
                        answer_analysis,
                        ai_reply,
                        user_answer,
                        round_score,
                        scenario,
                        session_id,
                        user_id,
                        round_no
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO coach_exam_round
                        (
                            exam_session_id,
                            user_id,
                            round_no,
                            dimension,
                            ai_question,
                            answer_analysis,
                            ai_reply,
                            user_answer,
                            round_score,
                            scenario,
                            create_time
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                    """, (
                        session_id,
                        user_id,
                        round_no,
                        dimension,
                        ai_question,
                        answer_analysis,
                        ai_reply,
                        user_answer,
                        round_score,
                        scenario
                    ))

                total_score += round_score  # 累加所有单题得分，得到总分
            
            # 更新会话表的总分 + 结束状态
            cursor.execute("""
                UPDATE coach_exam_session 
                SET status=2, finish_time=NOW(), total_score=%s 
                WHERE id=%s
            """, (total_score, session_id))
            conn.commit()
    
    return {"success": True, "msg": "答案提交成功", "session_id": session_id, "total_score": total_score}

# 完成考试
@router.post("/finish")
def finish_exam(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE coach_exam_session
                SET status=2, finish_time=%s
                WHERE id=%s
                """,
                (datetime.now(), data.get("session_id"))
            )
            conn.commit()

    return {"success": True}

# 2. 获取结果接口：从会话表取总分，从单题表取每道题得分
@router.get("/result")
def get_result(
    session_id: int,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        with conn.cursor() as cursor:
            # 1. 取总分（会话级）
            cursor.execute("SELECT total_score FROM coach_exam_session WHERE id=%s", (session_id,))
            total_score = cursor.fetchone()["total_score"] or 0
            
            # 2. 取每道题的得分（单题级）
            cursor.execute("""
                SELECT round_no, round_score, user_answer ,dimension, ai_question, answer_analysis, ai_reply, scenario
                FROM coach_exam_round 
                WHERE exam_session_id=%s
                ORDER BY round_no ASC
            """, (session_id,))
            round_details = cursor.fetchall()  # 每道题的得分详情
    
    return {
        "total_score": total_score,  # 总分
        "round_details": round_details,  # 每道题的得分列表
        "scores": [{"dimension": "综合能力", "score": total_score, "comment": "得分合格"}]  # 兼容原有前端逻辑
    }


