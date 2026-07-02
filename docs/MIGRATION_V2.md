# v1 → v2 Migration Guide

v2 是 breaking change：框架不再提供自動連結注入、批量 stub 或以行數為目標的筆記充實。

## 為什麼改變

實際使用顯示，關鍵字匹配無法判斷概念在特定段落中的語意。大量自動連結會製造錯誤關係、紅連結與審查負擔；批量擴寫也容易讓筆記變長但沒有回答新的問題。

v2 改以使用者問題作為選擇機制，讓 AI 只處理當下真正需要的知識。

## 已移除

### Scripts

- `concept_index.py`
- `inject_links.py`
- `extract_candidates.py`
- `create_stubs.py`
- `prepare_enrich_tasks.py`
- `quickadd-create-concept.js`

### Skills

- `/enrich`
- `/onboard`
- `/process-inbox`
- `/pipeline-status`

### 產物

- `OV-Papers/enrich-tasks/`
- `OV-Papers/enrich-inbox.md`
- `concept_index.json`
- `candidates_review.md`
- `link_report.md`

## 升級步驟

1. 提交或備份既有 vault，確認工作樹乾淨。
2. 刪除上述已棄用 scripts 與 skills；歷史報告可保留為普通紀錄。
3. 將 `vault_config.yaml` 中的 `filtering`、`link_injection`、`enrichment` 與 `preferences.auto_rescan` 移除。
4. 設定 `preferences.link_policy: manual-semantic`。
5. 更新 Agent 規則，明確禁止自動連結與自動 stub。
6. 執行 `vault_health.py --broken-links`，人工分類真正缺筆記與程式碼誤判。
7. 從一個實際研究問題開始，驗證搜尋、回答、提案、確認、寫入流程。

## 舊內容如何處理

- 不需要移除既有正確 wikilink。
- 不要機械重寫所有歷史筆記。
- 對可疑連結逐篇讀上下文後修正。
- 帶有 `AI-ENRICHED` 標記的筆記可在真正被研究問題用到時再審查。
- 空 stub 若沒有任何引用或用途，可在人工確認後刪除；不要自動補內容。

## v2 完成判準

- 新增來源筆記不會自動改寫其他檔案。
- 建立概念筆記前會先檢查重複與研究用途。
- 所有知識寫入都有使用者確認。
- 健康檢查不會污染 vault 的 Git 工作樹。
- README、Agent prompt、Skills 和 scripts 不再引用 v1 流程。
