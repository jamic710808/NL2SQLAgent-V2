import sqlite3
import os

# 精確映射字典
MAPPING = {
    # 區域
    "华东": "華東",
    "华北": "華北",
    "华南": "華南",
    "华西": "華西",
    "华中": "華中",
    
    # 類別
    "电子产品": "電子產品",
    "家具": "家具",
    "办公用品": "辦公用品",
    
    # 產品名稱
    "笔记本电脑": "筆記型電腦",
    "无线鼠标": "無線滑鼠",
    "机械键盘": "機械鍵盤",
    "显示器": "顯示器",
    "办公椅": "辦公椅",
    "办公桌": "辦公桌",
    "打印纸": "列印紙",
    "签字笔": "原子筆",
    "文件夹": "資料夾",
    "台灯": "檯燈",
    "平板电脑": "平板電腦",
    "耳机": "耳機",
    "投影仪": "投影機",
    "书架": "書架",
    "白板": "白板",
    
    # 部門
    "技术部": "技術部",
    "市场部": "市場部",
    "财务部": "財務部",
    "人事部": "人事部",
    
    # 職位
    "高级工程师": "高級工程師",
    "工程师": "工程師",
    "市场经理": "市場經理",
    "市场专员": "市場專員",
    "财务主管": "財務主管",
    "会计": "會計",
    "人事经理": "人事經理",
    "技术总监": "技術總監",
    
    # 姓名
    "张伟": "張偉",
    "李娜": "李娜",
    "王芳": "王芳",
    "刘洋": "劉洋",
    "陈明": "陳明",
    "赵丽": "趙麗",
    "孙强": "孫強",
    "周杰": "周傑"
}

# 簡單的字符替換（針對對話內容）
COMMON_VARS = {
    "总": "總",
    "样": "樣",
    "务": "務",
    "据": "據",
    "项": "項",
    "应": "應",
    "个": "個",
    "关": "關",
    "开": "開",
    "发": "發",
    "经": "經",
    "济": "濟",
    "会": "會",
    "论": "論",
    "计": "計",
    "单": "單",
    "位": "位",
    "级": "級",
    "员": "員",
    "师": "師",
    "理": "理",
    "专": "專",
    "管": "管",
    "财": "財",
    "库": "庫",
    "表": "表",
    "里": "裡",
    "么": "麼",
    "什么": "什麼",
    "话": "話",
    "测": "測",
    "试": "試",
    "数据库": "資料庫",
    "资料": "資料",
    "显示": "顯示",
    "查询": "查詢",
    "销售": "銷售",
    "金额": "金額",
    "最高": "最高",
    "最低": "最低",
    "平均": "平均",
    "类别": "類別",
    "哪些": "哪些"
}

def multi_replace(text, dictionary):
    if not text:
        return text
    new_text = text
    for k, v in dictionary.items():
        new_text = new_text.replace(k, v)
    return new_text

def convert_db(db_path):
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Converting sales table...")
    cursor.execute("SELECT id, product_name, category, region FROM sales")
    for row in cursor.fetchall():
        new_prod = multi_replace(row[1], MAPPING)
        new_cat = multi_replace(row[2], MAPPING)
        new_reg = multi_replace(row[3], MAPPING)
        cursor.execute("UPDATE sales SET product_name=?, category=?, region=? WHERE id=?", (new_prod, new_cat, new_reg, row[0]))
        
    print("Converting employees table...")
    cursor.execute("SELECT id, name, department, position FROM employees")
    for row in cursor.fetchall():
        new_name = multi_replace(row[1], MAPPING)
        new_dept = multi_replace(row[2], MAPPING)
        new_pos = multi_replace(row[3], MAPPING)
        cursor.execute("UPDATE employees SET name=?, department=?, position=? WHERE id=?", (new_name, new_dept, new_pos, row[0]))
        
    print("Converting chat_sessions table...")
    cursor.execute("SELECT id, title FROM chat_sessions")
    for row in cursor.fetchall():
        new_title = multi_replace(row[1], COMMON_VARS)
        cursor.execute("UPDATE chat_sessions SET title=? WHERE id=?", (new_title, row[0]))
        
    print("Converting chat_messages table...")
    cursor.execute("SELECT id, content FROM chat_messages")
    for row in cursor.fetchall():
        new_content = multi_replace(row[1], COMMON_VARS)
        # 也對內容進行 MAPPING 替換（處理數據庫中的術語）
        new_content = multi_replace(new_content, MAPPING)
        cursor.execute("UPDATE chat_messages SET content=? WHERE id=?", (new_content, row[0]))
        
    conn.commit()
    conn.close()
    print("Conversion completed successfully!")

if __name__ == "__main__":
    db_path = "c:/NL2SQLAgent-V2/backend/data/app.db"
    convert_db(db_path)
