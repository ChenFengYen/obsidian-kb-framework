# 使用者日常操作指南

## 開始一次對話

在 vault 根目錄啟動 AI 代理，直接描述本次問題、決策或希望整理的材料。若是延續工作，附上相關 project note 或 MOC。

## 提問與沉澱

```text
你：目前有哪些筆記能解釋 X？它們之間有什麼矛盾？
AI：搜尋 vault → 綜合回答 → 標示缺口
你：確認更新 A，暫時不要建立 B
AI：修改 → 驗證 → 回報
```

AI 不會因為看到新術語就自動建立筆記，也不會批量插入 wikilink。

## 新資料入庫

1. 將來源保存為 source note 或 `OV-Papers/PDF-md/{citekey}.md`。
2. 記錄可追溯的書目資料與摘要。
3. 只有在研究問題需要時，才把來源內容整合進概念筆記或 MOC。
4. 連結應由閱讀上下文後人工確認。

## 檢查知識庫

- `/review-vault`：解讀健康報告並排序治理工作。
- `python OV-Papers/scripts/vault_health.py --summary`：快速摘要。
- `python OV-Papers/scripts/note_graph.py`：檢查孤兒、hub 與 bridge。

診斷結果是候選，不代表每個短筆記、孤兒或紅連結都必須修正。

## 不知道下一步

使用 `/suggest-next`。建議應優先考慮目前研究問題、缺少證據的概念與尚未連回 MOC 的有效筆記。

## 結束對話

使用 `/debrief`：

1. 列出本次可沉澱的洞見。
2. 決定更新哪些既有筆記。
3. 確認是否真的需要新筆記。
4. 寫入後提供下次繼續點。

## 指令速查

| 指令 | 功能 |
|:--|:--|
| `/init-domain` | 初始化領域與 MOC |
| `/review-vault` | 診斷 vault |
| `/suggest-next` | 建議下一步 |
| `/debrief` | 回收已確認洞見 |
