---
name: review-vault
description: 知識庫架構診斷——結合數據分析和 AI 架構建議，輸出優先行動清單
disable-model-invocation: true
---

# 知識庫架構診斷

## 任務

分析知識庫的結構健康狀態，提供架構層面的改善建議（不只是統計數字）。

## 步驟

### Phase 1：收集數據

1. 執行 `python OV-Papers/scripts/vault_health.py --summary` 取得快速摘要
2. 執行 `python OV-Papers/scripts/note_graph.py --json` 取得連結圖分析
3. 讀取 `vault_config.yaml` 的 learning.goals 和 current_focus

### Phase 2：分析架構

基於收集的數據，分析以下面向：

**知識覆蓋度**：
- 哪些領域（OV-* 資料夾）的筆記最少？與使用者的學習目標對比
- stub/thin 比例高的領域 → 知識基礎薄弱

**連結品質**：
- 孤兒概念（不在任何 MOC 中）→ 需要被組織
- 孤立群集（note_graph 的 clusters）→ 缺少跨領域連結
- 橋接概念不足 → 知識碎片化

**MOC 狀態**：
- 哪些 MOC 是連結清單而非思考地圖 → 需要重寫
- 哪些領域缺少 MOC → 知識無法被導航

**待處理事項**：
- AI-ENRICHED 待審數量
- 壞連結數量
- Zotero-Vault 落差（若啟用 Zotero）

### Phase 3：輸出行動清單

按優先度排列具體行動，格式：

```
## 架構診斷報告

### 📊 健康摘要
[1-2 行總結]

### 🔴 高優先（立即行動）
1. [具體行動 + 原因 + 預估影響]
2. ...

### 🟡 中優先（本週處理）
1. ...

### 🟢 低優先（有空再做）
1. ...

### 💡 架構建議
- [結構性改善建議，如 MOC 重組、領域合併等]
```

## 注意事項

- 建議要具體可執行（「充實 OV-Pheno 的 15 個 stub 筆記」而非「改善筆記品質」）
- 考量使用者的學習目標，優先建議與目標相關的行動
- 若使用者是 beginner，行動清單不要超過 5 項，避免壓倒
