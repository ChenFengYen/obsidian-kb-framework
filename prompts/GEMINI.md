@AGENTS.md

# Gemini / Antigravity Adapter

`AGENTS.md` 是本 vault 的跨 Agent 核心規則。**本檔不得放置任何規則**——放進來就成為第二份權威，而下面第三點說明了為什麼那特別危險。

三件經實測確認的平台行為（2026-09-02，Antigravity IDE）：

1. **Antigravity 會自動載入 workspace 根目錄的 `AGENTS.md`**，不需要本檔轉介。Gemini CLI 則預設只讀 `GEMINI.md`，除非設定 `context.fileName` 納入 `AGENTS.md`——本檔存在是為了後者。
2. **Antigravity 不展開 `@` import。** 上面第一行在 Gemini CLI 可能有效，在 Antigravity 只會被當成一行文字。因此本檔絕不能靠 import 引入正文。
3. **Antigravity 把每個規則檔平級注入 `<user_rules>`，沒有優先序 metadata。** 兩份檔案的內容衝突時，由模型當場依語意自行裁決，結果不穩定。**唯一可靠的作法是不製造衝突。**

若你不使用 Gemini CLI，可在 `vault_config.yaml` 的 `agent.adapters` 移除 `gemini`，讓根目錄只留 `AGENTS.md` 一份規則檔。

啟動時：確認 `AGENTS.md` 已進入 context（Gemini CLI 可用 `/memory show`），並確認看得到它最後一行的 `AGENTS-EOF`。看不到就是被截斷了——Antigravity 實測的載入上限是 **24,000 bytes**，超過的部分靜默截尾。未確認規則完整載入前，只進行唯讀探索，不修改 vault。
