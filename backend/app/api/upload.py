from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
import os
from datetime import datetime
import hashlib
from utils.jwt import get_current_user
from app.core.db import get_db

router = APIRouter(prefix="/upload", tags=["upload"])

# 确保上传目录存在
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/file")
def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        # 计算文件哈希值
        file_hash = hashlib.md5(content).hexdigest()
        
        # 保存到数据库
        user_id = current_user.get("user_id")
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO coach_file_upload (user_id, file_name, file_path, file_size, file_type, file_hash)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, file.filename, file_path, len(content), file.content_type, file_hash)
                )
                conn.commit()
        
        return {
            "success": True,
            "message": "文件上传成功",
            "filename": filename,
            "size": len(content)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"文件上传失败: {str(e)}"
        }

@router.get("/list")
def get_file_list(page: int = 1, pageSize: int = 10, search: str = "", current_user: dict = Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # 构建查询条件
                where_clause = ""
                params = []
                
                if search:
                    where_clause = "WHERE coach_user.username LIKE %s"
                    params.append(f"%{search}%")
                
                # 查询总记录数
                cursor.execute(
                    f"""
                    SELECT COUNT(*) as total
                    FROM coach_file_upload
                    LEFT JOIN coach_user ON coach_file_upload.user_id = coach_user.id
                    {where_clause}
                    """,
                    params
                )
                total_result = cursor.fetchone()
                total = total_result["total"] if total_result else 0
                
                # 计算偏移量
                offset = (page - 1) * pageSize
                
                # 查询分页数据
                query_params = params + [pageSize, offset]
                cursor.execute(
                    f"""
                    SELECT 
                        coach_file_upload.id, 
                        coach_file_upload.user_id, 
                        coach_user.username,
                        coach_file_upload.file_name as name, 
                        coach_file_upload.file_path, 
                        coach_file_upload.file_size as size, 
                        coach_file_upload.file_type as type, 
                        coach_file_upload.create_time as uploadTime
                    FROM coach_file_upload
                    LEFT JOIN coach_user ON coach_file_upload.user_id = coach_user.id
                    {where_clause}
                    ORDER BY coach_file_upload.create_time DESC
                    LIMIT %s OFFSET %s
                    """,
                    query_params
                )
                files = cursor.fetchall()
        
        # 转换为字典列表
        file_list = []
        for file in files:
            file_dict = {
                "id": file["id"],
                "userId": file["user_id"],
                "username": file["username"],
                "name": file["name"],
                "path": file["file_path"],
                "size": file["size"],
                "type": file["type"],
                "uploadTime": file["uploadTime"].strftime("%Y-%m-%d %H:%M:%S") if file["uploadTime"] else None
            }
            file_list.append(file_dict)
        
        return {
            "success": True,
            "files": file_list,
            "total": total
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取文件列表失败: {str(e)}"
        }

@router.get("/download/{file_id}")
def download_file(file_id: int, current_user: dict = Depends(get_current_user)):
    try:
        # 从数据库中获取文件信息
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT file_path, file_name FROM coach_file_upload WHERE id = %s
                    """,
                    (file_id,)
                )
                file = cursor.fetchone()
                
                if not file:
                    return {
                        "success": False,
                        "message": "文件不存在"
                    }
                
                file_path = file[0]
                file_name = file[1]
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "message": "文件不存在"
                    }
                
                # 返回文件
                return FileResponse(
                    path=file_path,
                    filename=file_name,
                    media_type='application/octet-stream'
                )
    except Exception as e:
        return {
            "success": False,
            "message": f"文件下载失败: {str(e)}"
        }

@router.post("/delete")
def delete_file(file_id: int, current_user: dict = Depends(get_current_user)):
    try:
        # 从数据库中获取文件信息
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT file_path FROM coach_file_upload WHERE id = %s
                    """,
                    (file_id,)
                )
                file = cursor.fetchone()
                
                if not file:
                    return {
                        "success": False,
                        "message": "文件不存在"
                    }
                
                # 删除文件
                file_path = file[0]
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 从数据库中删除记录
                cursor.execute(
                    """
                    DELETE FROM coach_file_upload WHERE id = %s
                    """,
                    (file_id,)
                )
                conn.commit()
        
        return {
            "success": True,
            "message": "文件删除成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"文件删除失败: {str(e)}"
        }

