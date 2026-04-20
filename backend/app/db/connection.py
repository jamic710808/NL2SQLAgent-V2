"""
資料庫連線管理模組
"""
import os
from functools import lru_cache
from typing import Optional
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, DateTime, func, ForeignKey, text, inspect
from langchain_community.utilities import SQLDatabase

from app.config import get_settings

metadata = MetaData()

sales_table = Table(
    'sales', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('product_name', String, nullable=False),
    Column('category', String, nullable=False),
    Column('quantity', Integer, nullable=False),
    Column('price', Float, nullable=False),
    Column('sale_date', Date, nullable=False),
    Column('region', String, nullable=False),
)

employees_table = Table(
    'employees', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('department', String, nullable=False),
    Column('position', String, nullable=False),
    Column('salary', Float, nullable=False),
    Column('hire_date', Date, nullable=False),
)

chat_sessions_table = Table(
    'chat_sessions', metadata,
    Column('id', String, primary_key=True),
    Column('title', String, nullable=False),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now()),
)

chat_messages_table = Table(
    'chat_messages', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('session_id', String, ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
    Column('role', String, nullable=False),
    Column('content', String, nullable=False),
    Column('sql_query', String, nullable=True),
    Column('created_at', DateTime, server_default=func.now()),
)

# 應用設定表（取代本地 JSON 檔案，以支援 Vercel 唯讀檔案系統）
app_settings_table = Table(
    'app_settings', metadata,
    Column('key', String, primary_key=True),
    Column('value', String, nullable=False),
)

def get_engine():
    settings = get_settings()
    db_url = settings.database_url
    
    if db_url.startswith("sqlite:///"):
        # 從 sqlite:///./data/app.db 提取路徑並確保目錄存在
        db_path = db_url.replace("sqlite:///", "")
        
        # 在 Vercel 上遇到 Read-only file system 時，將 SQLite 強制寫入 /tmp
        if os.environ.get("VERCEL") == "1" and not db_path.startswith("/tmp/"):
            db_path = "/tmp/app.db"
            db_url = f"sqlite:///{db_path}"
            
        data_dir = os.path.dirname(db_path)
        if data_dir:
            try:
                os.makedirs(data_dir, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create directory {data_dir}: {e}")
                
        kwargs = {"connect_args": {"check_same_thread": False}}
    else:
        kwargs = {}
        
    return create_engine(db_url, **kwargs)

@lru_cache
def get_sql_database() -> SQLDatabase:
    """獲取 SQLDatabase 實例（用於 LangChain Agent）"""
    engine = get_engine()
    
    inspector = inspect(engine)
    if "sales" not in inspector.get_table_names():
        init_sample_database(engine)
        
    # Langchain SQLDatabase wrapper
    return SQLDatabase(engine)

def get_raw_connection():
    """獲取 SQLAlchemy 連線（用於會話存儲等）"""
    return get_engine().connect()

def init_sample_database(engine):
    """初始化範例資料庫並建立表結構與資料"""
    print(f"Initializing sample database on {engine.url}")
    metadata.create_all(engine)
    
    sales_data = [
        {'product_name': '筆記型電腦', 'category': '電子產品', 'quantity': 15, 'price': 5999.00, 'sale_date': datetime(2024, 1, 15).date(), 'region': '華東'},
        {'product_name': '無線滑鼠', 'category': '電子產品', 'quantity': 80, 'price': 99.00, 'sale_date': datetime(2024, 1, 15).date(), 'region': '華東'},
        {'product_name': '機械鍵盤', 'category': '電子產品', 'quantity': 45, 'price': 299.00, 'sale_date': datetime(2024, 1, 16).date(), 'region': '華北'},
        {'product_name': '顯示器', 'category': '電子產品', 'quantity': 20, 'price': 1299.00, 'sale_date': datetime(2024, 1, 17).date(), 'region': '華南'},
        {'product_name': '辦公椅', 'category': '家具', 'quantity': 30, 'price': 599.00, 'sale_date': datetime(2024, 1, 18).date(), 'region': '華東'},
        {'product_name': '辦公桌', 'category': '家具', 'quantity': 15, 'price': 899.00, 'sale_date': datetime(2024, 1, 18).date(), 'region': '華北'},
        {'product_name': '列印紙', 'category': '辦公用品', 'quantity': 200, 'price': 29.00, 'sale_date': datetime(2024, 1, 19).date(), 'region': '華南'},
        {'product_name': '原子筆', 'category': '辦公用品', 'quantity': 500, 'price': 5.00, 'sale_date': datetime(2024, 1, 19).date(), 'region': '華東'},
        {'product_name': '資料夾', 'category': '辦公用品', 'quantity': 300, 'price': 15.00, 'sale_date': datetime(2024, 1, 20).date(), 'region': '華北'},
        {'product_name': '檯燈', 'category': '家具', 'quantity': 40, 'price': 199.00, 'sale_date': datetime(2024, 1, 20).date(), 'region': '華南'},
        {'product_name': '平板電腦', 'category': '電子產品', 'quantity': 25, 'price': 3299.00, 'sale_date': datetime(2024, 1, 21).date(), 'region': '華東'},
        {'product_name': '耳機', 'category': '電子產品', 'quantity': 60, 'price': 199.00, 'sale_date': datetime(2024, 1, 22).date(), 'region': '華北'},
        {'product_name': '投影機', 'category': '電子產品', 'quantity': 8, 'price': 2999.00, 'sale_date': datetime(2024, 1, 23).date(), 'region': '華南'},
        {'product_name': '書架', 'category': '家具', 'quantity': 12, 'price': 399.00, 'sale_date': datetime(2024, 1, 24).date(), 'region': '華東'},
        {'product_name': '白板', 'category': '辦公用品', 'quantity': 25, 'price': 149.00, 'sale_date': datetime(2024, 1, 25).date(), 'region': '華北'},
    ]
    
    employees_data = [
        {'name': '張偉', 'department': '技術部', 'position': '高級工程師', 'salary': 25000.00, 'hire_date': datetime(2020, 3, 15).date()},
        {'name': '李娜', 'department': '技術部', 'position': '工程師', 'salary': 18000.00, 'hire_date': datetime(2021, 6, 20).date()},
        {'name': '王芳', 'department': '市場部', 'position': '市場經理', 'salary': 22000.00, 'hire_date': datetime(2019, 8, 10).date()},
        {'name': '劉洋', 'department': '市場部', 'position': '市場專員', 'salary': 12000.00, 'hire_date': datetime(2022, 1, 5).date()},
        {'name': '陳明', 'department': '財務部', 'position': '財務主管', 'salary': 20000.00, 'hire_date': datetime(2018, 11, 20).date()},
        {'name': '趙麗', 'department': '財務部', 'position': '會計', 'salary': 15000.00, 'hire_date': datetime(2021, 4, 15).date()},
        {'name': '孫強', 'department': '人事部', 'position': '人事經理', 'salary': 18000.00, 'hire_date': datetime(2020, 7, 1).date()},
        {'name': '周傑', 'department': '技術部', 'position': '技術總監', 'salary': 35000.00, 'hire_date': datetime(2017, 2, 28).date()},
    ]
    
    with engine.begin() as conn:
        conn.execute(sales_table.insert(), sales_data)
        conn.execute(employees_table.insert(), employees_data)
        
    print(f"Sample database initialized with {len(sales_data)} sales records and {len(employees_data)} employees.")

def get_database_schema() -> dict:
    """获取数据库结构信息"""
    db = get_sql_database()
    tables = db.get_usable_table_names()
    
    schema = {
        "dialect": db.dialect,
        "tables": []
    }
    
    engine = get_engine()
    inspector = inspect(engine)
    
    for table in tables:
        if table.startswith("chat_"):
            continue
            
        columns = inspector.get_columns(table)
        
        with engine.connect() as conn:
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            
        table_info = {
            "name": table,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col.get("primary_key", 0) > 0
                }
                for col in columns
            ],
            "row_count": row_count
        }
        schema["tables"].append(table_info)
    
    return schema
