/**
 * QuickAdd Macro: Create Concept Note
 *
 * Usage: Select text in Obsidian editor → run this macro via command palette or right-click
 *
 * What it does:
 * 1. Takes selected text as concept name
 * 2. Asks user to choose domain (OV-* folder)
 * 3. Creates a stub note with YAML frontmatter at the correct path
 * 4. Replaces selected text with [[concept]] wiki link in source document
 * 5. Appends to inbox queue for Claude Code to enrich later
 */
module.exports = async (params) => {
    const { app, quickAddApi } = params;

    // ── 1. Get selected text ───────────────────────────────
    const activeView = app.workspace.activeLeaf?.view;
    if (!activeView || !activeView.editor) {
        new Notice("Please open a markdown file and select text first.");
        return;
    }
    const editor = activeView.editor;
    let selection = editor.getSelection().trim();

    if (!selection) {
        // If no selection, prompt for input
        selection = await quickAddApi.inputPrompt("Enter concept name", "e.g. 高光譜");
        if (!selection) return;
    }

    const conceptName = selection.trim();

    // ── 1b. Extract Chinese title from bracket patterns ──────
    // Matches: 中文(English), English(中文), 中文（English）, English（中文）
    const hasCJK = (s) => /[\u4e00-\u9fff\u3400-\u4dbf]/.test(s);
    const bracketMatch = conceptName.match(/^(.+?)[（(](.+?)[）)]$/);
    let displayName = conceptName; // used in note body (original text)
    let titleName = conceptName;   // used as filename (prefer Chinese)
    const aliases = [];

    if (bracketMatch) {
        const outside = bracketMatch[1].trim();
        const inside = bracketMatch[2].trim();
        if (hasCJK(outside)) {
            // 光合作用(Photosynthesis) → title=光合作用, alias=Photosynthesis
            titleName = outside;
            aliases.push(inside);
        } else if (hasCJK(inside)) {
            // NDVI(歸一化植被指數) → title=歸一化植被指數, alias=NDVI
            titleName = inside;
            aliases.push(outside);
        } else {
            // Both non-Chinese: mAP(mean Average Precision) → title=mAP, alias=full name
            titleName = outside;
            aliases.push(inside);
        }
    }

    // ── 1c. Sanitize filename (replace illegal chars) ────────
    // Characters illegal in filenames: / \ : * ? " < > |
    const illegalChars = /[/\\:*?"<>|]/g;
    const safeName = titleName.replace(illegalChars, (ch) => {
        const map = { "/": "／", "\\": "＼", ":": "：", "*": "＊", "?": "？", '"': "＂", "<": "＜", ">": "＞", "|": "｜" };
        return map[ch] || "_";
    });
    if (safeName !== titleName) {
        aliases.push(titleName);
    }

    // ── 2. Check if note already exists ────────────────────
    const existingFile = app.metadataCache.getFirstLinkpathDest(safeName, "");
    if (existingFile) {
        new Notice(`Note [[${safeName}]] already exists at ${existingFile.path}`);
        // Still replace selection with link (use safeName for valid path)
        if (editor.getSelection()) {
            editor.replaceSelection(`[[${safeName}]]`);
        }
        return;
    }

    // ── 3. Choose domain ───────────────────────────────────
    const domainChoices = [
        "OV-Bioinformatics — 生物資訊/植物生理/育種",
        "OV-MachineLearning — 機器學習/電腦視覺/深度學習",
        "OV-Pheno — 植物表型分析",
        "OV-Software — 軟體/程式設計",
        "OV-Database — 資料庫",
        "OV-Docker — Docker/DevOps",
        "OV-Git — 版本控制",
        "OV-Hardware — 硬體/感測器",
        "OV-Ubuntu — Linux/系統管理",
    ];
    const domainKeys = [
        "OV-Bioinformatics",
        "OV-MachineLearning",
        "OV-Pheno",
        "OV-Software",
        "OV-Database",
        "OV-Docker",
        "OV-Git",
        "OV-Hardware",
        "OV-Ubuntu",
    ];

    const chosenDisplay = await quickAddApi.suggester(domainChoices, domainKeys);
    if (!chosenDisplay) return;
    const domain = chosenDisplay;

    // ── 4. Get source paper context ────────────────────────
    const activeFile = app.workspace.getActiveFile();
    const sourcePaper = activeFile ? activeFile.basename : "unknown";
    const cursorLine = editor.getCursor().line;
    // Get surrounding context (3 lines before and after)
    const totalLines = editor.lineCount();
    const contextStart = Math.max(0, cursorLine - 3);
    const contextEnd = Math.min(totalLines - 1, cursorLine + 3);
    let contextLines = [];
    for (let i = contextStart; i <= contextEnd; i++) {
        contextLines.push(editor.getLine(i));
    }
    const context = contextLines.join("\n");

    // ── 5. Create stub note ────────────────────────────────
    const notePath = `${domain}/Note/${safeName}.md`;
    const now = new Date();
    const dateStr = now.toISOString().split("T")[0];

    // Build YAML: add aliases if title differs from original or has bracket parts
    const yamlLines = [
        "---",
        "cssclasses: []",
        `created: ${dateStr}`,
        `source: "[[${sourcePaper}]]"`,
    ];
    if (aliases.length > 0) {
        const aliasStr = aliases.map((a) => `"${a}"`).join(", ");
        yamlLines.push(`aliases: [${aliasStr}]`);
    }
    yamlLines.push("---");

    const stubContent = [
        ...yamlLines,
        "#### 待整理",
        "",
        `## 一句話版`,
        `> **${displayName}** — `,
        "",
        "## 定義",
        "",
        "## 核心概念",
        "",
        "## 在我的研究中的應用",
        "",
        "## 相關筆記",
        "",
        "## 待解決問題",
        "",
    ].join("\n");

    try {
        // Ensure directory exists
        const folderPath = `${domain}/Note`;
        if (!app.vault.getAbstractFileByPath(folderPath)) {
            await app.vault.createFolder(folderPath);
        }
        await app.vault.create(notePath, stubContent);
        new Notice(`Created: ${notePath}`);
    } catch (e) {
        new Notice(`Error creating note: ${e.message}`);
        return;
    }

    // ── 6. Replace selection with wiki link ────────────────
    if (editor.getSelection()) {
        editor.replaceSelection(`[[${safeName}]]`);
    }

    // ── 6b. Open the new stub note in a new tab ──────────
    const newFile = app.vault.getAbstractFileByPath(notePath);
    if (newFile) {
        await app.workspace.getLeaf("tab").openFile(newFile);
    }

    // ── 7. Append to inbox queue ───────────────────────────
    const inboxPath = "OV-Papers/enrich-inbox.md";
    const inboxEntry = [
        "",
        `## [[${safeName}]]`,
        `- **Domain**: ${domain}`,
        `- **Source**: [[${sourcePaper}]]`,
        `- **Date**: ${dateStr}`,
        `- **Status**: pending`,
        `- **Context**:`,
        "```",
        context,
        "```",
        "",
    ].join("\n");

    let inboxFile = app.vault.getAbstractFileByPath(inboxPath);
    if (inboxFile) {
        const existing = await app.vault.read(inboxFile);
        await app.vault.modify(inboxFile, existing + inboxEntry);
    } else {
        const header = "# Concept Note Enrichment Inbox\n\n> Auto-generated by QuickAdd. Use `/process-inbox` in Claude Code to enrich these notes.\n";
        await app.vault.create(inboxPath, header + inboxEntry);
    }

    new Notice(`Queued [[${safeName}]] for enrichment`);
};
