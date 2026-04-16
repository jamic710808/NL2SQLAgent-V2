"""
LLM 接入模块 - 統一使用 OpenAI 格式
"""
import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from app.models.settings import get_llm_settings

def get_llm(
    model: Optional[str] = None,
    streaming: bool = True,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    获取 LLM 实例
    
    Args:
        model: 模型名称，默认使用配置中的模型
        streaming: 是否启用流式输出
        temperature: 温度参数
    
    Returns:
        ChatOpenAI 实例
    """
    settings = get_llm_settings()
    
    # 确保 API Key 已设置
    api_key = settings.api_key
    if not api_key:
        raise ValueError("API Key not configured. Please set it in settings.")
    
    return ChatOpenAI(
        model=model or settings.model_name,
        api_key=api_key,
        base_url=settings.base_url,
        streaming=streaming,
        temperature=temperature,
    )

def get_llm_with_tools(tools: list, model: Optional[str] = None) -> BaseChatModel:
    """
    获取绑定工具的 LLM 实例
    
    Args:
        tools: 工具列表
        model: 模型名称
    
    Returns:
        绑定工具后的 LLM 实例
    """
    llm = get_llm(model=model, streaming=True)
    return llm.bind_tools(tools)

# 預定義的系統提示模板
SQL_AGENT_SYSTEM_PROMPT = """你是一個專業的 SQL 資料庫分析助手。

你的任務是幫助使用者透過自然語言查詢資料庫。請按以下步驟操作：

1. **理解問題**：仔細分析使用者的查詢意圖
2. **查看表結構**：使用 sql_db_list_tables 和 sql_db_schema 了解資料庫結構
3. **編寫 SQL**：根據表結構編寫正確的 SQL 查詢
4. **驗證 SQL**：使用 sql_db_query_checker 檢查 SQL 語法
5. **執行查詢**：使用 sql_db_query 執行查詢
6. **分析結果**：解讀查詢結果並給出清晰的回答

資料庫方言: {dialect}

**注意事項：**
- 只能執行 SELECT 查詢，禁止 INSERT/UPDATE/DELETE/DROP 等操作
- 查詢結果限制在 {top_k} 條以內，除非使用者明確要求更多
- 優先選擇相關列，避免 SELECT *
- 如果查詢出錯，分析錯誤原因並重新編寫 SQL
- **語言規範**：你必須始終使用「繁體中文（zh-TW）」與使用者對話及解釋分析結果。

請用繁體中文回答使用者問題，並在回答中說明你的分析思路。
"""
