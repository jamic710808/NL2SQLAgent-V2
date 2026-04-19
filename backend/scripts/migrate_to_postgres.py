"""
資料庫遷移腳本 (SQLite -> PostgreSQL)
"""
import os
import sys
from sqlalchemy import create_engine, MetaData
from dotenv import load_load

# 將上層目錄加入 sys.path 以匯入 app 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import (
    metadata, 
    sales_table, 
    employees_table, 
    chat_sessions_table, 
    chat_messages_table
)

def migrate_data(source_url: str, target_url: str):
    print(f"來源資料庫: {source_url}")
    print(f"目標資料庫: {target_url}\n")
    
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    print("1. 正在目標資料庫建立資料表結構...")
    metadata.create_all(target_engine)
    
    tables_to_migrate = [
        (sales_table, 'sales'),
        (employees_table, 'employees'),
        (chat_sessions_table, 'chat_sessions'),
        (chat_messages_table, 'chat_messages')
    ]
    
    with source_engine.connect() as src_conn, target_engine.begin() as tgt_conn:
        for table_obj, table_name in tables_to_migrate:
            print(f"2. 正在遷移 [{table_name}] 數據...")
            
            # 從來源讀取所有資料
            rows = src_conn.execute(table_obj.select()).fetchall()
            
            if not rows:
                print(f"   - {table_name} 為空，跳過。")
                continue
                
            # 將 rows 轉為字典列表
            data = [dict(row._mapping) for row in rows]
            
            # 刪除目標庫舊有資料 (可選，避免重複)
            tgt_conn.execute(table_obj.delete())
            
            # 寫入目標資料庫
            tgt_conn.execute(table_obj.insert(), data)
            print(f"   - 成功遷移 {len(data)} 筆紀錄至 {table_name}。")
            
    print("\n遷移完成！")

if __name__ == "__main__":
    # 預設來源為本地 SQLite
    source_db = "sqlite:///../data/app.db"
    
    print("=== SQLite 至 PostgreSQL 遷移工具 ===")
    target_db = input("請輸入您的 PostgreSQL 連線字串 (例如 postgresql://user:pass@host/dbname): ").strip()
    
    if not target_db:
        print("錯誤: 必須提供目標資料庫連線字串。")
        sys.exit(1)
        
    migrate_data(source_db, target_db)
