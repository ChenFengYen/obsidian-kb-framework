# Scripts 參考

v2 只保留診斷、圖譜與附件治理工具。所有工具預設提供資訊或執行明確計畫，不自動建立知識關係。

## 核心工具

| Script | 用途 | 寫入行為 |
|:--|:--|:--|
| `vault_health.py` | richness、孤兒、壞連結、MOC 覆蓋 | 報告寫入系統暫存目錄 |
| `note_graph.py` | hub、bridge、cluster、跨領域缺口 | 報告或 JSON |
| `audit_images.py` | 圖片引用與孤立附件稽核 | 只產生報告 |
| `rename_images.py` | 依人工核准計畫重命名附件 | 會修改，先 dry-run |
| `config.py` | 共用 vault 路徑與模組設定 | 不寫入 |

## 常用命令

```bash
python OV-Papers/scripts/vault_health.py --summary
python OV-Papers/scripts/vault_health.py --broken-links
python OV-Papers/scripts/vault_health.py --orphans
python OV-Papers/scripts/note_graph.py
python OV-Papers/scripts/audit_images.py
```

## 可選論文工具

啟用 `paper_pipeline` 時，setup 會安裝：

- `extract_figures.py`
- `insert_figures.py`
- `status_tracker.py`

這些工具只處理 PDF、圖片與狀態，不注入概念連結。

## 已移除的 v1 工具

`concept_index.py`、`inject_links.py`、`extract_candidates.py`、`create_stubs.py`、`prepare_enrich_tasks.py` 與 QuickAdd stub macro 已移除。原因及升級方式見 `MIGRATION_V2.md`。
