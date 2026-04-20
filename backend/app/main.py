"""
FastAPI 應用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import chat, session, database, settings as api_settings
from app.db.connection import get_sql_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時：初始化資料庫
    get_sql_database()
    print("Application started, database initialized.")
    
    yield
    
    # 關閉時：清理資源
    print("Application shutting down.")


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.app_name,
    description="智能數據分析助理 - 基於 LangChain + Qwen3 的自然語言資料庫查詢系統",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 API 路由
app.include_router(session.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(database.router, prefix="/api")
app.include_router(api_settings.router, prefix="/api")


@app.get("/health")
async def health_check():
    """健康檢查介面"""
    return {"status": "ok", "message": "Service is running"}


@app.get("/")
async def root():
    """根路徑 - API 資訊"""
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "api_endpoints": {
            "sessions": "/api/sessions",
            "chat": "/api/chat",
            "database": "/api/database/schema",
            "settings": "/api/settings/llm",
        }
    }
