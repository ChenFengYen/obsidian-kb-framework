# Scripts 目錄指南

本文件記錄 `OV-Papers/scripts/` 下所有腳本的功能、依賴關係與使用建議。

最後更新：2026-03-16

---

## 腳本總覽

| 腳本 | 功能 | 狀態 | 使用頻率 |
|:--|:--|:--|:--|
| `config.py` | 路徑常數、領域映射 | 核心 | 被所有腳本 import |
| `concept_index.py` | 概念索引建立與快取 | 核心 | 高（每次連結注入前） |
| `inject_links.py` | 論文中注入 `[[概念]]` 連結 | 核心 | 高（新概念/新論文後） |
| `prepare_enrich_tasks.py` | 產生批量充實任務檔 | 調整後 | 中（批量打底用） |
| `extract_candidates.py` | 從論文挖掘概念候選 | 保留 | 低（大掃描用） |
| `create_stubs.py` | 從審核清單建立 stub | 保留 | 低（QuickAdd 已覆蓋多數場景） |
| `status_tracker.py` | 解析/更新 PDF_status.md | 維護 | 低（逐漸淡出） |
| `extract_figures.py` | 從 PDF 提取圖表 | 維護 | 低（論文入庫時） |
| `insert_figures.py` | 將圖表嵌入論文 markdown | 維護 | 低（論文入庫時） |
| `quickadd-create-concept.js` | Obsidian QuickAdd macro | 核心 | 高（閱讀時即時建 stub） |
| `audit_images.py` | 圖片盤點：掃描全 vault 圖片，交叉比對引用，分類命名，輸出報告 | 核心 | 低（定期盤點） |
| `rename_images.py` | 批次重命名圖片 + 自動更新 .md 引用（plan file + dry run） | 核心 | 低（整理時） |

**狀態說明**：
- **核心**：問題驅動模式和日常使用的基礎，需持續維護
- **調整後**：已配合新策略修改，功能保留但定位改變
- **保留**：功能有用但使用頻率降低，不需主動投入
- **維護**：維持現狀，不修改也不刪除

---

## 依賴關係圖

```
config.py  ← 所有腳本的根依賴（路徑、DOMAIN_MAP、SECTION_MARKERS）
  │
  ├─ concept_index.py  ← 概念索引建立（~268 筆記、~1400 匹配詞）
  │    │
  │    ├─ inject_links.py  ← 連結注入（+ status_tracker.py）
  │    └─ extract_candidates.py  ← 概念候選挖掘
  │
  ├─ prepare_enrich_tasks.py  ← 批量任務檔產生
  ├─ create_stubs.py  ← stub 建立
  │
  ├─ status_tracker.py  ← PDF 進度追蹤
  │    │
  │    ├─ extract_figures.py  ← 圖表提取（+ PyMuPDF）
  │    └─ insert_figures.py  ← 圖表嵌入
  │
  └─ quickadd-create-concept.js  ← Obsidian 端，無 Python 依賴
```

---

## 核心腳本詳細說明

### config.py — 路徑與設定

所有路徑常數的唯一來源。修改路徑結構時只需改這裡。

主要匯出：
- `VAULT_ROOT`, `PAPERS_ROOT`, `PDF_MD_DIR`, `PDF_RAW_DIR`
- `OV_FOLDERS` — 9 個 OV-* 領域資料夾路徑
- `DOMAIN_MAP` — 論文領域關鍵字 → OV-* 資料夾的映射
- `CONCEPT_INDEX_CACHE` → `concept_index.json`
- `SECTION_MARKERS` — 論文 markdown 的 emoji 區段標頭

### concept_index.py — 概念索引

掃描所有 `OV-*/Note/*.md`，建立可搜尋的概念索引。

```bash
python concept_index.py          # 自動快取，僅在檔案更新時重建
python concept_index.py --force  # 強制重建
```

索引結構（JSON）：
```json
{
  "notes": { "stem": {"stem": "...", "path": "...", "domain": "...", "aliases": [...]} },
  "alias_map": { "alias": "stem" }
}
```

關鍵過濾規則：
- 英文 alias 最短 12 字元（`MIN_ALIAS_LEN`）
- 40+ 泛用詞黑名單（database, model, network...）
- 中文 stem 直接匹配（不用 `\b`）

### inject_links.py — 連結注入

在論文 markdown 中自動將概念名稱替換為 `[[概念]]` 連結。

```bash
python inject_links.py --paper-id briggs1920quantitative  # 單篇
python inject_links.py --rescan --dry-run                 # 全部重掃（預覽）
python inject_links.py --rescan                           # 全部重掃（正式）
```

連結策略：
- 每個概念每個 section 只連結**首次出現**
- 跳過 frontmatter、code blocks、已有連結、圖片嵌入
- 中文：直接匹配；短英文（≤4 字）：加 word boundary；長英文：不分大小寫

**何時執行 `--rescan`**：
- 新增概念筆記後（create_stubs 或 QuickAdd）
- 每完成約 10 則筆記充實後

### quickadd-create-concept.js — 即時建 stub

Obsidian QuickAdd macro，閱讀論文時圈選文字即可建立概念筆記。

流程：圈選 → `Ctrl+Shift+N` → 選領域 → 自動建 stub + 開啟 + 加入佇列

特殊處理：
- `光合作用(Photosynthesis)` → 標題=光合作用, alias=Photosynthesis
- 非法檔名字元（`:*?"<>|`）替換為全形
- 佇列：`OV-Papers/enrich-inbox.md`

---

## 調整後的腳本

### prepare_enrich_tasks.py — 批量任務檔

**2026-03-12 調整**：配合「批量打底 + 問題驅動深化」策略，目標從 rich 降為 basic。

主要變更：
- 任務檔標題標示「basic 等級」
- 指令簡化：不要求寫「應用」和「待解決問題」
- 風格範例從 80 行縮短至 30 行
- 論文摘錄從 800 字縮短至 400 字
- 每篇筆記預設來源論文從 5 篇降為 3 篇

```bash
python prepare_enrich_tasks.py                           # 全部 thin notes
python prepare_enrich_tasks.py --physio-only             # 植物生理優先
python prepare_enrich_tasks.py --domain OV-Bioinformatics --batch-size 10
python prepare_enrich_tasks.py --note "水分逆境"          # 單一筆記
```

關鍵設定：
- `THIN_THRESHOLD = 10`：< 10 行內容的筆記被標為 thin
- `--batch-size`：預設 10 篇/批
- `--max-papers`：預設 3 篇/筆記

---

## 保留但低頻的腳本

### extract_candidates.py — 概念候選挖掘

從論文中挖掘尚未建立筆記的概念。三個來源按信度排序：
1. YAML keywords（1.5x 加權）
2. Bold terms（需通過特異性過濾）
3. Final-md 中的紅色連結（1.3x 加權）

```bash
python extract_candidates.py                 # 全部
python extract_candidates.py --keywords-only # 只看 YAML keywords
```

輸出 `candidates_review.md`，人工勾選 `[x]` 後由 `create_stubs.py` 建立 stub。

> 使用頻率降低原因：問題驅動模式中，缺口會在提問時自然浮現並即時補上。此腳本適合偶爾做一次「全面掃描」。

### create_stubs.py — 批量建 stub

讀取 `candidates_review.md` 中勾選的項目，批量建立 stub 筆記。

```bash
python create_stubs.py --dry-run  # 預覽
python create_stubs.py            # 正式建立
```

> QuickAdd macro 已覆蓋多數即時建 stub 的需求，此腳本保留做大批量使用。

### extract_figures.py + insert_figures.py — 圖表處理

從 PDF 提取圖表並嵌入論文 markdown。`/onboard-paper` skill 中已整合呼叫。

```bash
python extract_figures.py --paper-id briggs1920quantitative
python insert_figures.py --paper-id briggs1920quantitative
```

依賴：PyMuPDF (`fitz`), Pillow (`PIL`)

### status_tracker.py — PDF 進度追蹤

解析/更新 `PDF_status.md` 的處理進度表。

```bash
python status_tracker.py --add-cols  # 新增追蹤欄位
```

---

## 兩種建設路徑與腳本的關係

```
批量路徑（Pipeline — 打底）
  extract_candidates.py → create_stubs.py → prepare_enrich_tasks.py → Claude Code 充實至 basic
                                                                        ↓
                                                              inject_links.py --rescan

問題驅動路徑（Collaboration — 深化）
  quickadd-create-concept.js → enrich-inbox.md → /process-inbox 或自然提問
                                                    ↓
                                         Claude 搜尋 concept_index → 回答 → 發現缺口 → 補強至 rich
```

批量路徑提供廣度覆蓋（讓概念可被搜到），問題驅動路徑提供深度驗證（讓知識經過討論確認）。

---

## 外部工具

### zotero-ai-agent — Zotero 文獻庫管理

位於 vault 根目錄 `zotero-ai-agent/`，獨立 Git repo。透過 Zotero API 查詢和管理文獻庫。

**與知識庫的關係**：Claude Code 在充實筆記或回答問題時，可用此工具查詢論文 metadata 以補充上下文。

**常用查詢**：
```bash
python zotero-ai-agent/zotero_agent.py items search "<query>"
python zotero-ai-agent/zotero_agent.py items get <key>
python zotero-ai-agent/zotero_agent.py col tree
```

**CLI 已知限制**：
- `items search ""` 預設只回傳 100 筆，需用 pyzotero 分頁取得完整資料
- `col tree` 顯示的 item count 全為 0（顯示 bug）
- Windows 需加 `PYTHONIOENCODING=utf-8`
- 完整查詢方法見 CLAUDE.md 的 Zotero AI Agent 段落

**文獻庫統計 (2026-03-19)**：272 篇文獻，Vault 論文筆記 182 篇（落差 90 篇）

**依賴**：pyzotero, python-dotenv, Claude CLI（AI 功能）

詳見 `zotero-ai-agent/README.md`。
