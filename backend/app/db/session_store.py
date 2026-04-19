"""
會話持久化存儲模組
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import text

from app.db.connection import get_raw_connection, get_engine, metadata, chat_sessions_table, chat_messages_table


class SessionStore:
    """會話存儲管理器"""
    
    def __init__(self):
        engine = get_engine()
        # 確保 Table 已被創建
        metadata.create_all(engine)
    
    def create_session(self, title: Optional[str] = None) -> dict:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        if not title:
            title = f"新對話 {now.strftime('%m-%d %H:%M')}"
        
        with get_raw_connection() as conn:
            conn.execute(
                chat_sessions_table.insert().values(
                    id=session_id,
                    title=title,
                    created_at=now,
                    updated_at=now
                )
            )
            conn.commit()
            
        return {
            "id": session_id,
            "title": title,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "message_count": 0
        }
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话信息"""
        query = text("""
            SELECT s.*, COUNT(m.id) as message_count
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.id = m.session_id
            WHERE s.id = :session_id
            GROUP BY s.id, s.title, s.created_at, s.updated_at
        """)
        with get_raw_connection() as conn:
            row = conn.execute(query, {"session_id": session_id}).fetchone()
            
            if row:
                return dict(row._mapping)
        return None
    
    def list_sessions(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """获取会话列表"""
        query = text("""
            SELECT s.*, COUNT(m.id) as message_count
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.id = m.session_id
            GROUP BY s.id, s.title, s.created_at, s.updated_at
            ORDER BY s.updated_at DESC
            LIMIT :limit OFFSET :offset
        """)
        with get_raw_connection() as conn:
            rows = conn.execute(query, {"limit": limit, "offset": offset}).fetchall()
            return [dict(row._mapping) for row in rows]
    
    def update_session(self, session_id: str, title: str) -> bool:
        """更新会话标题"""
        with get_raw_connection() as conn:
            result = conn.execute(
                chat_sessions_table.update()
                .where(chat_sessions_table.c.id == session_id)
                .values(title=title, updated_at=datetime.now())
            )
            conn.commit()
            return result.rowcount > 0
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话及其所有消息"""
        with get_raw_connection() as conn:
            # 由於 ForeignKey cascade, 刪除 session 即可，或者我們都顯式刪除
            conn.execute(chat_messages_table.delete().where(chat_messages_table.c.session_id == session_id))
            result = conn.execute(chat_sessions_table.delete().where(chat_sessions_table.c.id == session_id))
            conn.commit()
            return result.rowcount > 0
    
    def touch_session(self, session_id: str):
        """更新会话的最后更新时间"""
        with get_raw_connection() as conn:
            conn.execute(
                chat_sessions_table.update()
                .where(chat_sessions_table.c.id == session_id)
                .values(updated_at=datetime.now())
            )
            conn.commit()
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sql_query: Optional[str] = None
    ) -> dict:
        """添加消息"""
        now = datetime.now()
        
        with get_raw_connection() as conn:
            result = conn.execute(
                chat_messages_table.insert().values(
                    session_id=session_id,
                    role=role,
                    content=content,
                    sql_query=sql_query,
                    created_at=now
                )
            )
            
            message_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
            
            # 更新会话时间
            conn.execute(
                chat_sessions_table.update()
                .where(chat_sessions_table.c.id == session_id)
                .values(updated_at=now)
            )
            
            conn.commit()
            
        return {
            "id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "sql_query": sql_query,
            "created_at": now.isoformat()
        }
    
    def get_messages(self, session_id: str, limit: int = 100) -> list[dict]:
        """获取会话消息"""
        query = chat_messages_table.select().where(chat_messages_table.c.session_id == session_id).order_by(chat_messages_table.c.created_at.asc()).limit(limit)
        with get_raw_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(row._mapping) for row in rows]
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> list[dict]:
        """获取最近的消息"""
        # 注意：子查询在多种数据库中支持，但 SQLAlchemy Core 更简单可以倒序查出再转正序
        query = chat_messages_table.select().where(chat_messages_table.c.session_id == session_id).order_by(chat_messages_table.c.created_at.desc()).limit(limit)
        with get_raw_connection() as conn:
            rows = conn.execute(query).fetchall()
            
            # 倒序回來
            results = [dict(row._mapping) for row in reversed(rows)]
            return results

# 全局会话存储实例
session_store = SessionStore()
