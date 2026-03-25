---
name: suggest-next
description: 基於知識庫現狀和學習目標，推薦下一步行動
disable-model-invocation: true
---

# 學習路徑建議

## 任務

分析知識庫的現狀，結合使用者的學習目標，推薦最有價值的下一步行動。

## 步驟

### Phase 1：了解現狀

1. 讀取 `vault_config.yaml` 的 `learning.goals`、`current_focus`、`experience_level`
2. 快速掃描筆記充實度分佈（可用 vault_health.py --richness 或直接掃描）
3. 執行 `python OV-Papers/scripts/note_graph.py --json --top 10` 了解連結結構

### Phase 2：識別知識缺口

- **概念缺口**：current_focus 領域中的 stub/thin 筆記 → 最需要深化的概念
- **連結缺口**：note_graph 中孤立的概念或缺少跨域連結的區域
- **結構缺口**：缺少 MOC 的領域、沒被任何 MOC 收錄的概念

### Phase 3：生成建議

輸出 3-5 個具體建議，按預估價值排序：

```
## 建議下一步

基於你的學習目標「{goal}」和目前知識庫狀態：

### 1. 🎯 [最推薦的行動]
- 為什麼：[與學習目標的關聯]
- 怎麼做：[具體步驟]
- 預估效果：[完成後知識庫的改善]

### 2. ...

### 3. ...
```

建議類型可以是：
- **深化概念**：「深入了解 [[概念名]]，它是連接 A 和 B 的橋樑」
- **探索新主題**：「你的 X 領域缺少關於 Y 的知識」
- **建立連結**：「[[A]] 和 [[B]] 可能有關聯，但目前沒有連結」
- **整理結構**：「X 領域有 15 個概念但沒有 MOC，建議建立」
- **閱讀文獻**：「根據知識缺口，建議閱讀關於 X 的 review paper」（若啟用 Zotero）

## 注意事項

- 建議要具體到筆記名稱，不要泛泛而談
- beginner：偏向「探索新主題」和「深化基礎概念」
- intermediate：偏向「建立連結」和「填補缺口」
- advanced：偏向「結構整理」和「跨域連結」
- 每個建議都要說明「為什麼這個比其他的優先」
