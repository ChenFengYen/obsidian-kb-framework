@AGENTS.md

# Legacy Agent Entry

此檔保留供既有工具相容。新的共通入口是 `AGENTS.md`。

開始前先讀：

1. `AGENTS.md`
2. 依 `AGENTS.md` 定義的順序載入 Convention、領域 MOC 與可用 memory

若無法讀取 memory，套用 `AGENTS.md` 的 Memory fallback：照常進行唯讀探索與回答，但不得假裝已載入進度，並明確回報哪些狀態未經確認。
