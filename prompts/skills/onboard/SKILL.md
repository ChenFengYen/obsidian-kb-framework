---
name: onboard
description: 將新筆記或論文納入知識庫——概念連結注入、候選概念發現，論文可選圖表提取
disable-model-invocation: true
argument-hint: "[筆記檔名或 paper-id，如 smith2025phenotyping 或 光合作用]"
---

# 筆記入庫

## 任務

將新加入的筆記（論文、書籍筆記、課程筆記等）完整納入知識庫，確保已有概念筆記被自動連結。

## 步驟

### Phase 1：識別筆記類型

根據 `$ARGUMENTS` 判斷：
- 若檔案在 `OV-Papers/PDF-md/` → 論文筆記
- 若檔案在 `OV-*/Note/` → 概念筆記
- 否則 → 搜尋 vault 中匹配的 .md 檔案

### Phase 2：概念連結注入

```bash
cd OV-Papers/scripts
python inject_links.py --paper-id $ARGUMENTS --dry-run
```

1. 先用 `--dry-run` 預覽將注入的連結
2. 報告：將注入 N 個概念連結，列出前 10 個
3. 確認後執行正式注入

### Phase 3：新概念發現

```bash
python extract_candidates.py --paper-id $ARGUMENTS
```

- 檢查筆記中是否有**尚未建立筆記**的重要術語
- 列出候選概念供使用者決定是否建立 stub

### Phase 4（可選）：圖表提取（僅論文，需啟用 paper_pipeline）

若為論文筆記且 `vault_config.yaml` 中 `modules.paper_pipeline: true`：

```bash
python extract_figures.py --paper-id $ARGUMENTS
python insert_figures.py --paper-id $ARGUMENTS
```

### Phase 5：報告

輸出入庫摘要：
- 注入了多少個概念連結
- 發現了多少個新候選概念
- （若論文）提取了多少張圖表
- 建議的 MOC 歸屬

## 注意事項

- 每次入庫前自動重建 concept_index（確保包含最新概念）
- 入庫不限於論文——任何 .md 筆記都可以接受連結注入和概念發現
- 若使用者最近新增了概念筆記，建議先跑 `python concept_index.py --force`
