# Decisions Log

## 2026-09-21 — Initial code steward
**What:** [mengzeleecs15] is the initial code steward for the team.

**Why:** [assigned by team agreement]

## 2026-10-23 — Code steward changed
**What:** [stue1202] is the code steward for the team from 2026-10-23 to 2026-11-06.

**Why:** [每兩週換一個 Code steward，有人提名並有多數人同意決定]

## 2026-10-23 — 專案方向微調與收束
**What:** 把專案方向從籠統的「意見不合」收斂成一個完整、具體的問題與設計（詳見Group18_CP1.md）

**Why:** 原本問題過於籠統，並難以產出具體設計與衡量計劃。

## 2026-11-23 技術選型：Python + discord.py + SQLite
**What:** 選擇：Python 3.11、discord.py 2.4、SQLite（aiosqlite）
**Why:** 相較 Node.js + discord.js 等其他工具，組員們更加熟悉

## 2026-11-23 資料格式定案（walking skeleton）
**What:** 5 張資料表（decisions、options、stances、ai_summaries、conclusions）與 models.py；立場分 support／reserved／oppose 三種
**Why:** 必要的文件

## 2026-11-23 保留意見預設匿名
**What:** 表態預設匿名，表態時可改為具名
**Why:** P2 訪談顯示有社交壓力時不敢說
## 2026-11-23 送給 AI 的資料不含使用者資訊
**What:** 呼叫 AI 時，只傳送 Concern 的選項代號、立場、理由，不再帶入使用者 ID 或名稱。
**Why:** 系統採匿名設計，若把整筆表態直接送給 AI，可能洩漏誰說了什麼。這樣切分也符合 CP1 4.5 Human-AI Boundary，讓 AI 只拿到完成任務所需的最少資料。

## 2026-11-23 重新表態直接覆蓋舊紀錄
**What:** save_stances 先刪除此人在該決定的舊表態，再寫入新的，只保留最後一次。
**Why:** 淘汰：保留每次修改的歷史（較複雜，揭曉只需要最終立場）。影響：評估時看不到「改過幾次立場」，需要時再加。

## 2026-11-23 按鈕處理方式
**What:** 按鈕 custom_id 寫成 stance:<編號>，由 cog 監聽所有按鈕事件；之後每種按鈕都用自己的前綴
**Why:** 用 View 物件 callback 的按鈕在 bot 重啟後就失效，而決定可能開好幾天；把決定編號寫進 custom_id、由 cog 統一處理，重啟後舊按鈕仍可用，也不用替每個決定各註冊一個 View。
