# 安裝指南

## 系統需求

- Python 3.10+
- Obsidian 桌面版
- 能在專案目錄讀寫檔案與執行命令的 AI 代理

## 安裝

```bash
git clone https://github.com/YOUR_USERNAME/obsidian-kb-framework.git
cd obsidian-kb-framework
pip install -r requirements.txt
python setup.py
```

setup 會詢問領域、學習目標、經驗程度，以及是否啟用 Zotero／論文工具。也可使用現有設定：

```bash
python setup.py --config examples/configs/neuroscience.yaml --target ./my-knowledge-base
```

## 開啟 Vault

在 Obsidian 選擇 setup 產生的目錄。推薦但非必要的插件：

- Dataview：查詢結構化 metadata。
- obsidian-git：多機器同步；應設定 debounce，避免每分鐘提交。
- QuickAdd：只用於 capture 到 Inbox，不自動建立概念 stub 或注入連結。

## 啟動 Agent

```bash
cd my-knowledge-base
claude  # 或 codex、gemini 等
```

setup 會產生 `AGENTS.md` 作為共通規則，並產生 `CLAUDE.md`、`GEMINI.md` adapter。Codex 直接讀取 `AGENTS.md`；Claude Code 與 Gemini CLI 由各自 adapter 匯入。其他本地 Agent 應在啟動時明確將 `AGENTS.md` 注入 system／project context。

## 可選依賴

```bash
pip install pymupdf pillow          # PDF 圖表
pip install pyzotero python-dotenv  # Zotero
```

Zotero 憑證應放在不納入 Git 的 `.env`，不要寫進 vault 或公開設定範例。

## 驗證

```bash
cd my-knowledge-base
python OV-Papers/scripts/vault_health.py --summary
```

另外確認 `.claude/skills/` 只包含 `init-domain`、`review-vault`、`suggest-next`、`debrief`。
