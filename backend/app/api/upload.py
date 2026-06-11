from fastapi import APIRouter, UploadFile, File, Depends, Body
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

# 岗位到表名的映射
ROLE_TABLE_MAP = {
    1: "coach_file_upload_shop_development",    # 商铺开发
    2: "coach_file_upload_door_service",         # 上门服务
    3: "coach_file_upload_brand_development",    # 品牌开发
    4: "coach_file_upload_shop_investment",      # 商铺招商
    5: "coach_file_upload_brand_location"        # 品牌选址
}

@router.post("/file")
def upload_file(file: UploadFile = File(...), category: str = Body("other"), role: int = Body(1), current_user: dict = Depends(get_current_user)):
    try:
        # 文件大小限制：500MB
        MAX_FILE_SIZE = 500 * 1024 * 1024
        
        # 验证岗位参数
        if role not in [1, 2, 3, 4, 5]:
            return {
                "success": False,
                "message": "无效的岗位选择"
            }
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # 保存文件
        with open(file_path, "wb") as f:
            content = file.file.read()
            
            # 检查文件大小
            if len(content) > MAX_FILE_SIZE:
                # 删除已写入的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    "success": False,
                    "message": "文件大小不能超过500MB"
                }
                
            f.write(content)

        # 计算文件哈希值
        file_hash = hashlib.md5(content).hexdigest()

        # 根据岗位选择对应的表
        table_name = ROLE_TABLE_MAP[role]
        
        # 保存到数据库
        user_id = current_user.get("user_id")
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {table_name} (user_id, file_name, file_path, file_size, file_type, category, file_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, file.filename, file_path, len(content), file.content_type, category, file_hash)
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
def get_file_list(page: int = 1, pageSize: int = 10, search: str = "", role: int = None, current_user: dict = Depends(get_current_user)):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # 从所有5个岗位表中查询文件
                all_files = []
                
                # 如果指定了角色，只查询该角色对应的表
                if role and role in ROLE_TABLE_MAP:
                    tables_to_query = [(role, ROLE_TABLE_MAP[role])]
                else:
                    # 查询所有岗位表
                    tables_to_query = ROLE_TABLE_MAP.items()
                
                for role_val, table_name in tables_to_query:
                    # 构建查询条件
                    where_clause = ""
                    params = []

                    if search:
                        where_clause = "WHERE file_name LIKE %s"
                        params.append(f"%{search}%")

                    # 查询该岗位的所有文件
                    query = f"""
                        SELECT
                            id,
                            user_id,
                            file_name as name,
                            file_path,
                            file_size as size,
                            file_type as type,
                            category,
                            create_time as uploadTime,
                            {role_val} as role
                        FROM {table_name}
                        {where_clause}
                        ORDER BY create_time DESC
                    """
                    
                    cursor.execute(query, params)
                    files = cursor.fetchall()
                    
                    # 添加岗位标识
                    for file in files:
                        all_files.append(file)

                # 按创建时间排序（最新的在前）
                all_files.sort(key=lambda x: x["uploadTime"], reverse=True)
                
                # 查询用户名
                user_ids = list(set([f["user_id"] for f in all_files]))
                user_map = {}
                if user_ids:
                    placeholders = ",".join(["%s"] * len(user_ids))
                    cursor.execute(
                        f"SELECT id, username FROM coach_user WHERE id IN ({placeholders})",
                        user_ids
                    )
                    users = cursor.fetchall()
                    user_map = {u["id"]: u["username"] for u in users}

                # 计算总记录数
                total = len(all_files)

                # 计算分页
                offset = (page - 1) * pageSize
                paginated_files = all_files[offset:offset + pageSize]

                # 转换为字典列表
                file_list = []
                for file in paginated_files:
                    file_dict = {
                        "id": file["id"],
                        "userId": file["user_id"],
                        "username": user_map.get(file["user_id"], ""),
                        "name": file["name"],
                        "path": file["file_path"],
                        "size": file["size"],
                        "type": file["type"],
                        "category": file["category"],
                        "role": file["role"],
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
def download_file(file_id: int):
    try:
        # 从所有5个岗位表中查找文件
        with get_db() as conn:
            with conn.cursor() as cursor:
                file = None
                for table_name in ROLE_TABLE_MAP.values():
                    cursor.execute(
                        f"""
                        SELECT file_path, file_name FROM {table_name} WHERE id = %s
                        """,
                        (file_id,)
                    )
                    file = cursor.fetchone()
                    if file:
                        break

                if not file:
                    return {
                        "success": False,
                        "message": "文件不存在"
                    }

                file_path = file['file_path']
                file_name = file['file_name']

                # 检查文件是否存在
                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "message": "文件不存在"
                    }

                # 根据文件扩展名设置适当的 media type
                import mimetypes
                extension = os.path.splitext(file_name)[1].lower()
                media_type, _ = mimetypes.guess_type(file_name)
                if not media_type:
                    # 对于常见文件类型，手动设置 media type
                    if extension in ['.txt', '.md', '.log']:
                        media_type = 'text/plain'
                    elif extension in ['.html', '.htm']:
                        media_type = 'text/html'
                    elif extension in ['.css']:
                        media_type = 'text/css'
                    elif extension in ['.js']:
                        media_type = 'application/javascript'
                    elif extension in ['.json']:
                        media_type = 'application/json'
                    elif extension in ['.xml']:
                        media_type = 'application/xml'
                    elif extension in ['.csv']:
                        media_type = 'text/csv'
                    elif extension in ['.pdf']:
                        media_type = 'application/pdf'
                    elif extension in ['.doc', '.docx']:
                        media_type = 'application/msword'
                    elif extension in ['.xls', '.xlsx']:
                        media_type = 'application/vnd.ms-excel'
                    elif extension in ['.ppt', '.pptx']:
                        media_type = 'application/vnd.ms-powerpoint'
                    elif extension in ['.jpg', '.jpeg']:
                        media_type = 'image/jpeg'
                    elif extension in ['.png']:
                        media_type = 'image/png'
                    elif extension in ['.gif']:
                        media_type = 'image/gif'
                    elif extension in ['.mp4']:
                        media_type = 'video/mp4'
                    elif extension in ['.mp3']:
                        media_type = 'audio/mpeg'
                    else:
                        media_type = 'application/octet-stream'
                
                # 使用FileResponse返回文件
                import urllib.parse
                
                # 对文件名进行URL编码，处理非ASCII字符
                encoded_filename = urllib.parse.quote(file_name)
                
                # 设置Content-Disposition为attachment，强制下载
                headers = {
                    'Content-Disposition': f'attachment; filename="{encoded_filename}"; filename*=UTF-8''\'{encoded_filename}\''
                }
                
                return FileResponse(
                    path=file_path,
                    media_type=media_type,
                    headers=headers
                )
    except Exception as e:
        return {
            "success": False,
            "message": f"文件下载失败: {str(e)}"
        }

@router.post("/delete")
def delete_file(id: int = Body(..., embed=True), current_user: dict = Depends(get_current_user)):
    try:
        # 验证 id 是否为正整数
        if not isinstance(id, int) or id <= 0:
            return {
                "success": False,
                "message": "无效的文件 ID"
            }

        # 从所有5个岗位表中查找文件
        with get_db() as conn:
            with conn.cursor() as cursor:
                try:
                    file = None
                    found_table = None  # 记录找到文件的表名
                    for table_name in ROLE_TABLE_MAP.values():
                        cursor.execute(
                            f"""
                            SELECT file_path FROM {table_name} WHERE id = %s
                            """,
                            (id,)
                        )
                        file = cursor.fetchone()
                        if file:
                            found_table = table_name
                            break

                    if not file:
                        return {
                            "success": False,
                            "message": "文件不存在"
                        }

                    # 删除文件
                    file_path = file['file_path']
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception:
                            # 即使文件删除失败，也继续删除数据库记录
                            pass

                    # 只从找到文件的那个表中删除记录
                    if found_table:
                        cursor.execute(
                            f"""
                            DELETE FROM {found_table} WHERE id = %s
                            """,
                            (id,)
                        )
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    return {
                        "success": False,
                        "message": f"数据库操作失败: {str(e)}"
                    }

        return {
            "success": True,
            "message": "文件删除成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"文件删除失败: {str(e)}"
        }


@router.post("/progress")
def update_progress(id: int = Body(..., embed=True), progress: int = Body(..., embed=True), learningTime: int = Body(0, embed=True), role: int = Body(1, embed=True), current_user: dict = Depends(get_current_user)):
    """更新用户文件学习进度"""
    try:
        user_id = current_user.get("user_id")
        
        # 验证参数
        if progress < 0:
            progress = 0
        elif progress > 100:
            progress = 100
        
        # 验证岗位参数
        if role not in [1, 2, 3, 4, 5]:
            role = 1
        
        is_completed = 1 if progress >= 100 else 0
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # 检查是否已存在记录（包含岗位信息）
                cursor.execute(
                    """
                    SELECT id, total_learning_time FROM coach_user_file_progress 
                    WHERE user_id = %s AND file_id = %s AND role = %s
                    """,
                    (user_id, id, role)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # 更新进度和学习时间（直接使用前端传递的学习时间）
                    total_time = learningTime
                    cursor.execute(
                        """
                        UPDATE coach_user_file_progress 
                        SET progress = %s, is_completed = %s, last_read_time = CURRENT_TIMESTAMP, total_learning_time = %s
                        WHERE user_id = %s AND file_id = %s AND role = %s
                        """,
                        (progress, is_completed, total_time, user_id, id, role)
                    )
                else:
                    # 插入新记录
                    total_time = learningTime
                    cursor.execute(
                        """
                        INSERT INTO coach_user_file_progress (user_id, file_id, progress, is_completed, total_learning_time, role)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (user_id, id, progress, is_completed, total_time, role)
                    )
                conn.commit()
        
        return {
            "success": True,
            "message": "进度更新成功",
            "progress": progress,
            "is_completed": is_completed,
            "learningTime": total_time if existing else learningTime
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"进度更新失败: {str(e)}"
        }


@router.get("/progress/{id}")
def get_progress(id: int, role: int = 1, current_user: dict = Depends(get_current_user)):
    """获取用户文件学习进度"""
    try:
        user_id = current_user.get("user_id")
        
        # 验证岗位参数
        if role not in [1, 2, 3, 4, 5]:
            role = 1
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT progress, is_completed, last_read_time, total_learning_time 
                    FROM coach_user_file_progress 
                    WHERE user_id = %s AND file_id = %s AND role = %s
                    """,
                    (user_id, id, role)
                )
                result = cursor.fetchone()
                
                if result:
                    return {
                        "success": True,
                        "progress": result["progress"],
                        "isCompleted": result["is_completed"],
                        "lastReadTime": result["last_read_time"].strftime("%Y-%m-%d %H:%M:%S") if result["last_read_time"] else None,
                        "learningTime": result["total_learning_time"]
                    }
                else:
                    return {
                        "success": True,
                        "progress": 0,
                        "isCompleted": 0,
                        "lastReadTime": None,
                        "learningTime": 0
                    }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取进度失败: {str(e)}"
        }


@router.get("/learning-status")
def get_learning_status(page: int = 1, pageSize: int = 10, search: str = "", current_user: dict = Depends(get_current_user)):
    """获取所有用户的学习情况（管理员用）"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # 构建联合查询所有岗位文件表（包含岗位信息）
                union_files_query = """
                    SELECT id, file_name, file_type, 1 as role FROM coach_file_upload_shop_development
                    UNION ALL
                    SELECT id, file_name, file_type, 2 as role FROM coach_file_upload_door_service
                    UNION ALL
                    SELECT id, file_name, file_type, 3 as role FROM coach_file_upload_brand_development
                    UNION ALL
                    SELECT id, file_name, file_type, 4 as role FROM coach_file_upload_shop_investment
                    UNION ALL
                    SELECT id, file_name, file_type, 5 as role FROM coach_file_upload_brand_location
                """

                # 构建查询条件
                where_clause = ""
                params = []

                if search:
                    where_clause = "WHERE coach_user.username LIKE %s OR files.file_name LIKE %s"
                    params.extend([f"%{search}%", f"%{search}%"])

                # 查询总记录数
                cursor.execute(
                    f"""
                    SELECT COUNT(*) as total
                    FROM coach_user_file_progress
                    LEFT JOIN coach_user ON coach_user_file_progress.user_id = coach_user.id
                    LEFT JOIN ({union_files_query}) as files ON coach_user_file_progress.file_id = files.id AND coach_user_file_progress.role = files.role
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
                        coach_user_file_progress.id,
                        coach_user.id as user_id,
                        coach_user.username,
                        coach_user.nickname,
                        coach_user.role as user_role,
                        files.id as file_id,
                        files.file_name as file_name,
                        files.file_type as file_type,
                        coach_user_file_progress.role,
                        coach_user_file_progress.progress,
                        coach_user_file_progress.is_completed,
                        coach_user_file_progress.last_read_time,
                        coach_user_file_progress.total_learning_time
                    FROM coach_user_file_progress
                    LEFT JOIN coach_user ON coach_user_file_progress.user_id = coach_user.id
                    LEFT JOIN ({union_files_query}) as files ON coach_user_file_progress.file_id = files.id AND coach_user_file_progress.role = files.role
                    {where_clause}
                    ORDER BY coach_user_file_progress.last_read_time DESC
                    LIMIT %s OFFSET %s
                    """,
                    query_params
                )
                records = cursor.fetchall()

        # 转换为字典列表
        record_list = []
        for record in records:
            record_dict = {
                "id": record["id"],
                "userId": record["user_id"],
                "username": record["username"],
                "nickname": record["nickname"],
                "userRole": record["user_role"],
                "fileId": record["file_id"],
                "fileName": record["file_name"],
                "fileType": record["file_type"],
                "role": record["role"],
                "progress": record["progress"],
                "isCompleted": record["is_completed"],
                "lastReadTime": record["last_read_time"].strftime("%Y-%m-%d %H:%M:%S") if record["last_read_time"] else None,
                "learningTime": record["total_learning_time"]
            }
            record_list.append(record_dict)

        return {
            "success": True,
            "records": record_list,
            "total": total
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取学习情况失败: {str(e)}"
        }

@router.get("/my-learning-records")
def get_my_learning_records(current_user: dict = Depends(get_current_user)):
    """获取当前用户的学习记录"""
    try:
        user_id = current_user.get("user_id")

        # 构建联合查询所有岗位文件表（包含岗位信息）
        union_files_query = """
            SELECT id, file_name, file_type, 1 as role FROM coach_file_upload_shop_development
            UNION ALL
            SELECT id, file_name, file_type, 2 as role FROM coach_file_upload_door_service
            UNION ALL
            SELECT id, file_name, file_type, 3 as role FROM coach_file_upload_brand_development
            UNION ALL
            SELECT id, file_name, file_type, 4 as role FROM coach_file_upload_shop_investment
            UNION ALL
            SELECT id, file_name, file_type, 5 as role FROM coach_file_upload_brand_location
        """

        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        coach_user_file_progress.id,
                        files.file_name as file_name,
                        files.file_type as file_type,
                        coach_user_file_progress.progress,
                        coach_user_file_progress.is_completed,
                        coach_user_file_progress.last_read_time,
                        coach_user_file_progress.total_learning_time
                    FROM coach_user_file_progress
                    LEFT JOIN ({union_files_query}) as files ON coach_user_file_progress.file_id = files.id AND coach_user_file_progress.role = files.role
                    WHERE coach_user_file_progress.user_id = %s
                    ORDER BY coach_user_file_progress.last_read_time DESC
                    """,
                    (user_id,)
                )
                records = cursor.fetchall()

        # 转换为前端需要的格式
        record_list = []
        for record in records:
            # 格式化学习时长
            total_time = record.get("total_learning_time") or 0
            if total_time >= 60:
                duration_str = f"{total_time // 60}小时{total_time % 60}分钟" if total_time % 60 > 0 else f"{total_time // 60}小时"
            else:
                duration_str = f"{total_time}分钟"

            record_list.append({
                "date": record["last_read_time"].strftime("%Y-%m-%d") if record["last_read_time"] else "",
                "progress": record.get("progress") or 0,
                "content": record["file_name"] or "未知文件",
                "duration": duration_str
            })

        return {
            "success": True,
            "records": record_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取学习记录失败: {str(e)}"
        }