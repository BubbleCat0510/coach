# app/core/db.py
import os
import pymysql
import logging
from contextlib import contextmanager
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

logger = logging.getLogger(__name__)

# 从环境变量读取数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
    "connect_timeout": 5,
    "read_timeout": 10,
    "write_timeout": 10,
}

def _check_db_config():
    """启动时检查数据库配置是否完整"""
    missing = [k for k, v in DB_CONFIG.items() if v is None and k != "port"]
    if missing:
        raise RuntimeError(f"数据库配置缺失，请检查 .env 中的变量: {missing}")

_check_db_config()

@contextmanager
def get_db():
    """
    获取数据库连接（上下文管理器）

    用法：
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(...)
    """
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        yield conn
    except Exception as e:
        logger.error("数据库连接或执行失败: %s", e, exc_info=True)
        raise
    finally:
        if conn:
            conn.close()
