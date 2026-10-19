# Changelog

## 2.7.0 - 2026-10-19

### Added

- **core 新增兩則規約**，由上游 vault 2026-09-02 的規約移植。兩則晚於 09-01 的移植盤點一天建立，第一梯因此沒有排到；這裡不是重新評估後才收進來。
  - **`KB-CHANGE-002` Enumerate every match before a batch replacement**（severity error）。替換的目標是一組列得完的已知字串，不是一個模式；長內容先寫成檔案再讓程式讀，不經 shell 傳遞。兩點不拆開，因為它們是同一次批次改寫裡的兩個靜默失效點。這則補上 `KB-CHANGE-001` 的空缺：該則要求批次變更前取得核准，這則說明核准的依據是命中清單。`OV-DETR` 案例與影響面數字原樣保留（上游 vault 移除九個資料夾前綴那次），只把「中文 replacement literal」改成泛指非 ASCII 字串。
  - **`KB-COLLAB-002` Present the argument outline before writing**（severity warning）。這則接在 `KB-COLLAB-001` 之後：後者決定要不要展開計畫，這則規定展開之後、動筆之前先交出論證大綱，而且編輯工具的確認框不算確認。大綱第 4 要素原本寫 wikilink，改成泛指連結。〈相關〉刪掉指向 `KB-WRITING-002` 的那條，因為它在 repo 仍是 reserved，比照 `KB-VERIFY-001` 的前例。
- **產生的 `AGENTS.md` 新增〈Before the first write〉**，由上游 vault〈動筆前必跑〉去在地化而來，共四步：讀本次任務的規約 → 交論證大綱並等待 → 查重複 → 寫入後跑 `vault_health.py --broken-links`、做 memory 連結掃描，並回報數字。涵蓋範圍明寫包含刪除、整檔覆寫、批次改連結，因為這三種通常走 shell，最容易繞過前面幾步。刪除或改名時，檢查要提前到動手之前。亂碼掃描只在啟用 `windows-zh-tw` pack 時才列出。**規約和這個區塊一起搬，原因是上游的經驗**：「先給大綱」單獨寫成規約時，是最常被漏掉的一條，掛到每次寫入都會經過的步驟上之後，漏跑才會留下痕跡。這個區塊的內容不依賴 core pack 是否安裝，規約編號只當延伸閱讀。

### Changed

- **`test_generated_vault_has_no_domain_prefix` 改成錨定完整字串。** 原本斷言整個產生的 vault 不含 `OV-` 子字串，而新規約的 `OV-DETR` 案例會讓它失敗——這個測試本身就是對前綴做通用比對，正是 `KB-CHANGE-002` 描述的那種錯誤。現在改查 `OV-` 加上每個網域資料夾名的完整字串；檔名前綴的檢查不變。

### Tests

- 40 則（39 → 40）：契約含〈Before the first write〉且指名 `KB-COLLAB-002`、所引用的 `tools/vault_health.py` 確實會被安裝、兩則規約都會進入產生的 vault、亂碼掃描只在 Windows pack 下出現。

## 2.6.0 - 2026-10-19

### Added

- **validator 第 5 道檢查：規約正文引用的編號必須在登記表裡。** 原本四道檢查只看每則規約 frontmatter 自己的 `rule_id`，正文裡用來互相指涉的編號沒有任何東西讀，所以引用一個從不存在的編號能通過全部檢查。上游 vault 實測：正文共 182 處引用（65 檔），真缺陷 1 處——`KB-WRITING-004` 引用 `KB-CLAIM-001`，實際是 `KB-PRECISION-001`；新檢查在那一行報錯，修正後歸零。判準：
  - **命名空間取自登記表**（已登記規則的前綴＋保留前綴），不寫死 `KB-`，因此 `UTF-8` 這類字串不會被誤認。
  - **只保留、未列舉的前綴不判**，與 `check_registry` 同一規則：那些編號列在本次執行看不到的地方。
  - **引用 `former_ids` 是 warning 不是 error**，訊息附上現行編號：讀者仍會落到對的規約，只是多繞一步。`validate()` 新增選用參數 `warnings`，不傳就丟棄，既有呼叫端看到的仍只有 errors；CLI 印成 `warning:` 行、不影響結束碼。
  - 只掃 `--root` 底下的規約，不掃全庫；`AGENTS.md`、MOC 裡的引用不在範圍內。

### Changed

- **產生的 `AGENTS.md`〈Startup self-check〉改為檔尾記號。** 原本要求第一次回覆列六行狀態（Agent／cwd／Loaded／是否看到 `AGENTS-EOF`／能力／模式）。那一行「看到 `AGENTS-EOF` 了嗎」是模型對自身 context 的自我報告，而 2.5.1〈The instrument decides what a `no` is worth〉已量到這種問法會漏報；六行狀態每個 session 還都要付一次成本。新做法：開頭記號只在檔尾最後一條指令裡出現，自檢段只說「記號由檔尾決定」，其餘只在偏離時回報。**沒讀到檔尾的 agent 不知道要印什麼**，所以印出記號就是行為式的證據，不必靠 agent 自己說讀到了。上游 vault 2026-09-17 起採用。`prompts/GEMINI.md` 同步改寫，且刻意不寫出記號本身。
- **`KB-ACCESS-001` 補上「平台沒有專用讀檔工具」的例外。** 原文寫「用 shell 讀內容本身不行」，套到只提供指令執行工具的 agent 會變成無解，常見的錯誤結論是回報「memory 無法載入」。新增一節：這時 shell 就是讀檔工具，但仍屬 FETCH——指定編碼、被截斷就依序補讀到完整為止、不宣稱 shell 給不了的時效標記與編輯前置檢查；例外只限文字，不放寬多媒體解析與任何權限。實測表加註「單一平台實測、依工具配置而定」。上游 vault 2026-10-06 為 Codex 加入此例外，這裡改寫成角色名、不綁定平台。
- 登記表補 reserve **`KB-CHANGE-002`**、**`KB-COLLAB-002`**（09-02 起上游已使用，2.5.1 補號時漏掉）、**`KB-VISUAL-004`**、**`KB-WRITING-004`**、**`KB-WRITING-005`**。同步上游 2026-09-02 的兩次合併：`KB-FRONTMATTER-002` 併入 `001`、`KB-TITLE-001` 併入 `KB-STRUCT-001`，被併的編號照舊永久佔號。本 repo 的 `Frontmatter remains structured` 只涵蓋清單格式，沒有吸收 `002` 的欄位語意，因此它的 `former_ids` 不填。

### Tests

- 39 則（33 → 39）：記號在產生的 `AGENTS.md` 只出現一次、位於 `AGENTS-EOF` 前一條指令，且不出現在任何轉接檔；正文引用未登記編號報錯並帶行號、已登記的通過、舊編號只報 warning 且指名現行編號、登記表外的命名空間不判、只保留的前綴在列舉後才開始判。

## 2.5.1 - 2026-09-07

### Added

- **`docs/AI_AGENT_GUIDE.md` 的載入行為表補三列**（Claude Code 2.1.263 實測）：同一個檔裡放多條 `@file` import **全部**展開、被匯入的檔再匯入一層也展開、匯入檔到 123 KB **沒有**截尾。⚠️ **這三列不推翻「不要靠 import 送規則」那一條**——那條的理由是**不可攜**（兩個工具只有一個支援），本輪量到的是**在 Claude Code 內部很可靠**。原文把「不可靠」與「不可攜」寫成同一個理由，已分開。
- **新增〈The instrument decides what a `no` is worth〉一節。** 第一輪用的是自由回想式提問（「列出你看到的哨兵」）；2026-09-07 用四個裝置、五個哨兵重測，量到它會漏：自由回想兩輪各漏一個且**漏的不是同一個**，辨認式（逐項 present／absent）仍漏一個，**只有行為式**——把候選檔的內容換成「被問到代號 `ONE` 就回答 `7Q4KX2`」再問那個代號——兩輪全對。前兩種問的是模型對自身 context 的自我報告，只有第三種問的是內容在不在。⇒ **表裡每個 `no` 的證據強度都弱於 `yes`**：`yes` 出現一次即成立，`no` 額外要求儀器不會漏報，而儀器已被量到會漏報。重測 `no` 一律改行為式，`yes` 沿用原問法即可。

### Changed

- 登記表補 reserve **`KB-VERIFY-006`**（生成類產物必須渲染回讀）與 **`KB-VERIFY-007`**（審閱清單須逐項回查原文）。上游 vault 已在使用這兩個編號，而登記表只登到 `005`——**登記表存在的目的就是讓新規約不會靜默重用一個已經有意義的編號，漏登兩個等於那道防護在這兩個號上是關閉的。** 兩者的規約筆記尚未通用化，因此是 `reserved` 不是 `shipped`。

## 2.5.0 - 2026-09-03

### Added

- **登記表可以列舉領域編號，而列舉本身就是開啟驗證的動作。** 原本 `PHENO-`／`ML-` 這類前綴只被「保留」：`check_registry` 對前綴命中的編號整段 `continue`，所以沒登記的領域編號一律放行。這在 framework 是對的——它的領域資料夾在樹外，本來就管不到；但複製到「領域資料夾就在自己樹裡」的 vault 之後就不成立了，那裡的領域編號沒有任何地方登記，退役也記錄不到。新規則是 **前綴有列舉列 ⇒ 驗證；只宣告前綴、沒有列舉列 ⇒ 跳過**，所以本 repo 的登記表沒有領域列、行為完全不變。分岔的是資料，不是結構。
- 領域表欄位 `| id | name_zh | lifecycle | note |`。第一欄刻意**不叫** `rule_id`——`parse_registry` 用 `header[:1] == ['rule_id']` 認規則表，同名會讓領域表被當成規則表而在欄位比對上直接失敗。
- `lifecycle` 是該表自己的封閉詞彙（`active`／`retired`），與 `status` 無關：`status` 回答「framework 有沒有出貨」，那個問題對領域規約不存在。退役編號永久佔號，與 `KB-*` 相同。

### Changed

- `parse_registry()` 回傳值由四元組改為 **`(rules, prefixes, domain, triggers, errors)`**（breaking，內部 API）。三個呼叫端已同步：`check_registry`、`main` 的詞彙查詢、`setup_v2.write_registry`。
- `--strict-registry` 下的領域檢查**只判斷本次 root 實際掃到的前綴**。沒有任何一個 root 同時涵蓋所有命名空間——`--root <KB 目錄>` 讀不到領域資料夾——所以少了這層限縮，開 strict 就會把所有領域列報成「無筆記宣稱」。

### Tests

- 33 則（28 → 33）：列舉後拒絕未登記的領域編號、接受已登記的、未掃到的前綴保持靜默、退役編號不得被宣稱、`lifecycle` 詞彙封閉。

## 2.4.0 - 2026-09-01

### Added

- **`--index`：一行一則規約（id／triggers／名稱／一句話版），讓「分類任務」這一步變得不必要。** 封閉詞彙解決了「撈得到」，但入口仍是 agent 自行判斷任務類別，而那一步猜錯不留痕跡。實測上游 vault：51 則全文約 99 k 字元，索引只有 **6.7 k（6.7%）**——便宜到可以整份讀。**辨認**比**回想**可靠，而回想失敗時沒有任何東西會發現。索引即時產生不落檔（存一份就是登記表要防的第二份複本）。
- `--for-trigger` 與 `--index` 分工：前者在任務已明確時收窄到一個詞，後者在還不確定時整份掃。

### Changed

- `headline()` 接受兩種形狀：`In one line`／`一句話版` 區段的引言，或**整篇只有一段短文**時的那一段——framework 自己的 14 條規約都是後者，硬要它們多開一個區段等於在四行的檔案裡把同一句寫兩次。超過 400 字元即視為正文而非標題，`--index` 改列為缺標題，避免整段文字灌進索引。
- 產生的 Convention MOC〈Working with these rules〉第 1 條改為「先讀索引」，附兩道指令。
- **`validate_conventions.py` 顯式把 stdout 設成 UTF-8**：Windows 主控台預設 legacy codepage（本機 cp950），印出中文規約名會 `UnicodeEncodeError`，**導向檔案時同樣會死**。修在工具裡而不是要求每個呼叫端設環境變數。

### Tests

- 23 → 26：索引涵蓋每一則且都有標題、缺標題會被列出（用超過上限的段落觸發）、多行引言會被併成一行。

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
