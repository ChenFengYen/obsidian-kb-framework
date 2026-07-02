@AGENTS.md

# Gemini CLI Adapter

`AGENTS.md` 是本 vault 的跨 Agent 核心規則。Gemini CLI 應載入該檔後再套用以下平台補充：

- 使用 `/memory show` 確認 `AGENTS.md` 已進入目前 context。
- 若設定 `context.fileName`，應包含 `AGENTS.md` 與 `GEMINI.md`。
- 未確認規則已載入前，只進行唯讀探索，不修改 vault。
