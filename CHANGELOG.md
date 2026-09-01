# Changelog

## 2.3.0 - 2026-09-01

### Changed

- **`triggers` 改為封閉詞彙**（breaking）：22 個詞登記在 `conventions/registry.md` 的〈Trigger vocabulary〉表，validator 拒絕表外的值。理由是實測——上游 vault 的 51 則規約用了 **162 個相異 trigger，其中 151 個只用過一次（93%）**。只用過一次的詞永遠篩不出第二則，於是這個欄位看起來像索引，實際上撈不出東西。詞彙表與編號表放同一個檔，因為兩者是同一種東西：一開放就失去篩選能力的命名空間。
- **新增開放欄位 `keywords`**：舊的具體用語（`impact-factor`、`cssclasses`、`gitignore-edit`）移到這裡，明文不作篩選用。散落的詞不必刪，它們只是被放錯位置——留著仍可全文搜尋，累積到足夠才升格為新的 trigger。
- **移除 `scope` 必填**：51 則規約有 51 個相異 `scope` 值、75% 只用過一次，還有單複數分裂；它與 `triggers` 重疊但品質更差，`triggers` 封閉後沒有留下的理由。
- 產生的 Convention MOC 的〈Working with these rules〉改為以 trigger 起手：先按手上的任務撈規約，再沿著規約之間的連結走。

### Tests

- 19 → 22：詞彙表逐項解析且無重複、樹內每個 trigger 都在表內、三種表外值（自創、封閉前的舊值、拼錯）都被擋下、`scope` 已從所有規約移除。

## 2.2.0 - 2026-09-01

### Changed

- **編號登記表從 YAML 改為 Markdown 表格**（breaking）：`conventions/registry.yaml` → `conventions/registry.md`，產生的 vault 同步改為 `KnowledgeBase/Convention/registry.md`。理由是這份資料是零巢狀平表，YAML 的巢狀與載入期型別檢查都沒用到；改成表格後它在自己治理的 vault 裡讀得到，規約名稱還能當 wikilink 進反向連結與 graph。表格本身即權威，庫裡仍然只有一份。
- registry 不再靠檔名尋找，改用 frontmatter `type: registry`。編號讓規約脫離檔名，登記表沒有理由反過來綁死在檔名上——vault 端與 repo 端也因此可以各自取名。
- `--strict-registry` 新增**連結檢查**：規約名稱加了 `[[ ]]` 卻沒有對應筆記、有筆記卻沒加連結、連結指到別的檔案，三種都失敗。沒有這道檢查，中括號就會變成一份要靠人記得更新的「這則筆記存在嗎」複本。
- `write_registry()` 在降級 `shipped` → `reserved` 的同時移除該列連結，並改為只重寫受影響的列，保留表格上方解釋編號體系的正文。
- 產生的 Convention MOC 改寫〈Rule numbering〉並新增〈Working with these rules〉：規約要讀原文而非只看 MOC 清單、以 `rule_id` 而非標題引用、新增規約必須「筆記與登記列同一次改動」、改完要跑 validator 並回報結果。
- 文件中的驗證指令不再寫死執行環境，改為說明唯一依賴是 PyYAML；`ModuleNotFoundError: No module named 'yaml'` 是直譯器選錯，不是規約庫壞了。

### Removed

- `validate_conventions.py --list` 與 `render_table()`。它們存在的理由是「可讀視圖即時產生、不存第二份」，權威改成 Markdown 後這個理由消失，留著反而會變成真正的第二份。

### Tests

- 迴歸測試 15 → 19：新增 registry 逐列解析、registry 不被當成 Convention 驗證、六種畸形列（缺欄、重複編號、未知 status、編號格式錯、一列兩個連結、整張表不見）、三種連結漂移，以及產生的 vault 必須保留表格正文。

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
