# TeamSync

讓團隊在 Discord 做決定前，每個人先私下表態（支持／有保留／反對），再同時揭曉。

## 目前狀態

只完成 walking skeleton：`/decide` 發起決定、按「表態」會固定記錄為支持選項 A、`/reveal` 印出原始資料。
立場選單、揭曉排版、AI 整理、`/conclude` 尚未完成。

## 事前準備：建立 Discord bot

1. 在 Discord Developer Portal 建立 application，到 Bot 頁取得 token
2. OAuth2 → URL Generator 勾選 `bot` 與 `applications.commands`，用產生的網址把 bot 加入伺服器
3. 開啟 Discord 開發者模式，右鍵伺服器複製伺服器 ID

## Setup

1. 需要 Python 3.11 以上：clone 此 repo 並進入資料夾
2. 建立虛擬環境並安裝套件：`python -m venv .venv`，啟用後 `pip install -r requirements.txt`
3. 建立 `.env`：在專案根目錄複製範例檔，再填入設定（見下方「環境變數」）
   - macOS / Linux：`cp .env.example .env`
   - Windows（PowerShell）：`Copy-Item .env.example .env`
4. 啟動：`python -m teamsync.bot`，看到「已登入」即成功
5. 在 Discord 試 `/ping`、`/decide 問題 | 選項A | 選項B`、按「表態」、`/reveal 編號`

## 環境變數

bot 啟動時會從專案根目錄的 `.env` 讀取設定（`teamsync/config.py`）。

| 變數 | 必填 | 說明 |
| --- | --- | --- |
| `DISCORD_TOKEN` | 是 | Discord Developer Portal → Bot 頁取得的 bot token |
| `GUILD_ID` | 是 | 要註冊 slash command 的伺服器 ID（純數字，見「事前準備」第 3 步） |
| `DB_PATH` | 否 | SQLite 資料庫檔案路徑，預設 `teamsync.db`；檔案不存在會自動建立 |
| `ANTHROPIC_API_KEY` | 使用 AI 整理時必填 | Anthropic API key，到 Anthropic Console 建立 |
| `ANTHROPIC_MODEL` | 使用 AI 整理時必填 | AI 整理使用的 Claude 模型 ID，例如 `claude-sonnet-5-5` |

- 缺少 `DISCORD_TOKEN` 或 `GUILD_ID` 時 bot 會直接啟動失敗（`KeyError`）；`GUILD_ID` 不是數字會出現 `ValueError`。
- `ANTHROPIC_API_KEY` 與 `ANTHROPIC_MODEL` 留空時 bot 仍可啟動，表態與揭曉照常運作，但 AI 整理會無法使用。要用 AI 整理就兩個都要填。

> ⚠️ **不要 commit `.env`**：裡面有 bot token 與 API key 等機密。`.env` 已列在 `.gitignore`，請只修改 `.env.example` 來新增或說明變數（不要填入真實值）。若不小心把 token 推上 GitHub，請立刻到 Developer Portal 重設 token。

## 測試

`pytest`

## 專案結構

`teamsync/` 內分為 `db/`（資料存取）、`cogs/`（slash command）、`ui/`（按鈕與顯示）、`ai/`（AI 整理）、`records/`（決策紀錄）。
