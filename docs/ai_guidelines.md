# AI 使用準則（Group 18）

本文件根據 Week 12 Lab 的審查證據，修訂 Week 3 的準則。每條新規則都能從一個 PR 檢查出來。

## 規則 1：每個 PR 都要說明 AI 做了什麼

- **舊規則（Week 3, Section 2）：** 程式碼生成 -> prompt log：模型、prompt、保留的地方。
- **新規則：** 每個 PR 都要填 `.github/PULL_REQUEST_TEMPLATE.md` 的「AI assistance」：
  - 使用的工具與模型（沒用就寫 none）
  - AI 生成了哪些檔案或函式
  - 給 AI 的一行指令
  - 作者之後改了什麼

  這一欄空白或只留 template 註解的 PR，reviewer 不會 approve。
- **為什麼改：** 審查（B2）看不出 walking skeleton 裡 AI 做了什麼。舊規則沒規定 prompt log 放在哪裡，所以實際上從來沒有產生。

## 規則 2：作者先自審，並寫出驗證方式

- **舊規則（Week 3, Section 1）：** 程式碼生成使用 GitHub Copilot（不包含直接整合進程式碼）。
- **新規則：** 送 review 前，作者要：
  - 勾選 "I read every line of this change myself and can explain it without the AI"。
  - 在 "How I checked it" 寫出實際執行的指令與結果（例如 `pytest` → 1 passed），或附 Discord 操作截圖。
  - 一個 PR 只處理一個 issue，並在 "What and why" 連結該 issue。
- **為什麼改：** 「不包含直接整合進程式碼」無法從 PR 檢查。審查的 Finding 2（匿名表態者身份被顯示）和 Finding 3（只照 README 無法把 bot 跑起來），實際跑過一次就會發現；要求寫出驗證方式就能提早抓到。

## 規則 3：AI 產出的爭議要寫進 DECISIONS.md

- **舊規則（Week 3, Section 3）：** 等於 50% 不同意：辯論後 steward 有最終決定權；超過 50% 不同意：直接否決；少於 50% 不同意：開放不同意的人提出意見，最終以多數人為主。
- **新規則：** AI 產出品質的分歧，仍照上述比例規則投票。投票後 24 小時內，由提出疑慮的人在 `DECISIONS.md` 新增一筆紀錄：
  - 日期
  - 有爭議的 AI 產出（PR 或檔案）
  - 投票結果
  - 最後決定與理由

  相關 PR 的 "What and why" 要連結這筆紀錄；沒有連結，steward 不 merge。
- **為什麼改：** 舊規則只說怎麼投票，沒說結果記在哪裡，理由只留在 Discord 和個人記憶裡。審查（B3）也發現分工與時程沒寫進 `DECISIONS.md`，讀 repo 的人看不出誰負責、何時完成。
