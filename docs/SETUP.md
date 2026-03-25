# 安裝指南

## 系統需求

- Python 3.10+
- Obsidian（桌面版）
- AI 代理工具（Claude Code / Gemini CLI / Codex CLI / 其他）

## 安裝步驟

### 1. 取得框架

```bash
git clone https://github.com/YOUR_USERNAME/obsidian-kb-framework.git
cd obsidian-kb-framework
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

可選依賴：
```bash
# 論文管線（PDF 圖表提取）
pip install pymupdf pillow

# Zotero 整合
pip install pyzotero python-dotenv
```

### 3. 建立知識庫

```bash
python setup.py
```

依提示輸入：
- 知識庫名稱
- 領域分類（名稱、描述、關鍵字）
- 學習目標和經驗等級
- 是否啟用 Zotero / 論文管線

### 4. 用 Obsidian 開啟

開啟 Obsidian → Open Vault → 選擇 setup.py 產生的目錄。

### 5. 安裝 Obsidian 插件（推薦）

- **QuickAdd**：閱讀時快速建立概念筆記
- **Dataview**：結構化查詢筆記
- **obsidian-git**：自動 Git 同步（多機器）

### 6. 啟動 AI 代理

```bash
cd my-knowledge-base
claude  # 或 gemini, codex 等
```

AI 會自動讀取 `CLAUDE.md` 和 `vault_config.yaml`，引導你開始。

## Zotero 設定（可選）

若啟用 Zotero 模組：

1. 建立 `zotero-tools/.env`：
```
ZOTERO_API_KEY=your_key_here
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_LIBRARY_TYPE=user
```

2. 取得 API Key：[Zotero Settings](https://www.zotero.org/settings/keys)

## 驗證安裝

```bash
cd my-knowledge-base/OV-Papers/scripts
python config.py  # 應無錯誤
python vault_health.py --summary  # 顯示 vault 摘要
```
