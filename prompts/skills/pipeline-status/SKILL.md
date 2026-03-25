---
name: pipeline-status
description: 檢查知識庫建設 pipeline 的目前進度
disable-model-invocation: true
---

# Pipeline 進度檢查

## 任務

掃描知識庫，報告各階段的處理進度。

## 檢查項目

### 1. 筆記充實度統計
掃描所有 `OV-*/Note/` 目錄中的 `.md` 檔案，統計：
- 排除 YAML frontmatter 後的實際內容行數
- 按充實度分級：空白/stub (0-3行)、薄弱 (4-9行)、基本 (10-29行)、充實 (≥30行)
- 各領域（OV-* 資料夾）的分佈

### 2. AI 充實進度
- 搜尋帶有 `<!-- AI-ENRICHED - NEEDS REVIEW -->` 標記的筆記
- 列出已充實但未審核的筆記
- 列出已審核（標記已移除）的筆記數量

### 3. 任務檔狀態
檢查 `OV-Papers/enrich-tasks/` 中的任務檔：
- 各批次包含哪些筆記
- 哪些筆記已完成充實、哪些未處理

### 4. 論文處理進度
讀取 `OV-Papers/PDF_status.md`，統計：
- 已提取圖表的論文數
- 已注入連結的論文數
- 尚未處理的論文數

## 輸出格式

```
=== Pipeline 進度報告 ===

📊 筆記充實度
  充實 (≥30行): XX 篇
  基本 (10-29行): XX 篇
  薄弱 (4-9行): XX 篇
  空白/stub (0-3行): XX 篇

📝 AI 充實進度
  已充實待審核: XX 篇
  Batch 1: X/5 完成
  Batch 2: X/5 完成
  ...

📄 論文處理進度
  圖表提取: XX/162
  連結注入: XX/162

⚠️ 待處理事項
  - ...
```
