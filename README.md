# TeamSync

讓團隊在 Discord 做決定前，每個人先私下表態（支持／有保留／反對），再同時揭曉。

## 目前狀態

Discord 流程目前仍是 walking skeleton：`/decide` 發起決定、按「表態」會固定記錄為支持選項 A、`/reveal` 印出原始資料。
AI 摘要函式與資料庫儲存已完成，但尚未接入 `/reveal` 的提議者確認／發布流程；立場選單、正式揭曉排版及 `/conclude` 也尚未完成。

## 事前準備：建立 Discord bot

1. 在 Discord Developer Portal 建立 application，到 Bot 頁取得 token
2. OAuth2 → URL Generator 勾選 `bot` 與 `applications.commands`，用產生的網址把 bot 加入伺服器
3. 開啟 Discord 開發者模式，右鍵伺服器複製伺服器 ID

## Setup

1. 需要 Python 3.11 以上：clone 此 repo 並進入資料夾
2. 建立虛擬環境並安裝套件：`python -m venv .venv`，啟用後 `pip install -r requirements.txt`
3. 在 `.env` 填入 `DISCORD_TOKEN` 與 `GUILD_ID`。若要執行 AI prompt suite，另填 `ANTHROPIC_API_KEY` 與 `ANTHROPIC_MODEL`
4. 啟動：`python -m teamsync.bot`，看到「已登入」即成功
5. 在 Discord 試 `/ping`、`/decide 問題 | 選項A | 選項B`、按「表態」、`/reveal 編號`

## 測試

`pytest`

執行 10 個 AI prompt 案例（會呼叫設定的 Anthropic 模型並產生 API 費用）：

`python tests/prompt_suite/run_suite.py`

結果預設寫入 `tests/prompt_suite/results/latest.json`。程式會檢查輸出數量和禁止詞；摘要是否涵蓋每個案例的預期重點仍需人工核對。

## 專案結構

`teamsync/` 內分為 `db/`（資料存取）、`cogs/`（slash command）、`ui/`（按鈕與顯示）、`ai/`（AI 整理）、`records/`（決策紀錄）。
