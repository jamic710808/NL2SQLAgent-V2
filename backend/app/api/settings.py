from fastapi import APIRouter, HTTPException
from app.models.settings import LLMSettings, get_llm_settings, save_llm_settings

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)

@router.get("/llm", response_model=LLMSettings)
async def get_settings():
    """獲取目前的 LLM 設定"""
    try:
        settings = get_llm_settings()
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm", response_model=LLMSettings)
async def update_settings(settings: LLMSettings):
    """更新 LLM 設定"""
    try:
        save_llm_settings(settings)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
