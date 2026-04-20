"""
LLM 設定管理 - 使用資料庫儲存（相容 Vercel 唯讀檔案系統）
"""
import json
import os
from pydantic import BaseModel

from app.db.connection import get_engine, app_settings_table, metadata
from sqlalchemy import select, inspect


class LLMSettings(BaseModel):
    provider: str
    base_url: str
    api_key: str
    model_name: str


def _ensure_settings_table():
    """確保 app_settings 表存在"""
    engine = get_engine()
    insp = inspect(engine)
    if "app_settings" not in insp.get_table_names():
        app_settings_table.create(engine, checkfirst=True)


def get_llm_settings() -> LLMSettings:
    """從資料庫讀取 LLM 設定，若不存在則回傳預設值"""
    default_settings = LLMSettings(
        provider="OpenAI",
        base_url="https://api.openai.com/v1",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name="gpt-4o-mini"
    )

    try:
        _ensure_settings_table()
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                select(app_settings_table.c.value).where(
                    app_settings_table.c.key == "llm_settings"
                )
            ).fetchone()

            if result:
                data = json.loads(result[0])
                return LLMSettings(**data)
    except Exception as e:
        print(f"Warning: Could not read LLM settings from database: {e}")

    return default_settings


def save_llm_settings(settings: LLMSettings) -> bool:
    """將 LLM 設定儲存到資料庫"""
    try:
        _ensure_settings_table()
        engine = get_engine()
        settings_json = json.dumps(settings.model_dump(), ensure_ascii=False)

        with engine.begin() as conn:
            # 嘗試更新，如果不存在則插入（upsert）
            existing = conn.execute(
                select(app_settings_table.c.key).where(
                    app_settings_table.c.key == "llm_settings"
                )
            ).fetchone()

            if existing:
                conn.execute(
                    app_settings_table.update()
                    .where(app_settings_table.c.key == "llm_settings")
                    .values(value=settings_json)
                )
            else:
                conn.execute(
                    app_settings_table.insert()
                    .values(key="llm_settings", value=settings_json)
                )

        return True
    except Exception as e:
        print(f"Error saving LLM settings: {e}")
        raise
