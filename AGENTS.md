# obsidian-kb-framework Agent Entry

本檔是維護 framework repository 時的跨 Agent 入口。

## 開始前

1. 讀取 `README.md`、`docs/METHODOLOGY.md` 與 `docs/MIGRATION_V2.md`。
2. 確認修改的是 framework 本身，還是 setup 產生的 vault template。
3. 先檢查 `git status`；不得覆蓋使用者既有變更。

## 產品原則

- v2 採問題驅動、proposal-first 的知識建設模式。
- 不恢復關鍵字自動連結、批量 stub 或批量 enrich。
- `prompts/AGENTS.md` 是生成 vault 的跨 Agent 核心規則。
- `prompts/CLAUDE.md` 與 `prompts/GEMINI.md` 只能包含平台 adapter，不複製核心規則。
- 平台差異應留在 adapter；通用行為修改只改 canonical template。

## 驗證

- 修改 Python 後執行語法檢查。
- 修改 YAML 後執行解析檢查。
- 修改 setup 或 prompt 後建立 smoke vault，確認產生 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 與預期 skills。
- 執行 `git diff --check` 與 mojibake 掃描。

## Git 安全

breaking change、commit 或 push 前，先向使用者報告修改與刪除項目、相容性風險、測試結果及預計 commit message，取得明確核准後才執行。
