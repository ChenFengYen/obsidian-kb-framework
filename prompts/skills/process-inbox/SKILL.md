---
name: process-inbox
description: 處理 QuickAdd 建立的概念筆記佇列，逐一充實 stub 筆記
disable-model-invocation: true
---

# 處理概念筆記佇列

## 任務

讀取 `OV-Papers/enrich-inbox.md` 中所有 `Status: pending` 的概念筆記請求，逐一充實。

## 步驟

1. **讀取佇列**：讀取 `OV-Papers/enrich-inbox.md`，列出所有 pending 的概念

2. **逐一充實**（每個概念筆記）：
   a. 讀取 stub 筆記的現有內容（含 source 欄位指向的來源論文）
   b. 讀取來源論文的完整內容，理解該概念在論文中的上下文
   c. 搜尋知識庫中其他提及該概念的論文（用 Grep 搜尋 concept name）
   d. 按 LYT 格式充實筆記：
      - 一句話版（核心定義）
      - 定義（詳細解釋）
      - 核心概念（2-5 個要點）
      - 在我的研究中的應用
      - 相關筆記（3-7 個連結）
      - 待解決問題（1-3 個）
   e. 在筆記結尾加上 `<!-- AI-ENRICHED - NEEDS REVIEW -->` 標記

3. **更新佇列狀態**：將已處理的項目 Status 改為 `done`

4. **更新概念索引**：提醒使用者執行 `python concept_index.py --force` 重建索引

5. **報告**：
   - 完成了幾個概念筆記
   - 每個筆記的充實前後行數對比
   - 建議是否需要執行 `inject_links.py --rescan`

## 注意事項

- 來源論文的上下文（inbox 中的 Context 區段）僅供定位參考，必須閱讀來源論文全文
- 使用 `[[citekey]]` 格式連結論文（不用 alias）
- 偏好植物生理學術語的深度解釋
- 若概念已有 ≥30 行內容，視為已充實，跳過並更新狀態為 done
