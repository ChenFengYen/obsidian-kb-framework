# obsidian-kb-framework

AI 引導式知識庫建設框架 — 將 AI 對話中的知識系統化納入 Obsidian 知識庫。

## 這是什麼？

一套以 **AI 代理為核心** 的知識庫建設系統。透過 AI 引導，幫助使用者將學習過程中的資訊（論文、書籍、課程、對話）轉化為結構化、相互連結的知識網路。

基於 [LYT（Linking Your Thinking）](https://www.linkingyourthinking.com/) 方法論，但你不需要先了解 LYT — AI 代理會在互動中引導你。

## 適合誰？

- 想學習陌生領域但不知道如何組織知識的人
- 研究者需要系統化管理文獻和概念筆記
- 任何想將「與 AI 對話的收穫」沉澱為長期知識的人

**不限特定領域** — 植物科學、神經科學、軟體工程、法律、語言學皆適用。

## AI 代理相容性

本框架以 **Claude Code v1.0.33**（Claude Opus 4.6, 1M context）開發和測試。但不依賴 Claude 專有功能，任何支援終端讀寫檔案和執行腳本的 AI 代理都適用：

| 工具 | 相容性 |
|:--|:--|
| Claude Code (Anthropic) | ✅ 開發環境 |
| Gemini CLI (Google) | ✅ 適用 |
| Codex CLI (OpenAI) | ✅ 適用 |
| Grok CLI (xAI) | ✅ 適用 |

差異在於：模型效能影響筆記生成品質，上下文窗口影響單次處理的筆記數量。

## 快速開始

### 1. 安裝

```bash
git clone https://github.com/YOUR_USERNAME/obsidian-kb-framework.git
cd obsidian-kb-framework
pip install -r requirements.txt
```

### 2. 建立知識庫

```bash
python setup.py
```

互動式設定會引導你：
- 定義領域分類
- 設定學習目標
- 選擇可選模組（Zotero、論文管線）

### 3. 開始使用

```bash
cd my-knowledge-base
claude  # 或你的 AI 代理工具
```

AI 代理會自動讀取配置，引導你開始建設知識庫。

## 核心功能

### AI 代理能力（8 個 Skills）

| 指令 | 功能 |
|:--|:--|
| `/init-domain` | AI 引導式建庫（對話了解領域 → 建議結構 → 生成配置） |
| `/review-vault` | 架構診斷 + 優先行動建議 |
| `/suggest-next` | 基於知識缺口的學習路徑推薦 |
| `/debrief` | Session 知識回收（回顧對話 → 沉澱洞見到筆記） |
| `/enrich` | 批量充實薄弱筆記 |
| `/onboard` | 新筆記入庫（連結注入 + 概念發現） |
| `/pipeline-status` | 檢查建設進度 |
| `/process-inbox` | 處理 QuickAdd 概念佇列 |

### 問題驅動模式

直接向 AI 提問 → AI 搜尋知識庫回答 → 發現缺口時提議建立新筆記 → 知識自然成長。

### 知識回收

對話中的洞見不會遺失在聊天記錄中：
- **即時捕獲**：AI 在對話中標示可沉澱的洞見
- **Session 回收**：結束時自動回顧對話，提議更新筆記

### 自動化工具鏈

| 工具 | 功能 |
|:--|:--|
| `concept_index.py` | 建立概念索引（自動快取） |
| `inject_links.py` | 自動注入 `[[概念]]` 連結 |
| `extract_candidates.py` | 從筆記中發現新概念候選 |
| `vault_health.py` | 知識庫健康診斷 |
| `note_graph.py` | 連結圖分析（群集、橋接、孤兒） |
| `prepare_enrich_tasks.py` | 生成批量充實任務 |

### 可選模組

- **Zotero 整合**：文獻搜尋、匯入、自動 Tag
- **論文管線**：PDF 圖表提取、論文連結注入

## 目錄結構

```
your-vault/
├── Home.md                    # 知識入口
├── vault_config.yaml          # 單一配置檔
├── CLAUDE.md                  # AI 代理行為定義
├── .claude/skills/            # 8 個 AI 指令
├── OV-Domain1/
│   ├── Map/                   # 內容地圖 (MOC)
│   ├── Note/                  # 概念筆記
│   └── Pic/                   # 圖片
├── OV-Domain2/...
└── OV-Papers/
    ├── PDF-md/                # 論文/來源筆記
    ├── scripts/               # 自動化工具
    └── enrich-inbox.md        # 概念佇列
```

## 文件

- [METHODOLOGY.md](docs/METHODOLOGY.md) — LYT 方法論與兩路徑策略
- [docs/SETUP.md](docs/SETUP.md) — 詳細安裝指南
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) — 日常使用指南
- [docs/AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md) — AI 代理行為說明
- [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md) — 領域自訂指南

## 授權

MIT License
