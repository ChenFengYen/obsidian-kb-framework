# Changelog

## 2.1.0 - 2026-08-27

### Added

- `conventions/registry.yaml`：`KB-*` 編號的唯一權威表，含尚未移植但已被上游佔用的 `reserved` 編號，以及下游領域前綴宣告。
- `validate_conventions.py --registry`：未登記的 `rule_id` 與登記為 `shipped` 卻無對應筆記的編號都會失敗；下游領域前綴自動放行。
- 產生的 vault 會裝入反映實際安裝 pack 的 `registry.yaml`（未安裝 pack 的編號降為 `reserved`）。
- 產生的 `AGENTS.md` 新增〈Memory fallback〉〈Instruction precedence〉〈Startup self-check〉三節——讀不到 memory 的 agent 必須回報而不是假裝記得。
- `vault_health.py` 解析 frontmatter `aliases`，`[[別名]]` 不再被誤判為壞連結。
- `validate_conventions.py --list`：即時把 registry 印成 Markdown 表格，避免手工維護第二份編號表。
- 產生的 Convention MOC 新增〈Rule numbering〉一節，說明編號體系與 `shipped`／`reserved` 界線；貢獻者面的說明併入既有的 `docs/CUSTOMIZATION.md`，不另開文件。
- `prompts/AgentRules.md`，並讓 `install_adapters()` 實際讀取 `prompts/` 底下的 adapter 檔——原本三個 adapter 檔沒有任何程式會讀，產生的是一行 placeholder，`@AGENTS.md` import 與平台補充全部遺失。
- `--strict-registry`：反向檢查（每個 `shipped` 編號都要有筆記）改為選用，只在驗證 registry 所描述的那棵樹時開啟；驗證單一領域資料夾等子集時不再誤報。
- 迴歸測試 6 → 15：編號登記正/負向、子集不誤報、部分 pack 安裝、無前綴佈局、alias 連結解析、BOM 檔仍受檢、表格渲染、adapter 帶 `@AGENTS.md`。

### Fixed

- `validate_conventions.py` 改用 `utf-8-sig` 讀檔。原本帶 BOM 的規約檔會在 `---` 判斷失敗後被整檔跳過，**只回報一個解析錯誤而完全不驗欄位**——對上游 vault 的 49 則規約實測，20 則帶 BOM，等於五分之二從未被檢查過。

### Changed

- **Breaking**：新產生的領域資料夾不再帶 `OV-` 前綴（`OV-Pheno` → `Pheno`）。既有 vault 不受影響，升級方式見 docs/MIGRATION_V2.md。
- `config.OV_FOLDERS` 更名為 `DOMAIN_FOLDERS`（保留舊名別名）；無 YAML 設定時改以「頂層目錄含 `Map/` 或 `Note/`」判定領域，不再依賴名稱前綴。
- 三則規約改編號以對齊上游：`KB-AI-001` → `KB-EVIDENCE-004`、`KB-RESEARCH-001` → `KB-EVIDENCE-005`、`KB-RESEARCH-002` → `KB-PRECISION-001`。舊編號記在 registry 的 `former_ids`。

## 2.0.0 - 2026-07-02

### Changed

- 問題驅動協作成為唯一預設知識建設流程。
- 連結改為閱讀上下文後的人工／AI 語意判斷。
- 筆記品質改以問題、來源、邊界與連結性判斷，不再以行數作為擴寫目標。
- 健康報告預設寫入系統暫存目錄。
- 內建 skills 精簡為 init-domain、review-vault、suggest-next、debrief。

### Removed

- 自動連結注入與 concept index。
- 自動候選擷取、stub 建立與 QuickAdd stub 佇列。
- 批量 enrich 任務與相關 skills。

升級方式見 docs/MIGRATION_V2.md。
