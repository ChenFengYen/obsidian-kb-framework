# Pipeline 操作指南

本文件記錄知識庫自動化建設的完整操作流程，從 CLAUDE.md v2.0 起獨立維護。

---

## 核心架構

使用者沒有 Anthropic API key，因此採用「腳本準備上下文 + Claude Code 手動執行」的模式。

```
prepare_enrich_tasks.py → 任務檔 (markdown) → Claude Code 讀取並執行 → 人工審核
```

---

## 腳本清單（OV-Papers/scripts/）

| 腳本 | 功能 | 階段 |
|:--|:--|:--|
| config.py | 路徑、DOMAIN_MAP、section markers | 基礎 |
| concept_index.py | 264 筆記、~1400 匹配詞、快取至 concept_index.json | 基礎 |
| status_tracker.py | 解析/更新 PDF_status.md | 基礎 |
| extract_figures.py | PyMuPDF 圖表提取、xref 去重、重複尺寸過濾 | Phase 1 |
| insert_figures.py | 插入 ![[fig]] 至圖表整理 section | Phase 1 |
| inject_links.py | 首次出現連結注入、跳過 frontmatter/基本資訊 | Phase 2 |
| extract_candidates.py | 3 區段：physio/keywords/bold、泛用詞黑名單 | Phase 3 |
| create_stubs.py | 依 candidates_review.md 中的 [x] 建立 stub | Phase 4 |
| prepare_enrich_tasks.py | 產生任務檔供 Claude Code 充實薄弱筆記 | Phase 5 |
| quickadd-create-concept.js | Obsidian QuickAdd macro：圈選→建 stub→加佇列 | 即時 |

---

## Phase 5：筆記充實工作流程

### 產生任務檔

```bash
cd OV-Papers/scripts

# 全部薄弱筆記
python prepare_enrich_tasks.py

# 只處理植物生理
python prepare_enrich_tasks.py --physio-only

# 指定領域
python prepare_enrich_tasks.py --domain OV-Bioinformatics

# 單一筆記
python prepare_enrich_tasks.py --note "光合作用"

# 控制批量大小
python prepare_enrich_tasks.py --batch-size 5
```

任務檔輸出至 `OV-Papers/enrich-tasks/`。

### Claude Code 執行

在 Claude Code 中使用自訂指令：
- `/enrich <任務檔名>` — 讀取任務檔並逐一充實筆記
- `/pipeline-status` — 檢查目前各階段進度

或手動指示：
> 請讀取 OV-Papers/enrich-tasks/enrich_batch_physio_batch01_20260310.md 並逐一充實其中的筆記。

### 人工審核

AI 充實的筆記會標記 `<!-- AI-ENRICHED - NEEDS REVIEW -->`。

審核流程：
1. 在 Obsidian 中搜尋 `AI-ENRICHED`
2. 對照來源論文確認事實正確性
3. 審核通過後移除標記
4. 可更新 `prepare_enrich_tasks.py` 中的 `STYLE_REFERENCE_NOTE` 指向最新審核通過的筆記

---

## 最佳實踐

- **批量大小**：每批 5-10 篇筆記（目標降為 basic，可處理更多）
- **目標深度**：basic 等級（10-15 行）——一句定義 + 核心要點 + 連結，不追求 rich。深度留給問題驅動路徑
- **優先順序**：植物生理優先（使用者知識缺口最大的領域）
- **風格一致性**：任務檔自動嵌入高品質筆記範例（預設 QTL.md）作為風格參考
- **來源閱讀**：至少瀏覽來源論文的相關段落，確保定義正確

---

## 已知問題與解法

| 問題 | 解法 |
|:--|:--|
| Chinese regex `\b` 不支援 CJK | 非 ASCII 詞直接匹配，不加 `\b` |
| Bold terms 過於嘈雜 | 特異性過濾 + 黑名單 |
| PDF 重複裝飾圖片 | xref 去重 + 尺寸頻率過濾 |
| Status tracker 排序失敗 | 使用 `key=lambda` 搭配 tuple |
| YAML importance 值型別不一致 | `try/except int()` |
| English alias 太短產生誤匹配 | MIN_ALIAS_LEN = 12 chars |

---

## 概念索引過濾規則

- STEM_BLOCKLIST: uv, id, ip, os, io
- ALIAS_BLOCKLIST: ~60 泛用英文詞（database, function, model 等）
- MIN_ALIAS_LEN: 12 chars（英文 alias 必須夠具體）
- 從 YAML keywords 提取（高信度）
- 從括號英文、粗體詞提取（需過濾）
- Max alias length: 50 chars，排除含 `。` `，` 的句子

---

## 論文入庫流程

新論文加入知識庫時，使用 `/onboard-paper {paper-id}` 自訂指令，自動執行：

1. **概念連結注入**：`inject_links.py --paper-id {id}` — 掃描論文，自動連結已有的概念筆記
2. **圖表提取**：`extract_figures.py` + `insert_figures.py`
3. **新概念發現**：`extract_candidates.py` — 找出尚未建立筆記的重要術語

### 反向更新：新增概念筆記後更新舊論文

當新增概念筆記（如透過 `create_stubs.py` 或手動建立）後，舊論文中的同名術語不會自動被連結。
使用 `--rescan` 模式重新掃描所有論文：

```bash
cd OV-Papers/scripts
python concept_index.py --force    # 重建索引（包含新概念）
python inject_links.py --rescan --dry-run   # 預覽新連結
python inject_links.py --rescan             # 正式注入
```

建議在以下時機執行 `--rescan`：
- 完成一批 `create_stubs.py` 建立新概念筆記後
- 手動建立多個概念筆記後
- 每完成 10 則筆記充實後（因為充實過程可能產生新的概念筆記）

---

## Obsidian QuickAdd 整合（即時概念筆記建立）

解決「閱讀論文時發現術語，不知道是否已有筆記」的問題。

### 架構

```
圈選文字 → Ctrl+Shift+N → 選領域 → 建 stub + 自動開啟 + 加入佇列
                                                    ↓
              Claude Code /process-inbox → 批次充實佇列中的 stub 筆記
```

### 組件

| 組件 | 路徑 | 功能 |
|:--|:--|:--|
| QuickAdd 外掛 | `.obsidian/plugins/quickadd/` | Obsidian 自動化框架 |
| Macro 腳本 | `OV-Papers/scripts/quickadd-create-concept.js` | 建 stub + 選領域 + 加佇列 |
| 佇列檔 | `OV-Papers/enrich-inbox.md` | 待充實的概念筆記清單 |
| Claude Skill | `.claude/skills/process-inbox/SKILL.md` | 讀取佇列並充實筆記 |

### Macro 行為

1. 取得編輯器中的圈選文字作為概念名稱
2. 檢查該概念筆記是否已存在（若存在則只插入連結）
3. 彈出領域選擇器（OV-Bioinformatics, OV-MachineLearning 等）
4. 在 `{domain}/Note/{conceptName}.md` 建立 stub 筆記（含 YAML + 模板）
5. 將原文中的圈選文字替換為 `[[conceptName]]`
6. 在 `OV-Papers/enrich-inbox.md` 記錄請求（含來源論文與上下文）
7. 自動在新分頁開啟建立的 stub 筆記

### 使用者端設定（一次性）

需在 Obsidian QuickAdd 設定中完成 Macro 註冊（已完成 ✓）：
1. Settings → Community plugins → QuickAdd ⚙️ → 輸入 `Create Concept Note`，選 Macro，Add Choice
2. 點擊 Macro 旁的 ⚙️ 齒輪 → 進入 Macro Builder → 新增 **User Script** command → 從列表選 `quickadd-create-concept`（腳本在 `OV-Papers/scripts/`，QuickAdd 會自動掃描 vault 中非隱藏資料夾的 .js 檔）
3. 回主設定頁，打開 ⚡ Command 圖示（加入命令面板）
4. Settings → Hotkeys → 搜尋 `QuickAdd: Create Concept Note` → 綁定 `Ctrl+Shift+N`

### 日常使用流程

1. **閱讀論文時**：圈選不熟悉的術語 → `Ctrl+Shift+N` → 選領域 → QuickAdd 自動建 stub、開啟新筆記、加入充實佇列
2. **累積數個概念後**：在 Claude Code 中說「**充實佇列**」或「**process inbox**」→ Claude 讀取佇列並逐一充實所有 pending 的 stub 筆記
3. **充實完成後**：人工審核標記了 `AI-ENRICHED` 的筆記 → 執行 `inject_links.py --rescan` 讓其他論文自動連結到新概念

> **注意**：圈選文字後直接按快捷鍵，不要先右鍵建連結（否則選取範圍會被消耗）。

---

## 兩種知識庫建設路徑

Pipeline 是知識庫建設的兩條路徑之一。另一條是「問題驅動協作」——使用者提問驅動的精準補強。

| | 批量路徑 (Pipeline) | 問題驅動路徑 (Collaboration) |
|:--|:--|:--|
| 驅動力 | 腳本掃描 thin notes | 使用者提問 |
| 目標等級 | **basic（10-15 行）** — 可搜尋、可引用 | **rich（≥30 行）** — 完整、經驗證 |
| 適合階段 | 初期打底，快速覆蓋 | 長期深化，精準補強 |
| Human-in-the-loop | 事後審核（QA 閘門） | 即時協作（共創） |
| 筆記標記 | `AI-ENRICHED` | `CO-CREATED`（或無標記，因已即時確認） |

**問題驅動路徑的典型流程**：

1. 使用者提出研究問題或概念釐清請求
2. Claude 搜尋知識庫中的概念筆記與論文，綜合回答並引用連結
3. 根據結果分流：知識庫足夠（無動作）、有缺口（提議新筆記）、有錯誤（提議修正）
4. 使用者確認後寫入——每次修改都經過即時討論驗證

兩條路徑互補：Pipeline 提供廣度覆蓋，問題驅動提供深度驗證。詳見 CLAUDE.md「問題驅動協作模式」區段。

---

## 策略的優勢與限制

**優勢：**
- 不需要 API key，利用 Claude Code 本身作為 AI agent
- 腳本自動收集論文上下文
- 批量可控，人工審核有標記可追溯

**限制：**
- 每批需手動下指令，無法全自動排程
- Context window 有上限，一次不宜處理太多
- 不同批次可能風格不一致
- 無法自動驗證學術事實正確性

---

## 連結哲學與 MOC 建設指南

### 連結原則（2026-03-11 確立）

**自動連結（inject_links.py）的定位**：每篇論文中每個概念只連結首次出現，作為基礎可發現性。不需要全文每處都連結——過度連結會造成視覺噪音，降低真正重要連結的辨識度。

**手動連結的價值**：概念筆記中的「相關筆記」區段，以及 MOC 中的敘述性連結，才是 LYT 中真正有思考價值的連結——它們反映的是你理解後的判斷，而非關鍵字匹配。

### MOC 不是什麼

- **不是連結清單**：只列 `[[A]] [[B]] [[C]]` 沒有組織價值
- **不是資料夾索引**：MOC 不等於把某資料夾下的筆記全部列出
- **不是自動生成物**：MOC 的價值來自作者的思考和組織

### MOC 是什麼

MOC 是你對一個知識領域的**思考地圖**，回答：「我對這個領域的理解是什麼？這些知識之間的關係是什麼？」

好的 MOC 包含：
1. **開頭敘述**：用自己的話說明這個領域的全景和你的研究視角
2. **主題分組**：按概念邏輯（不是按字母或建立日期）組織筆記連結
3. **跨概念關係**：說明 A 和 B 為什麼放在一起、它們的關係是什麼
4. **你的切入點**：從你的研究角度，這個知識群最重要的是什麼
5. **待釐清問題**：引導未來思考的開放問題

### 庫中現有範例評估

| Map 筆記 | 評估 | 原因 |
|:--|:--|:--|
| 植物表型分析 MOC.md | ✅ 完成 | 155 行，七大區段，敘述性連結+研究視角+待釐清問題，符合 MOC 設計標準 |
| 育種.md | ✅ 接近 MOC | 有邏輯結構、比較表格、自己的組織 |
| YOLO.md | ⚠️ 工作流索引 | 有用但只是步驟列表，缺乏跨概念組織 |
| 植物生理學.md | ✅ 完成 | 183 行，八大區段（碳同化→水分→營養→發育→逆境→影像橋樑→論文→問題），從表型分析視角組織生理知識 |
| AI方法_MOC.md | ✅ 完成 | ~250 行，十大區段（學習範式→最佳化→損失→網路元件→Transformer→視覺任務→評估→數據策略→論文→問題），從表型管線視角組織 99 個 ML 概念 |
| 2D性狀整理.md | ⚠️ 資料表格 | 有參考價值但不是 MOC |
| 植物形態學.md | ⚠️ 術語參考 | 146 行的分類學整理，但無 wiki 連結 |

### 建議優先建立的 MOC（按重要性排序）

1. ~~**植物表型分析 MOC**~~ ✅ 已完成（155 行，OV-Pheno/Map/植物表型分析 MOC.md）
2. ~~**植物生理學 MOC**~~ ✅ 已完成（183 行，OV-Bioinformatics/Map/植物生理學.md）
3. ~~**AI 方法 MOC**~~ ✅ 已完成（~250 行，OV-MachineLearning/Map/AI方法_MOC.md）
4. **論文 MOC** — 按研究主題而非 citekey 組織論文，形成文獻綜述的基礎

---

## 跨機器同步

知識庫在兩台機器上運作，透過 Git 雙向自動同步（5 分鐘間隔）。

### 架構

| 機器 | 同步方式 | 間隔 |
|:--|:--|:--|
| Obsidian 主力機 | obsidian-git plugin（auto commit + pull + push） | 5 min |
| 開發機 | `vault-sync.sh` + Task Scheduler "VaultSync" | 5 min |

### 開發機同步檔案

| 檔案 | 功能 |
|:--|:--|
| `vault-sync.sh` | pull --rebase → fallback merge → commit + push |
| `vault-sync.vbs` | VBS wrapper，讓 bash 靜默執行（無彈窗） |
| `.vault-sync.log` | 同步日誌（gitignored） |
| `.vault-sync.lock` | 防止重複執行（gitignored） |

### Obsidian 機器設定（obsidian-git plugin）

| 設定項 | 值 |
|:--|:--|
| Auto commit interval | 5 min |
| Auto pull interval | 5 min |
| Auto push interval | 5 min |
| Pull on startup | enabled |
| Pull before push | enabled |

### 衝突處理

| 情境 | 處理 |
|:--|:--|
| 不同檔案 | Git 自動合併 |
| 同檔案不同段落 | Git auto-merge |
| 同檔案同段落 | Merge conflict — 手動解決（極少發生） |
| rebase 失敗 | 自動 fallback 到 merge |

### 操作紀律

- Claude Code 跑 pipeline 時，避免在 Obsidian 端編輯同一批筆記
- 切換機器前，確認上一台已 push（或等 5 分鐘）

### Task Scheduler 管理（PowerShell）

```powershell
Get-ScheduledTask -TaskName "VaultSync"        # 查看狀態
Disable-ScheduledTask -TaskName "VaultSync"    # 暫停
Enable-ScheduledTask -TaskName "VaultSync"     # 恢復
Unregister-ScheduledTask -TaskName "VaultSync" # 刪除
```

---

最後更新：2026-03-13 (v2.7: 新增跨機器同步段落)
