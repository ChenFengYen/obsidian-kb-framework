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

- `OV-Papers/enrich-tasks/`（v1 佈局，前綴見下節）
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

## v2.1：領域資料夾不再帶 `OV-` 前綴

v1 與 v2.0 產生的領域目錄叫 `OV-Pheno`、`OV-Papers`；v2.1 起直接叫 `Pheno`、`Papers`。前綴當初是為了讓領域目錄在檔案總管裡集中排序，但它出現在每一條路徑、每一個 domain 鍵與每一份文件裡，卻不帶任何資訊。

**既有 vault 不必改。** 前綴只影響新產生的 vault；已存在的 `OV-*` 目錄照常運作，`config.py` 的 fallback 掃描改用結構判定（頂層目錄底下有 `Map/` 或 `Note/` 就算領域），帶不帶前綴都認得。

要跟進改名時：

1. 先確認沒有帶路徑的 wikilink（`[[OV-Domain/Note/X]]` 形式）。純 `[[X]]` 連結不受搬移影響。
2. **不要對 `OV-` 做通用字串替換。** 錨定到實際的資料夾名逐一替換——上游 vault 做這件事時，`OV-DETR`（Open-Vocabulary DETR，一個模型名）差點被無腦替換毀掉。
3. 改完必查 `.gitignore`：綁了舊目錄名的忽略規則會靜默失效，並用 `git check-ignore -v` 實測。
4. 跑 `vault_health.py --broken-links`，數字不應增加。

## 規約編號登記表

`conventions/registry.yaml` 是 `KB-*` 編號的唯一權威。`validate_conventions.py` 會擋下未登記的 `rule_id`，也會擋下登記為 `shipped` 卻找不到筆記的編號。

下游 vault 的領域規約用自己的前綴（registry 的 `reserved_prefixes` 宣告，例如 `PHENO-`、`ML-`），內容不進本 repo，但編號空間保證不撞。

## v2 完成判準

- 新增來源筆記不會自動改寫其他檔案。
- 建立概念筆記前會先檢查重複與研究用途。
- 所有知識寫入都有使用者確認。
- 健康檢查不會污染 vault 的 Git 工作樹。
- README、Agent prompt、Skills 和 scripts 不再引用 v1 流程。
