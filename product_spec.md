# AI Flight Guardian (飛機票守護者) - 產品規格書

## 1. 產品概述 (Product Overview)
AI Flight Guardian 是一個為價格敏感且重視效率的旅客量身打造的自動化航班監控與分析系統。本系統採用 GitHub 架構與 AI Agent (Gemini Pro/Claude Pro) 協同運作，旨在達成低成本甚至是零成本的運營與高效的資訊更新。

## 2. 目標用戶 (User Persona)
### The Tech-Savvy Value Hunter (科技型價值尋找者)
- **行為特徵**：重視自動化與數據透明度。對價格敏感，但不願犧牲過多時間成本在極端的轉機路徑上。
- **痛點**：不希望被瑣碎訊息干擾，僅在「有價值」的變動發生時才接收即時通知。
- **需求**：需要一個簡單的 UI 來同時管理多個跨年度、跨國家的旅遊查詢任務。

## 3. 技術棧與模型策略 (Tech Stack & Model Strategy)
- **開發環境**: Antigravity (Workflow Orchestration)
- **Gemini Pro (Strategic Planner & Data Analyst)**:
  - 負責 Phase 0 規劃與 Phase 1 架構設計。
  - 設計跨國航線（含歐美長程）的「智慧轉機路徑演算法」。
  - 負責設計分析歷史數據、產出每日 Summary 的 Prompt 邏輯。
- **Claude Pro (Architecture & Code Specialist)**:
  - 負責 Phase 1 基礎設施實作（GitHub Actions, Repo Schema）。
  - 負責 Phase 2 & 3 的核心代碼撰寫、Telegram Bot 整合與 React/GitHub Pages 前端開發。
- **Infrastructure**: GitHub Actions (Compute), GitHub Repo (Storage - JSON/CSV)
- **Frontend**: React (hosted on GitHub Pages)
- **Backend/Scripts**: Python
- **Notification**: Telegram API

## 4. 階段性開發藍圖 (Phased Roadmap)

### Phase 0: Clarification & Strategic Planning (Gemini Leading)
- **目標 (Target)**: 明確產品核心業務邏輯與技術可行性，完成專案宏觀架構設計。
- **產出物 (Deliverables)**:
  - 歷史低價與轉機價值之演算法公式文件。
  - 工具鏈與技術棧確認報告。
- **驗收 Check List (Acceptance Checklist)**:
  - [ ] 確定機票數據來源 (API/爬蟲) 且成功取得測試資料。
  - [ ] 定義出能具體量化「好機票」的指標公式。
  - [ ] 確認 GitHub Actions Secrets 已設立且安全。
- **核心邏輯定義**：
  - 定義「歷史低價」判定指標 (例如：低於過去 30 天平均價格或特定閥值)。
  - 定義「轉機價值」運算公式 (評估轉機總次數、等待時間、總飛行時間，排除過於冗長的路徑)。
- **工具鏈確認**：
  - 確認 GitHub Actions 環境下 Secrets 管理（如 Telegram Token）。
  - 規劃 Python 爬蟲與 API 結合策略以確保能穩定獲取票價數據。

### Phase 1: Architecture & GitHub Infrastructure (Claude Leading)
- **目標 (Target)**: 建立穩固的底層基礎設施，確保資料能被正確儲存並能觸發自動化流程。
- **產出物 (Deliverables)**:
  - 具備完整 Schema 定義的 GitHub Repository 結構。
  - 可正常執行的 GitHub Actions Workflow 設定檔 (`.yml`)。
  - 可發送測試訊息的 Telegram Bot 模塊。
- **驗收 Check List (Acceptance Checklist)**:
  - [ ] 成功在 `.github/workflows` 中建立排程，且能按時觸發。
  - [ ] `tasks.json` 解析與讀取正常。
  - [ ] 成功推播測試用 Mock Message 至 Telegram 群組/使用者。
- **Data Layer**：
  - 建立 GitHub Repo 儲存任務設定 (`tasks.json`) 與價格紀錄 (`records/`)。
- **Compute Layer**：
  - 配置 GitHub Actions 排程工作 (`.github/workflows/scraper.yml`)。
  - 針對多個不同的航班追蹤任務實作平行 (Parallel) 處理邏輯，或串列 (Sequential) 處理以防止 API Rate Limit。
- **Communication**：
  - 建立 Telegram API 串接模組，確保訊息格式美觀且支援 Markdown。

### Phase 2: MVP Development (Core Monitoring)
- **目標 (Target)**: 完成機票價格監控核心邏輯，實現全自動化運作與智慧通知。
- **產出物 (Deliverables)**:
  - 自動機票查詢與解析腳本 (Python)。
  - 樞紐機場轉機自動比對模組。
  - 每日摘要與低價警報推播機制。
- **驗收 Check List (Acceptance Checklist)**:
  - [ ] 系統能成功獲取並解析真實機票數據，並將結果存入 CSV 中。
  - [ ] AI 能根據起訖點自動推薦至少 2 個合理樞紐機場進行延伸查詢。
  - [ ] 收到正確格式的 Telegram 每日摘要與具備 Actionable 按鈕/連結的低價警報。
- **AI Agent 邏輯**：
  - 實作「樞紐機場自動偵測」，針對起訖點長程航線（如：亞洲飛歐洲）由 AI 或演算法自動判定並加入合理轉機點（如：DXB, IST, BKK）以拓展更豐富的低價選擇。
- **通知系統**：
  - **每日摘要 (Daily Summary)**：匯總所有監控航線的趨勢、均價變化。
  - **低價緊急報警 (Price Drop Alert)**：當觸發「歷史低價」或具備極高「轉機價值」時，立即發送 Telegram 推播通知。

### Phase 3: Dashboard & Dynamic Task Management
- **目標 (Target)**: 提供易於操作的視覺化介面，讓非技術背景的使用者也能直覺地管理監控任務。
- **產出物 (Deliverables)**:
  - 部署於 GitHub Pages 的 React Web Application。
  - 視覺化價格趨勢圖表組件。
  - 任務設定檔 (CRUD) 編輯器。
- **驗收 Check List (Acceptance Checklist)**:
  - [ ] Dashboard 能正確讀取 `records` 內的 CSV 並渲染折線圖與散佈圖。
  - [ ] 使用者能透過網頁表單新增一筆新任務，並看見該任務成功以 Pull Request 或直接 Commit 的形式更新回 Git Repo。
  - [ ] 支援 RWD (Responsive Web Design)，確保在手機瀏覽趨勢圖表時排版正常不跑版。
- **GitHub Pages UI**：
  - 採用 React 開發輕量級 Dashboard，透過讀取 Repo 內的資料集實現視覺化的票價趨勢圖表。
- **Task CRUD (任務管理)**：
  - 提供簡易的網頁 UI，讓使用者能直接新增、修改或刪除旅遊任務（如：2026 美國行、2027 歐洲行）。
  - 使用者在 UI 的變更可透過 GitHub API 自動同步 Commit 回 Repository 內。

## 5. Style & Structure Requirements

### 5.1 用戶故事與驗收標準 (User Stories & AC)
- **Story 1**: 身為一名尋找便宜機票的旅客，我希望每天能在 Telegram 收到一次航班價格摘要，這讓我掌握趨勢卻不會被頻繁打擾。
  - **AC**: GitHub Action 每天定時執行一次。Telegram Bot 必須發送包含各路線最低價、均價與趨勢（漲/跌）的單一報表訊息。
- **Story 2**: 身為一名對價格敏感的旅客，我希望在出現異常低價且轉機合理的航班時，馬上收到通知，以便我立刻搶票。
  - **AC**: 當票價低於歷史低谷閥值，且轉機次數與總時長符合個人設定，系統必須透過 Telegram 即刻發出高優先級警告訊息。
- **Story 3**: 身為系統管理者，我需要一個 Dashboard 來輕鬆管理未來的多筆出遊計畫。
  - **AC**: Dashboard 能圖表化呈現趨勢，且包含表單供使用者修改任務，設定完成後能自動反映於後台 JSON 任務設定檔中。

### 5.2 模型分工表 (Model Task Allocation Table)
| 任務模組 | Gemini Pro 職責 (Strategic & Analytical) | Claude Pro 職責 (Execution & Architecture) |
| :--- | :--- | :--- |
| **P0: 策略規劃** | 定義低價與轉機價值公式、整體流程規劃 | 提供技術限制建議 (如 GitHub Actions 的特性) |
| **P1: 基礎架構** | 驗證 Repo 結構與資料儲存可讀性 | 撰寫 GitHub Actions YAML, 定義 Repo Schema |
| **P2: 核心監控** | 撰寫 Prompt 生成 Daily Summary、提供自動偵測樞紐演算法指導 | Python 腳本實作、Telegram Bot API 模組開發 |
| **P3: Dashboard**| 建議數據圖表呈現維度與 UX 流程 | React 前端開發、GitHub API 整合進 UI 儲存設定 |

### 5.3 資料結構定義 (Data Schema)
**Task Config (`tasks.json`)**
```json
{
  "tasks": [
    {
      "id": "eu-2027-summer",
      "name": "2027 歐洲行",
      "origin": ["TPE", "KIX"],
      "destination": ["CDG", "AMS"],
      "departure_date_range": ["2027-06-01", "2027-07-15"],
      "trip_duration_days": [14, 21],
      "max_stops": 2,
      "max_duration_hours": 24,
      "alert_threshold_price": 25000,
      "active": true
    }
  ]
}
```

**Flight Records (`records/eu-2027-summer.csv`)**
```csv
timestamp,airline,origin,destination,departure_date,return_date,stops,duration_outbound,duration_return,price,currency,is_lowest
2026-04-20T12:00:00Z,EK,TPE,CDG,2027-06-10,2027-06-25,1,18h30m,19h15m,26500,TWD,false
```

### 5.4 Antigravity 實作指南 (Antigravity Implementation Guide)
為了在 Antigravity 中最大化模型的協同效能，建議採用以下漸進式工作流：
1. **規劃與探索期**：將模型切換為 `Gemini Pro`，提供本產品規格書作為 Context，要求其進行高階設計、演算法推演，並完成專案 README 架構。
2. **底層架構實作**：將模型切換為 `Claude Pro`，基於 Gemini 的宏觀設計，專注於撰寫清晰的 Python 代碼、無錯誤的 GitHub Actions YAML 與 Telegram 串接邏輯。
3. **優化與驗證**：運用 Antigravity 的背景執行與除錯能力，測試爬蟲與通知機制；若需優化 Daily Summary 等 AI 解析功能，再交由 Gemini 調整 Prompt。
4. **介面開發**：以 Claude 為核心開發者，透過命令列建置 React 專案，結合快速迭代將前端視覺化與任務管理功能實作完成。

## 6. 限制與考量 (Constraints)
- **MVP 原則**：首重核心監控與最低運行成本。前端 Dashboard 在 Phase 3 前的過渡期內，使用者可直接以編輯 `tasks.json` 的方式管理任務。避免使用成本高昂的關聯式資料庫，全面依賴 GitHub Repository 作為靜態資料儲存點。
- **高擴展性**：代碼架構必須解耦。「資料獲取 (Scraper)」、「策略演算 (Analyzer)」與「訊息通知 (Notifier)」必須是彼此獨立的 Python 模組。這樣才能彈性應對未來從東亞短程擴展到歐美超級長程航線的不同複雜度需求。
