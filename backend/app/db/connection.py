"""
資料庫連線管理模組
"""
import os
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Optional

from langchain_community.utilities import SQLDatabase

from app.config import get_settings


def get_db_path() -> str:
    """獲取資料庫檔案路徑"""
    settings = get_settings()
    db_url = settings.database_url
    
    # 从 sqlite:///./data/app.db 提取路径
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "")
    return "./data/app.db"


def ensure_data_dir():
    """確保數據目錄存在分"""
    db_path = get_db_path()
    data_dir = os.path.dirname(db_path)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)


@lru_cache
def get_sql_database() -> SQLDatabase:
    """
    獲取 SQLDatabase 實例（用於 LangChain Agent）
    
    Returns:
        SQLDatabase 實例
    """
    settings = get_settings()
    ensure_data_dir()
    
    db_path = get_db_path()
    
    # 检查是否需要初始化示例数据
    need_init = False
    if not os.path.exists(db_path):
        need_init = True
    else:
        # 检查 sales 表是否存在
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        if not cursor.fetchone():
            need_init = True
        conn.close()
    
    if need_init:
        init_sample_database(db_path)
    
    return SQLDatabase.from_uri(settings.database_url)


def get_raw_connection() -> sqlite3.Connection:
    """
    獲取原生 SQLite 連線（用於會話存儲等）
    
    Returns:
        sqlite3.Connection
    """
    ensure_data_dir()
    db_path = get_db_path()
    return sqlite3.connect(db_path, check_same_thread=False)


def init_sample_database(db_path: str):
    """
    初始化範例資料庫
    
    建立銷售數據表並插入範例數據
    """
    print(f"Initializing sample database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建销售表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            sale_date DATE NOT NULL,
            region TEXT NOT NULL
        )
    """)
    
    # 创建员工表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL,
            hire_date DATE NOT NULL
        )
    """)
    
    # 创建会话表（用于持久化）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建消息表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sql_query TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    
    # 插入销售示例数据
    sales_data = [
        ('筆記型電腦', '電子產品', 15, 5999.00, '2024-01-15', '華東'),
        ('無線滑鼠', '電子產品', 80, 99.00, '2024-01-15', '華東'),
        ('機械鍵盤', '電子產品', 45, 299.00, '2024-01-16', '華北'),
        ('顯示器', '電子產品', 20, 1299.00, '2024-01-17', '華南'),
        ('辦公椅', '家具', 30, 599.00, '2024-01-18', '華東'),
        ('辦公桌', '家具', 15, 899.00, '2024-01-18', '華北'),
        ('列印紙', '辦公用品', 200, 29.00, '2024-01-19', '華南'),
        ('原子筆', '辦公用品', 500, 5.00, '2024-01-19', '華東'),
        ('資料夾', '辦公用品', 300, 15.00, '2024-01-20', '華北'),
        ('檯燈', '家具', 40, 199.00, '2024-01-20', '華南'),
        ('平板電腦', '電子產品', 25, 3299.00, '2024-01-21', '華東'),
        ('耳機', '電子產品', 60, 199.00, '2024-01-22', '華北'),
        ('投影機', '電子產品', 8, 2999.00, '2024-01-23', '華南'),
        ('書架', '家具', 12, 399.00, '2024-01-24', '華東'),
        ('白板', '辦公用品', 25, 149.00, '2024-01-25', '華北'),
    ]
    
    cursor.executemany(
        "INSERT INTO sales (product_name, category, quantity, price, sale_date, region) VALUES (?, ?, ?, ?, ?, ?)",
        sales_data
    )
    
    # 插入员工示例数据
    employees_data = [
        ('張偉', '技術部', '高級工程師', 25000.00, '2020-03-15'),
        ('李娜', '技術部', '工程師', 18000.00, '2021-06-20'),
        ('王芳', '市場部', '市場經理', 22000.00, '2019-08-10'),
        ('劉洋', '市場部', '市場專員', 12000.00, '2022-01-05'),
        ('陳明', '財務部', '財務主管', 20000.00, '2018-11-20'),
        ('趙麗', '財務部', '會計', 15000.00, '2021-04-15'),
        ('孫強', '人事部', '人事經理', 18000.00, '2020-07-01'),
        ('周傑', '技術部', '技術總監', 35000.00, '2017-02-28'),
    ]
    
    cursor.executemany(
        "INSERT INTO employees (name, department, position, salary, hire_date) VALUES (?, ?, ?, ?, ?)",
        employees_data
    )
    
    conn.commit()
    conn.close()
    
    print(f"Sample database initialized with {len(sales_data)} sales records and {len(employees_data)} employees.")


def get_database_schema() -> dict:
    """
    获取数据库结构信息
    
    Returns:
        包含表结构的字典
    """
    db = get_sql_database()
    tables = db.get_usable_table_names()
    
    schema = {
        "dialect": db.dialect,
        "tables": []
    }
    
    conn = get_raw_connection()
    cursor = conn.cursor()
    
    for table in tables:
        # 跳过内部表
        if table.startswith("chat_"):
            continue
            
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # 获取行数
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        
        table_info = {
            "name": table,
            "columns": [
                {
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ],
            "row_count": row_count
        }
        schema["tables"].append(table_info)
    
    conn.close()
    return schema
