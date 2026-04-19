import sqlite3
import json
import os

def inspect_db(db_path):
    if not os.path.exists(db_path):
        return {"error": f"File not found: {db_path}"}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 獲取所有資料表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    results = {}
    for table in tables:
        # 獲取 Schema
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 獲取前 5 筆資料進行抽樣
        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
        data = cursor.fetchall()
        
        results[table] = {
            "columns": columns,
            "sample_data": data
        }
    
    conn.close()
    return results

if __name__ == "__main__":
    db_info = inspect_db("c:/NL2SQLAgent-V2/backend/data/app.db")
    print(json.dumps(db_info, indent=2, ensure_ascii=False))
