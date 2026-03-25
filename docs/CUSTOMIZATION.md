# 領域自訂指南

## 修改 vault_config.yaml

`vault_config.yaml` 是框架的單一配置檔。所有腳本和 AI 行為都從這裡讀取設定。

### 新增領域

```yaml
domains:
  NewDomain:
    description: "新領域描述"
    keywords:
      - "keyword1"
      - "keyword2"
```

新增後：
1. 手動建立 `OV-NewDomain/Map/`、`OV-NewDomain/Note/`、`OV-NewDomain/Pic/`
2. 建立 `OV-NewDomain/Map/NewDomain_MOC.md`
3. 更新 `Home.md` 加入新 MOC 連結

### 調整過濾清單

```yaml
filtering:
  # 不該成為概念筆記的泛用詞
  generic_blocklist:
    - "新增的泛用詞"

  # 知識缺口領域的關鍵字（1.5x 加權）
  boost_patterns:
    - "新增的 boost 關鍵字"

  # 不該作為概念別名的英文詞
  alias_blocklist:
    - "new generic word"
```

### 調整連結注入範圍

```yaml
link_injection:
  # 只掃論文
  scan_dirs: ["OV-Papers/PDF-md"]

  # 掃論文和概念筆記
  scan_dirs: ["OV-Papers/PDF-md", "OV-Biology/Note", "OV-CS/Note"]

  # 掃所有 .md 檔案
  scan_dirs: "all"
```

### 啟用可選模組

```yaml
modules:
  zotero: true          # 需要 pyzotero + .env 配置
  paper_pipeline: true  # 需要 pymupdf + pillow
```

## 修改 AI 行為

### CLAUDE.md

直接編輯 `CLAUDE.md` 可以改變 AI 的核心行為。常見調整：
- 新增情境路由規則
- 調整 Session Protocol 的自動行為
- 修改筆記充實度標準

### Skills

每個 skill 在 `.claude/skills/{name}/SKILL.md`。可以：
- 修改現有 skill 的步驟
- 新增自訂 skill

## 多語言

`vault_config.yaml` 的 `language` 欄位影響：
- 論文模板的 section markers（中文 emoji vs 英文標題）
- figures_section 名稱

筆記內容語言由使用者自行決定，不受配置限制。
