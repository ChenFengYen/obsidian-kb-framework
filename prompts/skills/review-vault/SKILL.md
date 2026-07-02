---
name: review-vault
description: 診斷知識庫結構、連結與治理成本，提出少量優先行動
disable-model-invocation: true
---

# 知識庫架構診斷

## 任務

將健康指標解讀為可行動的治理建議，不把短筆記、孤兒或紅連結直接視為錯誤。

## 流程

1. 執行 `vault_health.py --summary` 與 `note_graph.py --json`。
2. 讀取 `vault_config.yaml`、Home、主要 MOC 與目前研究焦點。
3. 分析：
   - Home 到 Domain MOC 的導航是否完整。
   - MOC 是否有敘述與關係，而不只是連結清單。
   - 孤兒是否是有價值但尚未歸位的筆記。
   - 壞連結屬真缺筆記、歷史殘留或程式碼誤判。
   - 來源攝取是否明顯快於概念整合。
   - 暫存輸出、圖片與 Git 提交是否造成治理成本。
4. 輸出最多五項行動，依影響、風險與成本排序。

## 約束

- 不以固定行數要求批量充實。
- 不建議機械補連結或建立 stub。
- 修改建議必須指出具體檔案、理由與完成判準。
- 本 skill 只診斷；未經使用者確認不修改 vault。
