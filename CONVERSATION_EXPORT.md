# NL2SQL Agent 開發對話完整匯出紀錄 (V1)

這份文件紀錄了本次對話中針對 **NL2SQL Agent** 專案所進行的所有重大優化、功能開發與 Bug 修復。

---

## 1. 專案核心變更摘要

### 多模型供應商支援 (Multi-LLM Support)
- **統一介面**：將原有的 `dashscope` 專有格式重構為通用的 `langchain-openai` 格式。
- **動態管理**：實作了 `/api/settings/llm` API，支援透過 `data/llm_settings.json` 動態配置 8 大模型供應商（OpenAI, DeepSeek, Google, SiliconFlow 等）。
- **前端整合**：新增 `SettingsModal.tsx`，允許使用者即時切換模型與金鑰。

### 繁體中文化 (Traditional Chinese Localization)
- **前端介面**：將 Sidebar、ChatArea、ChartPanel、SettingsModal 等所有組件的簡體中文靜態字串全數轉為繁體中文。
- **AI 邏輯**：更新 `SQL_AGENT_SYSTEM_PROMPT`，強制 AI 必須始終以「繁體中文（zh-TW）」進行回答。
- **預設數據**：轉換了資料庫初始化時的範例數據標籤與預設對話名稱（「新對話」）。

### 佈局與捲軸修復 (Scroll & Layout Fixes)
- **捲軸問題**：解決了長對話時訊息列表無法垂直捲動的問題。透過正確配置 Flex 容器的 `min-h-0` 與 `overflow-hidden` 屬性，確保聊天區塊在內部產生捲軸。
- **可調整面板**：右側數據視覺化面板現在支援滑鼠拖曳縮放（面板寬度自訂）。

### 圖表渲染修復 (Chart Rendering)
- **穩定性**：重構 `Chart.tsx`，加入 `parseValue` 函式處理千分位逗號字串，避免圖表數據產生 `NaN`。
- **動態更新**：使用 React `key` 機制確保切換圖表類型時完全重新掛載畫布，解決 ECharts 殘留舊實例的問題。

---

## 2. 解決的關鍵 Bug

1. **Delete Session Crash**：修正了刪除對話時後端回傳 204 No Content 導致前端 `response.json()` 解析失敗的錯誤。
2. **Chart Blank Issue**：修復了柱狀圖與折線圖在某些數據格式下無法載入的問題。
3. **Scroll Truncation**：解決了對話內容過長時頁面被撐開且無法滑動回到上方的問題。

---

## 3. 系統目前的架構架構
- **前端**：React + TypeScript + Tailwind CSS + ECharts
- **後端**：FastAPI + SQLite + LangChain
- **數據存儲**：`backend/data/app.db` (SQLite)
- **配置存儲**：`backend/data/llm_settings.json`

---

## 4. 未來建議與擴充方向 (Next Steps)
- **數據寫入權限**：目前 AI 僅能讀取數據，可視需求開發 `INSERT` 功能。
- **對話刪除確認**：為刪除對話按鈕增加二次確認視窗，避免誤刪。
- **模型回應優化**：針對特定業務場景進一步微調 System Prompt。

---

> [!NOTE]
> 本次對話結束時，系統已達到 V1 版穩定狀態，並已準備好同步至 GitHub。


1. 資料存放在哪裡？
資料是存放在 「後端（Backend）」。

具體的存放路徑位在： c:\NL2SQLAgent\backend\data\app.db

資料格式：這是一個 SQLite 資料庫檔案（.db）。
存放內容：
分析數據：包含 sales（銷售數據）和 employees（員工數據）等業務表格。
對話紀錄：包含 chat_sessions（對話會話）和 chat_messages（對話訊息內容）。
優點：SQL Agent 會讀取這個資料庫的結構，並根據您的問題生成 SQL 語言來查詢這些資料。
2. 如何擴充或更新資料？
如果您想要增加數據量或更新現有的內容，您可以透過以下幾種方式：

方法 A：修改初始化程式碼（推薦用於開發環境）
如果您希望在每次重設系統時都有這些新資料，可以修改後端的初始化腳本：

開啟檔案：

…\backend\app\db\connection.py
找到 

init_sample_database
 函式。
在 sales_data 或 employees_data 的清單中加入您的新數據。
生效方式：刪除 

backend/data/app.db
 檔案，然後重啟後端服務。系統會自動偵測檔案不存在並根據新程式碼重新建立資料庫。
方法 B：使用外部資料庫工具（推薦用於手動管理）
您可以像使用 Excel 一樣管理資料庫：

下載並安裝 「DB Browser for SQLite」（免費工具）。
使用該工具開啟 c:\NL2SQLAgent\backend\data\app.db。
您可以像編輯表格一樣直接新增、刪除或修改資料列。
修改完成後點擊「Write Changes」，網頁前端就會立即查詢到更新後的結果。
方法 C：透過 AI 擴充（進階功能）
目前的 Agent 被設定為「唯讀」以保護安全。如果您未來需要透過對話來「新增」數據，我們可以修改後端的 System Prompt，賦予 AI 執行 INSERT 或 UPDATE 指令的權限。

接下來，我將繼續幫您執行「同步到 GitHub」的任務。 您是否希望將 

backend/data/app.db
 這個資料庫檔案也一併上傳到 GitHub，還是只上傳程式碼？（通常建議不安裝資料庫檔案，讓每個人在本地端自動生成）。
