from fastapi import APIRouter, Depends
from app.core.db import get_db
from utils.jwt import get_current_user
from datetime import datetime
import json

router = APIRouter(prefix="/exam", tags=["Exam"])

# 获取随机题目（正式考试用）
@router.get("/random_questions")
def get_random_questions(
    role: int = None,
    current_user: dict = Depends(get_current_user)
):
    """
    从题库中随机获取题目：单选题10题、判断题10题、多选题5题
    题目范围：通用题目 + 对应用户角色的题目
    """
    user_id = current_user.get("user_id")
    
    # 如果没有传入角色，从用户表获取
    if role is None:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT role FROM coach_user WHERE id=%s", (user_id,))
                user = cursor.fetchone()
                if user:
                    role = user.get("role", 0)
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # 构建分类条件：通用题目(0) + 对应角色的题目(role)
            category_condition = "category = 0"
            if role and role != 0:
                category_condition = f"(category = 0 OR category = {role})"
            
            # 获取单选题（10题）
            cursor.execute(f"""
                SELECT id, question, answer, type, options, difficulty, category 
                FROM coach_question_bank 
                WHERE status = 1 AND type = 'single' AND {category_condition}
                ORDER BY RAND() LIMIT 10
            """)
            single_questions = cursor.fetchall()
            
            # 获取判断题（10题）
            cursor.execute(f"""
                SELECT id, question, answer, type, options, difficulty, category 
                FROM coach_question_bank 
                WHERE status = 1 AND type = 'judge' AND {category_condition}
                ORDER BY RAND() LIMIT 10
            """)
            judge_questions = cursor.fetchall()
            
            # 获取多选题（5题）
            cursor.execute(f"""
                SELECT id, question, answer, type, options, difficulty, category 
                FROM coach_question_bank 
                WHERE status = 1 AND type = 'multiple' AND {category_condition}
                ORDER BY RAND() LIMIT 5
            """)
            multiple_questions = cursor.fetchall()
            
            # 合并题目并打乱顺序
            all_questions = []
            
            # 添加单选题
            for q in single_questions:
                all_questions.append({
                    "id": q["id"],
                    "question": q["question"],
                    "options": q["options"] if q["options"] else [],
                    "answer": q["answer"],
                    "type": q["type"]
                })
            
            # 添加判断题
            for q in judge_questions:
                all_questions.append({
                    "id": q["id"],
                    "question": q["question"],
                    "answer": q["answer"],
                    "type": q["type"]
                })
            
            # 添加多选题
            for q in multiple_questions:
                all_questions.append({
                    "id": q["id"],
                    "question": q["question"],
                    "options": q["options"] if q["options"] else [],
                    "answer": q["answer"],
                    "type": q["type"]
                })
            
            # 打乱题目顺序
            import random
            random.shuffle(all_questions)
            
            return {
                "success": True,
                "questions": all_questions,
                "counts": {
                    "single": len(single_questions),
                    "judge": len(judge_questions),
                    "multiple": len(multiple_questions)
                }
            }

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

# 提交答案（AI训练模式，保留原有逻辑）
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
            cursor.execute("SELECT status, exam_mode FROM coach_exam_session WHERE id=%s AND user_id=%s", (session_id, user_id))
            session = cursor.fetchone()
            if not session or session["status"] != 1:
                return {"success": False, "msg": "考试已结束/不存在，无法提交"}
            
            exam_mode = session.get("exam_mode", "")
            
            # 2. 批量更新每轮的用户答案
            total_score = 0  # 临时计算总分
            for item in round_answers:
                round_no = item.get("round_no")
                if not isinstance(round_no, int):
                    raise ValueError(f"round_no 非法: {round_no}")

                dimension = item.get("dimension") or "综合能力"
                ai_question = item.get("ai_question", "")
                scenario = item.get("scenario", "")
                answer_analysis = item.get("answer_analysis", "")
                ai_reply = item.get("ai_reply", "")
                
                user_answer = item.get("answer")
                if user_answer is not None and not isinstance(user_answer, str):
                    user_answer = json.dumps(user_answer, ensure_ascii=False)

                # 根据考试模式计算得分
                if exam_mode == 'comprehensive' and item.get("question_id"):
                    # 正式考试：后端校验答案并计算分数
                    question_id = item.get("question_id")
                    cursor.execute("""
                        SELECT answer, type FROM coach_question_bank WHERE id=%s
                    """, (question_id,))
                    question = cursor.fetchone()
                    
                    if question:
                        correct_answer = question["answer"]
                        question_type = question["type"]
                        # 根据题目类型确定分值
                        if question_type == 'multiple':
                            question_score = 8  # 多选题8分
                        else:
                            question_score = 3  # 单选和判断题3分
                        
                        # 比对答案（多选题需要排序后比较）
                        user_ans = str(user_answer or "").strip().upper()
                        correct_ans = str(correct_answer).strip().upper()
                        
                        # 多选题答案排序后比较
                        if user_ans and correct_ans:
                            user_sorted = ''.join(sorted(user_ans))
                            correct_sorted = ''.join(sorted(correct_ans))
                            round_score = question_score if user_sorted == correct_sorted else 0
                        else:
                            round_score = question_score if user_ans == correct_ans else 0
                    else:
                        round_score = 0
                else:
                    # AI训练模式：使用前端传入的分数（原有逻辑）
                    round_score = int(item.get("round_score", 0))

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

# 直接结算并保存考试结果到 coach_exam_result 表（不使用 coach_exam_session 表）
@router.post("/save_result")
def save_exam_result(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    exam_date = data.get("exam_date")
    duration = data.get("duration")
    exam_mode = data.get("exam_mode", "comprehensive")
    round_answers = data.get("round_answers", [])
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # 直接计算总分和统计数据（不使用任何中间表）
            total_score = 0
            correct_count = 0
            wrong_count = 0
            unanswered_count = 0
            
            for item in round_answers:
                user_answer = item.get("answer", "")
                question_id = item.get("question_id")
                
                if not user_answer or user_answer.strip() == "":
                    unanswered_count += 1
                    continue
                
                # 根据题目ID查询正确答案并计算得分
                if exam_mode == 'comprehensive' and question_id:
                    cursor.execute("""
                        SELECT answer, type FROM coach_question_bank WHERE id=%s
                    """, (question_id,))
                    question = cursor.fetchone()
                    
                    if question:
                        correct_answer = question["answer"]
                        question_type = question["type"]
                        
                        # 根据题目类型确定分值
                        if question_type == 'multiple':
                            question_score = 8
                        else:
                            question_score = 3
                        
                        # 比对答案（多选题排序后比较）
                        user_ans = str(user_answer).strip().upper()
                        correct_ans = str(correct_answer).strip().upper()
                        
                        if user_ans and correct_ans:
                            user_sorted = ''.join(sorted(user_ans))
                            correct_sorted = ''.join(sorted(correct_ans))
                            round_score = question_score if user_sorted == correct_sorted else 0
                        else:
                            round_score = question_score if user_ans == correct_ans else 0
                    else:
                        round_score = 0
                else:
                    round_score = int(item.get("round_score", 0))
                
                total_score += round_score
                
                if round_score > 0:
                    correct_count += 1
                else:
                    wrong_count += 1
            
            # 计算正确率
            answered_count = correct_count + wrong_count
            accuracy = round((correct_count / answered_count) * 100, 1) if answered_count > 0 else 0
            
            # 直接插入考试结果到结果表（不使用 coach_exam_session）
            cursor.execute("""
                INSERT INTO coach_exam_result (
                    user_id,
                    total_score,
                    exam_date,
                    duration,
                    correct_count,
                    wrong_count,
                    unanswered_count,
                    accuracy,
                    exam_mode
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                total_score,
                exam_date,
                duration,
                correct_count,
                wrong_count,
                unanswered_count,
                accuracy,
                exam_mode
            ))
            conn.commit()
    
    return {
        "success": True, 
        "msg": "考试结果保存成功",
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "unanswered_count": unanswered_count,
        "accuracy": accuracy,
        "total_score": total_score
    }

# 获取历史成绩列表
@router.get("/history")
def get_exam_history(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    获取用户的历史考试成绩列表
    """
    user_id = current_user.get("user_id")
    offset = (page - 1) * page_size

    with get_db() as conn:
        with conn.cursor() as cursor:
            # 获取总数
            cursor.execute(
                "SELECT COUNT(*) as total FROM coach_exam_result WHERE user_id=%s",
                (user_id,)
            )
            total = cursor.fetchone()["total"]

            # 获取历史成绩列表
            cursor.execute("""
                SELECT 
                    id,
                    total_score,
                    exam_date,
                    duration,
                    correct_count,
                    wrong_count,
                    unanswered_count,
                    accuracy,
                    exam_mode,
                    create_time
                FROM coach_exam_result
                WHERE user_id=%s
                ORDER BY create_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, page_size, offset))
            results = cursor.fetchall()

            # 格式化日期
            history_list = []
            for item in results:
                history_list.append({
                    "id": item["id"],
                    "total_score": item["total_score"],
                    "exam_date": item["exam_date"].strftime("%Y-%m-%d %H:%M:%S") if item["exam_date"] else None,
                    "duration": item["duration"],
                    "correct_count": item["correct_count"],
                    "wrong_count": item["wrong_count"],
                    "unanswered_count": item["unanswered_count"],
                    "accuracy": float(item["accuracy"]) if item["accuracy"] else 0,
                    "exam_mode": item["exam_mode"],
                    "create_time": item["create_time"].strftime("%Y-%m-%d %H:%M:%S") if item["create_time"] else None
                })

    return {
        "success": True,
        "total": total,
        "page": page,
        "page_size": page_size,
        "history": history_list
    }


