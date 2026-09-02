# obsidian-kb-framework

English version: [README.en.md](README.en.md)

AI 引導式 Obsidian 知識庫框架。v2 採用問題驅動協作：AI 先搜尋既有知識，再回答問題、辨識缺口，並在使用者確認後更新筆記。

## v2 核心原則

- `Home → Domain MOC → Notes` 作為導航骨架。
- 連結是閱讀上下文後的語意判斷，不做關鍵字批量注入。
- 不自動建立 stub，不以筆記行數作為充實目標。
- 優先更新既有筆記；新筆記必須能回答獨立問題。
- 重要概念採多源驗證，單一來源發現需明確標示。
- 對話洞見先提出候選，再由使用者確認寫入。

## 適合誰

- 需要管理論文、概念、實驗與研究決策的研究者。
- 正在學習陌生領域，希望讓 AI 協助建立長期知識網路的人。
- 需要可稽核、可逐步演進，而非大量自動生成內容的知識庫。

## AI 代理相容性

`AGENTS.md` 是生成 vault 的跨 Agent 核心規則；`CLAUDE.md` 與 `GEMINI.md` 是薄平台 adapter。Codex 可直接載入 `AGENTS.md`，Claude Code／Gemini CLI 透過 adapter 匯入同一份規則，避免維護平行副本。目前 skills 仍安裝於 `.claude/skills/`；跨平台 skill adapter 留待後續版本。

## 快速開始

```bash
git clone https://github.com/ChenFengYen/obsidian-kb-framework.git
cd obsidian-kb-framework
pip install -r requirements.txt
python setup.py
```

用 Obsidian 開啟產生的 vault，接著在 vault 根目錄啟動 AI 代理。第一次使用可執行 `/init-domain`，也可以直接提出研究問題。

## 工作流程

```text
使用者提出問題
  → AI 搜尋 vault 與現有來源
  → 綜合回答並標示知識缺口
  → 提出更新／新建筆記候選
  → 使用者確認
  → 寫入並驗證連結
  → /debrief 記錄下次繼續點
```

## Skills

| Skill | 用途 |
|:--|:--|
| `/init-domain` | 建立領域、MOC 與第一批研究問題 |
| `/review-vault` | 診斷孤兒、壞連結、MOC 覆蓋與治理問題 |
| `/suggest-next` | 依目前問題與知識缺口排序下一步 |
| `/debrief` | 回收對話中已確認的洞見 |

## 工具

| 工具 | 用途 |
|:--|:--|
| `vault_health.py` | 唯讀健康診斷，報告預設寫入系統暫存目錄 |
| `note_graph.py` | 分析孤兒、hub、bridge 與跨領域連結 |
| `audit_images.py` | 圖片引用與孤立附件稽核 |
| `rename_images.py` | 依人工計畫批次重命名圖片與引用 |

論文圖表與 Zotero 工具屬可選模組，不會自動建立概念連結。

## 框架與產物

repo 是模板來源，本身不是知識庫。`setup.py` 讀 `vault_config.yaml` 生成一個可獨立版本控管的 vault，兩邊的檔案有對應關係但職責不同。

```text
obsidian-kb-framework/                     模板來源，本身不是任何人的 vault
|
+-- AGENTS.md                              給「來改框架的 agent」的規則
+-- setup_v2.py                            生成器；vault 的 AGENTS.md 由它算出來
+-- prompts/
|   +-- CLAUDE.md GEMINI.md AgentRules.md  薄轉接檔，原樣複製進 vault
|   +-- skills/                            init-domain review-vault suggest-next debrief
+-- conventions/
|   +-- registry.md                        KB-* 編號與 trigger 詞彙的唯一權威
|   +-- core/ obsidian/                    預設 pack
|   +-- research/ windows-zh-tw/           選用 pack
+-- framework/                             validate_conventions vault_health note_graph
+-- paper-pipeline/ zotero-tools/          選用模組，預設不裝
+-- templates/ examples/ docs/ tests/
        |
        |   python setup.py                依 vault_config.yaml 決定裝哪些
        v
your-vault/                                產物，可獨立成一個 git repo
|
+-- AGENTS.md                              啟動權威，規則全文只有這一份
+-- CLAUDE.md GEMINI.md AgentRules.md      薄轉接；Codex 等直接讀 AGENTS.md
+-- vault_config.yaml
+-- Home.md
+-- <Domain>/
|   +-- Map/ Note/ Pic/                    Map 內含 <Domain>_MOC.md
+-- KnowledgeBase/
|   +-- Convention/                        依 packs 安裝的規約，加一份 registry.md
|   +-- Map/                               Knowledge Base Conventions.md
+-- tools/                                 從 framework/ 複製過去
+-- .claude/skills/
+-- Papers/                                只有啟用 zotero 或 paper_pipeline 時才建立
    +-- PDF-raw/ PDF-md/ Final-md/ PDF-assets/ scripts/
```

**沒有任何檔名是三家 agent 通吃的**，所以規則全文只存在 `AGENTS.md`，其餘都是薄轉接檔。轉接檔一旦長出自己的規則，就變成第二份權威。

兩邊的 `AGENTS.md` 是不同的兩份東西，也是不同的兩件工作：repo 根目錄那份給「來改框架的人」；vault 那份是 `setup_v2.py` 依 `vault_config.yaml` **算出來的**——啟用了哪些 pack、哪些模組，會決定任務路由表多出哪幾列。它不是複製某個模板檔，所以要改生成的規則就改生成器，不是去找一份範本。

## 文件

- [METHODOLOGY.md](docs/METHODOLOGY.md) — 問題驅動方法論
- [MIGRATION_V2.md](docs/MIGRATION_V2.md) — 從 v1 升級
- [SETUP.md](docs/SETUP.md) — 安裝與配置
- [USER_GUIDE.md](docs/USER_GUIDE.md) — 日常使用
- [AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md) — Agent 行為
- [SCRIPTS_REFERENCE.md](docs/SCRIPTS_REFERENCE.md) — 保留工具清單

## 授權

MIT License
