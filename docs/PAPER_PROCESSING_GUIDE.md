
# 論文 Markdown 圖表提取與嵌入指南

本指南定義了從 PDF 原始論文提取圖表並嵌入至結構化論文 Markdown 的標準流程。

--------------------------------

## 檔案路徑規範

| 用途 | 路徑 |
|---|---|
| 原始 PDF | `OV-Papers/PDF-raw/{paperID}.pdf` |
| 草稿 Markdown | `OV-Papers/PDF-md/{paperID}.md` |
| 完成 Markdown | `OV-Papers/Final-md/{paperID}.md` |
| 提取圖片 | `OV-Papers/PDF-assets/{paperID}_fig{N}.png` |

命名慣例：`{第一作者姓氏}{年份}{標題關鍵字}`，與 PDF-md 檔名一致。

--------------------------------

## 圖片篩選規則

### 保留

- 寬度 >= 500px 的圖片（論文正式圖表）
- Graphical Abstract（通常在前 1-2 頁，尺寸 > 800px）

### 跳過

- 寬度 < 500px 的圖片（期刊 logo、ORCID 圖示、QR code）
- 最後 2 頁中寬高比接近 1:1 且尺寸 < 500px 的圖片（作者大頭照）

--------------------------------

## 圖片嵌入位置

依圖片在論文中的功能，分配至 Markdown 對應章節：

| 圖片類型 | 嵌入位置 |
|---|---|
| Graphical Abstract | 🧾 基本資訊 之後 |
| 方法類（實驗裝置、流程圖、儀器照片） | 🔬 研究方法 Methods |
| 結果類（數據圖表、比較表、統計圖） | 📊 結果 Results > 圖表整理 |
| 討論類（機制示意圖、概念模型） | 🧠 討論 Discussion |

### 嵌入格式

```markdown
![[{paperID}_fig{N}.png|500]]
- **圖 {N}**：圖片說明文字。
```

--------------------------------

## 文字型表格處理

當表格在 PDF 中以文字渲染（非嵌入式圖片），無法自動提取。插入以下佔位符：

```markdown
> [!warning] 📋 表格需人工檢查
> **表 {N}**：{表格標題/描述}
> 此表格在 PDF 中為文字渲染，請使用 PDF++ 從原始 PDF 截取。
> 來源：OV-Papers/PDF-raw/{paperID}.pdf，第 {X} 頁
```

--------------------------------

## 圖片編號注意事項

- PDF 嵌入順序可能與論文圖片編號不一致（同一頁多張圖的嵌入順序不可控）
- 提取後必須目視檢查，確認圖片內容與論文圖號的對應關係
- 需人工審核圖片放置的章節是否正確

--------------------------------

## 處理流程

1. 使用 PyMuPDF 掃描 PDF 所有頁面，提取符合篩選規則的嵌入式圖片
2. 目視驗證每張圖片內容，建立圖片與論文圖號的對應
3. 依圖片功能將 `![[]]` 引用插入 Markdown 對應章節
4. 對文字型表格插入佔位符提醒人工截取
5. 最終由人工審核確認所有圖表位置與編號正確

--------------------------------

## 工具依賴

- **Python 3.11+**
- **PyMuPDF (fitz)**：PDF 圖片提取（`pip install pymupdf`）
- **Pillow**：圖片格式轉換，統一輸出 PNG（`pip install pillow`）
- **PDF++ (Obsidian 外掛)**：人工截取文字型表格或需精確裁切的子區域

--------------------------------

## Python 提取腳本

### 步驟一：掃描 PDF 中的嵌入式圖片資訊

用於預覽 PDF 中所有圖片的頁碼、尺寸與格式，決定哪些應該提取。

```python
import fitz

PAPER_ID = "abdelhakim2021effect"  # 替換為目標論文 ID
PDF_PATH = f"C:/Users/ChenFengYen/ObsidianWork/OV-Papers/PDF-raw/{PAPER_ID}.pdf"

doc = fitz.open(PDF_PATH)
total_pages = len(doc)
print(f"Pages: {total_pages}")

for i, page in enumerate(doc):
    images = page.get_images(full=True)
    if not images:
        continue
    print(f"Page {i+1}: {len(images)} images")
    for j, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        w, h = base_image["width"], base_image["height"]
        ext = base_image["ext"]
        aspect = w / h if h > 0 else 0

        # 標記篩選結果
        is_last_pages = (i >= total_pages - 2)
        is_small = (w < 500)
        is_portrait = (is_small and 0.7 < aspect < 1.4 and is_last_pages)
        skip_reason = ""
        if is_portrait:
            skip_reason = " [SKIP: author portrait]"
        elif is_small:
            skip_reason = " [SKIP: too small]"

        print(f"  Image {j+1}: xref={xref}, {w}x{h}, {ext}, aspect={aspect:.2f}{skip_reason}")

doc.close()
```

### 步驟二：提取圖片並儲存至 PDF-assets

根據步驟一的掃描結果，提取所有符合條件的圖片。

```python
import fitz
from PIL import Image
import io
import os

PAPER_ID = "abdelhakim2021effect"  # 替換為目標論文 ID
PDF_PATH = f"C:/Users/ChenFengYen/ObsidianWork/OV-Papers/PDF-raw/{PAPER_ID}.pdf"
OUTPUT_DIR = "C:/Users/ChenFengYen/ObsidianWork/OV-Papers/PDF-assets"

doc = fitz.open(PDF_PATH)
total_pages = len(doc)
fig_num = 0

for i, page in enumerate(doc):
    images = page.get_images(full=True)
    for j, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        w, h = base_image["width"], base_image["height"]

        # 篩選：跳過小圖片
        if w < 500:
            continue

        # 篩選：跳過最後 2 頁的作者大頭照（接近正方形的小圖）
        is_last_pages = (i >= total_pages - 2)
        aspect = w / h if h > 0 else 0
        if is_last_pages and w < 500 and 0.7 < aspect < 1.4:
            continue

        fig_num += 1
        img_data = base_image["image"]

        # 轉換為 PNG 並儲存
        pil_img = Image.open(io.BytesIO(img_data))
        filename = f"{PAPER_ID}_fig{fig_num}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        pil_img.save(filepath, "PNG")
        print(f"Extracted: {filename} from page {i+1} ({w}x{h})")

doc.close()
print(f"\nTotal extracted: {fig_num} figures")
```

### 步驟三：目視驗證與重新編號

提取完成後，需逐一檢視圖片內容，確認與論文圖號的對應。
若 PDF 嵌入順序與論文圖號不一致（如同一頁多張圖），需手動重新命名。

```python
import os

OUTPUT_DIR = "C:/Users/ChenFengYen/ObsidianWork/OV-Papers/PDF-assets"
PAPER_ID = "abdelhakim2021effect"  # 替換為目標論文 ID

# 範例：當提取的 fig1 實際對應論文 Fig 2，fig2 對應 Fig 1 時
# 使用三步交換避免覆蓋
swap_pairs = [
    ("fig1", "fig2"),  # 依實際情況修改
]

for a, b in swap_pairs:
    path_a = os.path.join(OUTPUT_DIR, f"{PAPER_ID}_{a}.png")
    path_b = os.path.join(OUTPUT_DIR, f"{PAPER_ID}_{b}.png")
    path_tmp = os.path.join(OUTPUT_DIR, f"{PAPER_ID}_tmp_swap.png")

    os.rename(path_a, path_tmp)
    os.rename(path_b, path_a)
    os.rename(path_tmp, path_b)
    print(f"Swapped: {a} <-> {b}")
```

### 步驟四：在 Markdown 中插入圖片引用

確認編號正確後，在對應章節插入 Obsidian 圖片引用語法：

```markdown
![[{paperID}_fig1.png|500]]
- **圖 1**：說明文字...

![[{paperID}_fig2.png|500]]
- **圖 2**：說明文字...
```

對於無法提取的文字型表格，插入佔位符：

```markdown
> [!warning] 📋 表格需人工檢查
> **表 1**：{表格標題/描述}
> 此表格在 PDF 中為文字渲染，請使用 PDF++ 從原始 PDF 截取。
> 來源：OV-Papers/PDF-raw/{paperID}.pdf，第 {X} 頁
```

--------------------------------

## 批次處理管線（Batch Processing Pipeline）

`OV-Papers/scripts/` 提供自動化腳本，將上述手動流程擴展為批次處理。

### 腳本總覽

| 腳本 | 用途 | 指令範例 |
|---|---|---|
| `config.py` | 路徑常數與領域對映表 | （模組，不直接執行） |
| `concept_index.py` | 建立 264 則概念筆記的索引與別名對映 | `python concept_index.py --force` |
| `status_tracker.py` | 解析/更新 PDF_status.md 追蹤表 | `python status_tracker.py --add-cols` |
| `extract_figures.py` | 批次從 PDF 提取圖片 | `python extract_figures.py --batch-size 10` |
| `insert_figures.py` | 將 `![[fig]]` 嵌入插入 markdown | `python insert_figures.py` |
| `inject_links.py` | 注入 `[[概念]]` wiki-links | `python inject_links.py --batch-size 10` |
| `extract_candidates.py` | 找出缺少的概念候選 | `python extract_candidates.py --min-refs 2` |
| `create_stubs.py` | 建立人工審核通過的 stub 筆記 | `python create_stubs.py` |
| `prepare_enrich_tasks.py` | 產生 Claude Code 任務檔以充實薄弱筆記 | `python prepare_enrich_tasks.py --physio-only` |

### 標準批次處理流程

```bash
cd OV-Papers/scripts/

# Phase 1：圖表
python extract_figures.py --batch-size 10    # 提取圖片
python insert_figures.py                      # 插入圖片引用

# Phase 2：概念連結
python inject_links.py --batch-size 10        # 注入 [[概念]] 連結

# Phase 3：新概念發現
python extract_candidates.py --min-refs 2     # 產生候選清單
# → 手動在 candidates_review.md 中勾選 [x]
python create_stubs.py                         # 建立 stub 筆記

# Phase 4：AI 輔助知識充實
python prepare_enrich_tasks.py --physio-only --batch-size 5
# → 在 Claude Code 中讀取 enrich-tasks/ 下的任務檔並執行
```

### 安全機制

- 所有修改前自動備份至 `PDF-md/.backup/`
- 每個腳本支援 `--dry-run` 預覽模式
- AI 插入的圖表標記 `<!-- AUTO-INSERTED FIGURES - NEEDS HUMAN REVIEW -->`
- AI 充實的筆記標記 `<!-- AI-ENRICHED - NEEDS REVIEW -->`
- 概念 stub 建立需人工在 `candidates_review.md` 勾選後才執行

### 追蹤欄位

PDF_status.md 包含以下追蹤欄位：

| 欄位 | 說明 |
|---|---|
| `figures_extracted` | 圖片是否已提取 `[yes]/[no]` |
| `links_injected` | 概念連結是否已注入 `[yes]/[no]` |

### 產出檔案

| 檔案 | 說明 |
|---|---|
| `PDF-assets/{paperID}_figN.png` | 提取的圖片 |
| `scripts/concept_index.json` | 概念索引快取 |
| `candidates_review.md` | 候選概念清單（需人工審核） |
| `link_report.md` | 連結注入報告 |
| `review_queue.md` | 人工審核佇列 |
| `enrich-tasks/enrich_batch_*.md` | Claude Code 知識充實任務檔 |

--------------------------------

## AI 輔助知識充實策略

### 背景

知識庫中 264 則概念筆記，有 99 則內容薄弱（<10 行），包括完全空白的重要筆記
（如「光合作用」「Segment Anything Model」）。同時有 57 篇植物生理相關高品質論文
可作為知識來源。

### 方法：腳本準備上下文 + Claude Code 手動執行

由於沒有 Anthropic API key，採用以下架構：

```
prepare_enrich_tasks.py     Claude Code          人工審核
 ┌─────────────────┐      ┌────────────┐      ┌──────────┐
 │ 掃描薄弱筆記      │      │ 讀取任務檔   │      │ 確認內容   │
 │ 搜尋引用論文      │ ──→  │ 讀取來源論文  │ ──→  │ 移除標記   │
 │ 抽取相關段落      │      │ 合成知識     │      │ 更新 MOC  │
 │ 產生任務檔       │      │ 寫入筆記     │      │           │
 └─────────────────┘      └────────────┘      └──────────┘
     自動化                   半自動                手動
```

### 優勢

1. **不需要 API key**：Claude Code 本身就是 AI agent，無額外成本
2. **上下文品質高**：腳本預先收集論文段落，但 Claude Code 可進一步讀取完整論文
   檔案，理解深度遠超過僅靠摘錄
3. **多論文交叉合成**：同一概念可從多篇論文中萃取不同面向，比人工逐篇閱讀更有效率
4. **批量可控**：每批 5 篇，避免 context window 溢出，也方便逐批審核
5. **可追溯**：每個任務記錄來源論文路徑，AI 充實的筆記有標記，可追溯知識來源
6. **漸進式**：可按領域、按優先級逐步執行，不需一次處理全部

### 限制與緩解措施

| # | 限制 | 緩解措施 |
|---|---|---|
| 1 | **無法全自動排程**：每批需手動觸發 | 適合每天 2-3 批（10-15 則），不需一次處理全部 |
| 2 | **Context window 上限**：論文過長時早期內容被壓縮 | 每批 ≤ 5 篇筆記 |
| 3 | **風格一致性**：不同 session 風格可能不同 | ✅ 已解決：任務檔自動嵌入真實範例筆記（QTL.md）作為風格基準 |
| 4 | **學術正確性無法自動驗證** | 必須人工對照來源論文審核 |
| 5 | **論文摘錄品質**：關鍵字匹配可能抓到不夠相關的段落 | ✅ 已解決：任務檔 prompt 明確指示「閱讀完整論文，摘錄僅為定位參考」 |
| 6 | **無增量記憶**：每批獨立對話 | ✅ 已解決：更新 `STYLE_REFERENCE_NOTE` 指向最新審核通過的筆記 |

### 最佳實踐

- 每批 5 篇筆記，優先處理植物生理領域（`--physio-only`）
- 任務檔已內建「閱讀完整論文」的指示，Claude Code 會自動讀取論文全文
- 審核時對照來源論文確認事實正確性，特別是數值、機制描述、因果關係
- 完成審核後移除 `<!-- AI-ENRICHED - NEEDS REVIEW -->` 標記
- 每完成 10 則筆記後，重新執行 `inject_links.py` 更新論文中的概念連結
- **風格迭代**：審核首批筆記後，將最佳筆記設為風格範例
  （更新 `prepare_enrich_tasks.py` 中的 `STYLE_REFERENCE_NOTE` 路徑）
