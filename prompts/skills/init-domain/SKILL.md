---
name: init-domain
description: 透過對話了解使用者的領域與問題，建立初始 MOC 和配置
disable-model-invocation: true
---

# 初始化領域

## 任務

以使用者真正想回答的問題為起點，建立最小可用的領域結構。

## 步驟

1. 詢問研究／學習領域、目前焦點、經驗程度及三個最重要問題。
2. 建議 3–8 個 `OV-*` 領域；關鍵字只作搜尋與路由提示。
3. 為每個領域提出一個 MOC，包括領域敘述、2–3 個主題群和待釐清問題。
4. 呈現完整結構，等待使用者確認。
5. 確認後建立：
   - `vault_config.yaml`
   - `OV-{name}/Map`、`Note`、`Pic`
   - `OV-Papers/PDF-raw`、`PDF-md`、`Final-md`、`PDF-assets`、`scripts`
   - `Home.md` 與各 Domain MOC
6. 說明問題驅動流程，邀請使用者選擇第一個問題開始。

## 約束

- 不建立大量空白概念 stub。
- 不產生 enrich queue。
- 不設定自動連結或自動 rescan。
- 分類只是初始假設；知識關係由 MOC 與人工判斷的連結表達。
