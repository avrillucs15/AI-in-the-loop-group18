## Part 2 — Draft AI Usage Guidelines
---

### Section 1 — What AI tools we plan to use, and what we will use each for
(specific task: specific tool (not for))
- 點子發想: Claude, Gemini, ChatGPT (不包含做為正式決定)
- 整理會議記錄、文獻參考: Gemini Notebook (不包含做為正式紀錄)
- 程式碼生成: Github Copilot (不包含直接整合進程式碼)

---

### Section 2 — How we will document AI interactions
(trigger -> place: what to record)
- 程式碼生成 -> prompt log: 模型、prompt、保留的地方
- debug -> PR description: 什麼 bug
- 點子發想 -> `DECISIONS.md`: 最終決策

---

Section 3 — How we will handle disagreements about AI output quality

- = 50% 不同意: 辯論後 steward 有最終決定權
- > 50% 不同意: 直接否決
- < 50% 不同意: 開放不同意的人提出意見，最終以多數人為主

---

## Part 3 — Draft Evaluation Plan
---
### Problem Grounding
Q: Who specifically has the collaboration problem you are addressing?
A: 有團體討論意見不合的學生

Q: What do they currently do instead of your tool?
A: 吵架

Q: What would be observably different about their collaboration if your tool worked?
A: 具有更多的證據去支持最終的結論，具有更高的說服力

---

### Evaluation Plan Draft

- Success definition: 團體中持反對意見的學生對最後的決策平均滿意度達60%
- Target users: 與決策持相反意見的團體學生
- Method: 做問卷，收集使用者認為使用工具後對決策與證據的滿意度
- Minimum evidence threshold: 5個團體
