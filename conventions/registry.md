---
type: registry
registry_version: 1
---

# Convention rule_id registry

Single source of truth for the `KB-*` namespace. Every Convention note, in this
repository or in any vault generated from it, must carry a `rule_id` listed
here. `validate_conventions.py` enforces both directions: an unlisted id fails,
and two notes claiming one id fail.

This table is the authority, not a rendering of one. The payload is a flat row
of scalars, so the nesting and schema checks a YAML file would buy are unused,
while a Markdown table is readable in the vault it governs and its rule names
are links that show up in backlinks and the graph.

A name in double brackets is the note that claims the id **in this tree**; plain
text means the id is registered but no note here claims it. The brackets are not
maintained by hand - `--strict-registry` compares them against the notes on disk
and fails when they disagree.

`status`:

- `shipped` - the Convention note lives in this repository, under `pack`.
- `reserved` - the id is taken by an upstream vault; the note has not been made
  portable yet. Reserved ids are recorded so a new Convention never silently
  reuses a number that already means something elsewhere.

Adding a rule: append a row, never renumber an existing entry. Ids are permanent
even after a note is superseded - see `KB-HISTORY-001`.

## Reserved prefixes

Prefixes owned by downstream vaults. Their contents are domain-specific and
deliberately absent here; this repository only reserves the namespace so generic
`KB-*` numbering can never collide with a domain rule.

| prefix | owner |
|---|---|
| `PHENO-` | downstream vault (plant phenotyping) |
| `ML-` | downstream vault (machine learning) |

## Rules

| rule_id | name | name_zh | status | pack | former_ids |
|---|---|---|---|---|---|
| `KB-ACCESS-001` | [[Fixed operation vocabulary for knowledge base access]] | 知識庫存取須用固定操作 | shipped | core | — |
| `KB-ASSET-001` | Image asset naming | 圖片命名規約 | reserved | — | — |
| `KB-AUTOMATION-001` | Segment LLM workflows under subscription limits | 訂閱模式LLM工作流分段 | reserved | — | — |
| `KB-CHANGE-001` | [[Approval before destructive or published changes]] | 變更提交前核准 | shipped | core | — |
| `KB-COLLAB-001` | [[Feasibility before implementation]] | 可行性問題與實作請求分流 | shipped | core | — |
| `KB-DATA-001` | [[Use structured parsers for structured data]] | CSV必須使用標準解析器 | shipped | core | — |
| `KB-DATA-002` | [[Version the analysis population]] | — | shipped | core | — |
| `KB-DATA-003` | [[Separate source and derived data]] | — | shipped | core | — |
| `KB-ENCODING-001` | [[Windows UTF-8 file safety]] | Windows UTF8輸出與中文檔案安全 | shipped | windows-zh-tw | — |
| `KB-EVIDENCE-001` | [[Do not invent facts or thresholds]] | 不捏造數值門檻 | shipped | core | — |
| `KB-EVIDENCE-002` | Literature search completeness | 文獻搜尋完整性 | reserved | — | — |
| `KB-EVIDENCE-003` | Multi-source verification for concept notes | 概念多源驗證 | reserved | — | — |
| `KB-EVIDENCE-004` | [[AI generated fields require verification]] | LLM生成內容的來源標註與引用界線 | shipped | core | `KB-AI-001` |
| `KB-EVIDENCE-005` | [[Match claim strength to evidence]] | — | shipped | research | `KB-RESEARCH-001` |
| `KB-EXPERIMENT-001` | [[Record experiment specifications]] | 乾實驗環境規格 | shipped | research | — |
| `KB-FRONTMATTER-001` | [[Frontmatter remains structured]] | Frontmatter清單格式 | shipped | obsidian | — |
| `KB-FRONTMATTER-002` | Frontmatter field semantics | Frontmatter欄位語意 | reserved | — | — |
| `KB-HISTORY-001` | [[Preserve note and convention history]] | 筆記與規約歷程保留 | shipped | core | — |
| `KB-LANG-001` | Traditional Chinese wording in notes | 繁體中文筆記用詞 | reserved | — | — |
| `KB-LANG-002` | Space around inline markers in CJK text | 中文粗體前後加半形空格 | reserved | — | — |
| `KB-LINK-001` | [[Obsidian link safety]] | Obsidian連結規約 | shipped | obsidian | — |
| `KB-MATH-001` | Math formula formatting | 數學公式格式 | reserved | — | — |
| `KB-METHOD-001` | Prefer simple justified methods | 簡單有依據的方法論優先 | reserved | — | — |
| `KB-OUTPUT-001` | [[Separate temporary work from durable knowledge]] | Vault工作產物與腳本分層 | shipped | core | — |
| `KB-PAPER-001` | PDF and YAML missing value handling | PDF與YAML缺值規約 | reserved | — | — |
| `KB-PAPER-002` | Supplementary material gets its own note | 論文補充材料獨立建檔 | reserved | — | — |
| `KB-PRECISION-001` | [[Make sources traceable]] | 學術引用與術語精確性 | shipped | research | `KB-RESEARCH-002` |
| `KB-STRUCT-001` | Vault directory and note type structure | Vault目錄與筆記型別規約 | reserved | — | — |
| `KB-TABLE-001` | Markdown tables and multi-image layout | Markdown表格與多圖排版 | reserved | — | — |
| `KB-TITLE-001` | Concept note titles | 概念筆記標題規約 | reserved | — | — |
| `KB-VCS-001` | [[Ignore rules must survive directory renames]] | 忽略規則與目錄改名 | shipped | core | — |
| `KB-VERIFY-001` | [[Confirm the measurement method before trusting numbers]] | 驗證數字前先確認量測方法 | shipped | core | — |
| `KB-VERIFY-002` | [[Counterbalance presentation order in paired comparison]] | 成對比較須抵銷呈現順序 | shipped | core | — |
| `KB-VERIFY-003` | Verification tools must not truncate by default | 驗證工具預設必須不省略 | reserved | — | — |
| `KB-VERIFY-004` | Prove an off-site copy exists, do not infer it from configuration | 離機副本要實測不看設定 | reserved | — | — |
| `KB-VERIFY-005` | A monitor's baseline must expire | 監測基準必須會過期 | reserved | — | — |
| `KB-VISUAL-001` | Sequential palette runs high red to low blue | 連續色盤使用高紅低藍 | reserved | — | — |
| `KB-VISUAL-002` | matplotlib CJK font rendering | matplotlib中文字型渲染 | reserved | — | — |
| `KB-VISUAL-003` | ASCII diagram alignment | ASCII示意圖對齊規約 | reserved | — | — |
| `KB-VOCAB-001` | Classification vocabularies must be closed | 分類詞彙必須封閉 | reserved | — | — |
| `KB-WRITING-001` | [[Notes teach, they do not log edits]] | 筆記不寫修改過程 | shipped | core | — |
| `KB-WRITING-002` | Choose a narrative mode before enriching a note | 豐富筆記先選敘事模式 | reserved | — | — |
| `KB-WRITING-003` | Callouts need an entry point in the body | callout須有正文入口 | reserved | — | — |

## Trigger vocabulary

`triggers` says **when a rule should come to mind** — the work in hand, not the
subject being thought about. The list is closed for the same reason the id
namespace is: a value invented for one rule can never be filtered for, so an
open list of triggers is a field that looks like an index and retrieves
nothing. `validate_conventions.py` rejects a trigger outside this table.

Adding a term is a deliberate change, not a side effect of writing a rule. A
term earns its place by covering several rules; one that covers a single rule
filters nothing, and one that covers most of them filters nothing either. When
a rule needs a value that is not here, record the specific words under
`keywords` — an open field, deliberately not a filter — and let them accumulate
until they justify a term.

| trigger | applies when |
|---|---|
| `analysis-run` | running an analysis, experiment, or model evaluation |
| `annotation` | labelling data or reviewing it object by object |
| `cjk-text` | writing CJK prose, or editing text with inline markers |
| `claim-writing` | writing a statement that carries evidential weight |
| `data-archive` | naming archived data or designing its keys |
| `data-classify` | designing a classification field, tag set, or vocabulary |
| `data-parse` | reading or writing structured data |
| `destructive-op` | deleting, batch-rewriting, or any irreversible edit |
| `figure-or-table` | a figure or a table: ASCII, embeds, layout, asset naming |
| `frontmatter` | editing YAML fields |
| `kb-access` | operating on the knowledge base itself |
| `literature-search` | searching outside the vault for sources |
| `note-create` | creating a note: naming it, titling it, placing it |
| `note-structure` | folders, moves, renames, MOCs |
| `note-write` | writing or revising note prose |
| `option-compare` | choosing between two or more candidates |
| `paper-ingestion` | bringing a paper into the vault as structured notes |
| `plotting` | producing a plot |
| `task-scoping` | deciding what kind of task this is, or designing automation |
| `verification` | producing a number that says the work is sound |
| `version-control` | commit, push, ignore rules, renames under version control |
| `wikilink` | editing links, including block links and link repair |
