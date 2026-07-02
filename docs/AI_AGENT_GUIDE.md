# AI 代理行為說明

## 規則入口

- `AGENTS.md`：跨 Agent 核心規則與唯一通用行為來源。
- `CLAUDE.md`：Claude Code adapter，只匯入 `AGENTS.md` 並補充 Claude-specific 行為。
- `GEMINI.md`：Gemini CLI adapter，只匯入 `AGENTS.md` 並補充 context 驗證。
- 本地 Agent：launcher 或 system prompt 必須明確注入 `AGENTS.md`；若無法確認載入，只能進行唯讀探索。
## 職責

AI 代理有三項核心職責：

1. 搜尋並綜合 vault 中已存在的知識。
2. 辨識內容缺口、錯誤與結構問題。
3. 在使用者確認後，將有效洞見寫回適當筆記。

## Proposal-first

涉及建立、重寫、搬移或大量修改筆記時，先提供候選清單、理由與影響範圍。只有在使用者確認後執行。

## 禁止行為

- 依關鍵字自動注入 wikilink。
- 自動建立空 stub 來消除紅連結。
- 以固定行數或模板欄位為目的批量擴寫筆記。
- 未讀上下文就批量替換連結。
- 將暫存報告與中間產物寫進 vault。

## 搜尋順序

1. 讀取相關 Domain MOC。
2. 搜尋概念、同義詞與 citekey。
3. 閱讀最相關筆記的上下文。
4. 必要時才查外部來源，並區分 vault 內容與新取得資訊。

## 寫入原則

- 優先更新既有筆記。
- 新筆記必須有明確主題、研究用途或獨立問題。
- 重要主張保留來源與不確定性。
- 寫入後檢查 wikilink、檔名與目標位置。
- 大規模修改先 dry-run 並保留可審查 diff。

## Skills

Skills 位於 `.claude/skills/`。每個 skill 應清楚定義觸發條件、輸入、核准點、輸出與驗證方式。v2 內建 `/init-domain`、`/review-vault`、`/suggest-next`、`/debrief`。
