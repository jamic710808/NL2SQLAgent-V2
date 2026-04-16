import json
import os
from pydantic import BaseModel

# 儲存在根目錄下的 data 資料夾
SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "data", 
    "llm_settings.json"
)

class LLMSettings(BaseModel):
    provider: str
    base_url: str
    api_key: str
    model_name: str

def get_llm_settings() -> LLMSettings:
    # 預設使用 OpenAI，但若環境變數有值可以覆蓋
    default_settings = LLMSettings(
        provider="OpenAI",
        base_url="https://api.openai.com/v1",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name="gpt-4o-mini"
    )
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return LLMSettings(**data)
    except Exception:
        return default_settings

def save_llm_settings(settings: LLMSettings) -> bool:
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings.model_dump(), f, ensure_ascii=False, indent=2)
    return True
