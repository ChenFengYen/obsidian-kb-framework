@AGENTS.md

# Claude Code Adapter

`AGENTS.md` 是本 vault 的跨 Agent 核心規則。Claude Code 啟動時先載入該檔，再套用以下平台補充：

- 可用 skills 安裝於 `.claude/skills/`；執行時遵循各 `SKILL.md` 的核准與驗證步驟。
- Claude auto memory 只能保存個人偏好與工作經驗，不得成為 vault 知識或跨 Agent project state 的唯一來源。
- 若 auto memory 與 `AGENTS.md` 衝突，以使用者本次指令與 `AGENTS.md` 為準，並回報衝突。
