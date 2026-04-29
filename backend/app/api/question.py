from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from app.core.db import get_db
from app.api.user import get_current_user
import os

router = APIRouter(prefix="/question")

# 获取题目列表
@router.get("/list")
def get_question_list(page: int = 1, page_size: int = 10, search: str = "", current_user: dict = Depends(get_current_user)):
    try:
        offset = (page - 1) * page_size
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # 构建查询条件
                where_clause = "WHERE q.status = 1"
                params = []
                
                if search:
                    where_clause += " AND (q.question LIKE %s OR q.category LIKE %s)"
                    params.extend([f"%{search}%", f"%{search}%"])
                
                # 查询总记录数
                cursor.execute(f"SELECT COUNT(*) FROM coach_question_bank q {where_clause}", params)
                total = cursor.fetchone()["COUNT(*)"]
                
                # 查询分页数据（关联用户表获取上传人名称）
                query_params = params + [page_size, offset]
                cursor.execute(
                    f"""
                    SELECT 
                        q.id, q.question, q.options, q.answer, q.type, q.category, 
                        q.difficulty, q.status, q.create_time, q.update_time, q.user_id,
                        u.username as uploader_name
                    FROM coach_question_bank q
                    LEFT JOIN coach_user u ON q.user_id = u.id
                    {where_clause}
                    ORDER BY q.create_time DESC
                    LIMIT %s OFFSET %s
                    """,
                    query_params
                )
                questions = cursor.fetchall()
        
        # 转换为字典列表
        question_list = []
        for question in questions:
            question_dict = {
                "id": question["id"],
                "question": question["question"],
                "options": question["options"],
                "answer": question["answer"],
                "type": question["type"],
                "category": question["category"],
                "difficulty": question["difficulty"],
                "status": question["status"],
                "userId": question["user_id"],
                "uploaderName": question["uploader_name"] or "未知",
                "createTime": question["create_time"].strftime("%Y-%m-%d %H:%M:%S") if question["create_time"] else None,
                "updateTime": question["update_time"].strftime("%Y-%m-%d %H:%M:%S") if question["update_time"] else None
            }
            question_list.append(question_dict)
        
        return {
            "success": True,
            "questions": question_list,
            "total": total
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"获取题目列表失败: {str(e)}"
        }

# 获取单个题目
@router.get("/{question_id}")
def get_question(question_id: int, current_user: dict = Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        id, question, options, answer, type, category, 
                        difficulty, status, create_time, update_time
                    FROM coach_question_bank 
                    WHERE id = %s AND status = 1
                    """,
                    (question_id,)
                )
                question = cursor.fetchone()
        
        if not question:
            return {"success": False, "message": "题目不存在"}
        
        question_dict = {
            "id": question["id"],
            "question": question["question"],
            "options": question["options"],
            "answer": question["answer"],
            "type": question["type"],
            "category": question["category"],
            "difficulty": question["difficulty"],
            "status": question["status"],
            "createTime": question["create_time"].strftime("%Y-%m-%d %H:%M:%S") if question["create_time"] else None,
            "updateTime": question["update_time"].strftime("%Y-%m-%d %H:%M:%S") if question["update_time"] else None
        }
        
        return {"success": True, "question": question_dict}
    
    except Exception as e:
        return {"success": False, "message": f"获取题目失败: {str(e)}"}

# 添加题目
@router.post("/add")
def add_question(
    question: str = Body(...),
    answer: str = Body(...),
    type: str = Body("single"),
    category: str = Body(...),
    difficulty: str = Body("medium"),
    options: str = Body(""),
    current_user: dict = Depends(get_current_user)
):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO coach_question_bank 
                    (question, options, answer, type, category, difficulty, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (question, options, answer, type, category, difficulty, current_user.get("id"))
                )
                conn.commit()
                question_id = cursor.lastrowid

        return {
            "success": True,
            "message": "添加成功",
            "questionId": question_id
        }
    
    except Exception as e:
        return {"success": False, "message": f"添加题目失败: {str(e)}"}

# 更新题目
@router.post("/update/{question_id}")
def update_question(
    question_id: int,
    question: str = Body(...),
    answer: str = Body(...),
    type: str = Body("single"),
    category: str = Body(...),
    difficulty: str = Body("medium"),
    options: str = Body(""),
    current_user: dict = Depends(get_current_user)
):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE coach_question_bank 
                    SET question = %s, options = %s, answer = %s, 
                        type = %s, category = %s, difficulty = %s, user_id = %s
                    WHERE id = %s
                    """,
                    (question, options, answer, type, category, difficulty, current_user.get("id"), question_id)
                )
                conn.commit()

        return {"success": True, "message": "更新成功"}
    
    except Exception as e:
        return {"success": False, "message": f"更新题目失败: {str(e)}"}

# 删除题目
@router.post("/delete/{question_id}")
def delete_question(question_id: int, current_user: dict = Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM coach_question_bank WHERE id = %s",
                    (question_id,)
                )
                conn.commit()
        
        return {"success": True, "message": "删除成功"}
    
    except Exception as e:
        return {"success": False, "message": f"删除题目失败: {str(e)}"}

# 获取题目分类列表
@router.get("/categories")
def get_categories(current_user: dict = Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT DISTINCT category FROM coach_question_bank WHERE status = 1 ORDER BY category"
                )
                categories = cursor.fetchall()
        
        category_list = [cat["category"] for cat in categories]
        return {"success": True, "categories": category_list}
    
    except Exception as e:
        return {"success": False, "message": f"获取分类列表失败: {str(e)}"}
