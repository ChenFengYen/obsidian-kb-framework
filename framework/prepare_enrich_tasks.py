"""
Prepare enrichment task files for Claude Code to process.

Scans for thin/empty notes, collects relevant paper context,
and generates structured markdown task files that Claude Code
can read and act on.

NOTE: This script targets "basic" level enrichment (10-15 lines).
Deep enrichment to "rich" level (≥30 lines) is handled by the
question-driven collaboration mode, not by batch processing.

Usage:
    python prepare_enrich_tasks.py                      # All thin notes
    python prepare_enrich_tasks.py --domain OV-Bioinformatics  # One domain
    python prepare_enrich_tasks.py --domain OV-MachineLearning --batch-size 10
    python prepare_enrich_tasks.py --note "光合作用"     # Single note
    python prepare_enrich_tasks.py --physio-only        # Plant physiology priority
"""
import argparse
import os
import re
import yaml
from datetime import datetime

from config import (
    VAULT_ROOT,
    OV_FOLDERS,
    PDF_MD_DIR,
    PAPERS_ROOT,
    STYLE_REFERENCE_NOTE,
    BOOST_PATTERNS,
    BATCH_SIZE,
)


# ── Threshold for "thin" notes ──────────────────────────────
THIN_THRESHOLD = 10  # lines of actual content (excluding frontmatter)

# STYLE_REFERENCE_NOTE and BOOST_PATTERNS loaded from vault_config.yaml via config.py
# See vault_config.yaml.example for reference values.

# ── Output directory ────────────────────────────────────────
TASKS_DIR = os.path.join(PAPERS_ROOT, "enrich-tasks")


def _load_style_reference() -> str:
    """Load a real example note to embed as style reference in task files.

    Since batch enrichment now targets basic level (10-15 lines),
    only the first ~30 lines are needed as a lightweight reference.
    """
    if not STYLE_REFERENCE_NOTE or not os.path.exists(STYLE_REFERENCE_NOTE):
        return ""
    try:
        with open(STYLE_REFERENCE_NOTE, "r", encoding="utf-8") as f:
            content = f.read()
        # Only need ~30 lines for basic-level reference
        lines = content.split("\n")
        if len(lines) > 30:
            lines = lines[:30] + ["", "（... 省略 — 批量充實僅需 basic 等級 ...）"]
        return "\n".join(lines)
    except (OSError, UnicodeDecodeError):
        return ""


def _is_boosted_topic(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in BOOST_PATTERNS)


def _read_note(filepath: str) -> tuple[str, str, int]:
    """Read a note file. Returns (frontmatter_str, body, content_lines)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter = ""
    body = content
    if content.startswith("---"):
        try:
            end = content.index("---", 3)
            frontmatter = content[: end + 3]
            body = content[end + 3 :].strip()
        except ValueError:
            pass

    content_lines = len([
        l for l in body.split("\n")
        if l.strip() and not l.startswith("cssclasses")
    ])
    return frontmatter, body, content_lines


def _find_papers_mentioning(concept: str) -> list[dict]:
    """Find papers whose keywords, body, or field mention this concept.

    Returns list of {paper_id, importance, excerpt} sorted by importance.
    """
    results = []
    concept_lower = concept.lower()

    for fname in os.listdir(PDF_MD_DIR):
        if not fname.endswith(".md"):
            continue
        paper_id = fname[:-3]
        filepath = os.path.join(PDF_MD_DIR, fname)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        # Check if concept appears in paper
        if concept_lower not in content.lower():
            continue

        # Parse frontmatter for importance
        importance = 3
        title = paper_id
        if content.startswith("---"):
            try:
                end = content.index("---", 3)
                fm = yaml.safe_load(content[3:end]) or {}
                if "rating" in fm and isinstance(fm["rating"], dict):
                    try:
                        importance = int(fm["rating"].get("importance", 3))
                    except (ValueError, TypeError):
                        pass
                title = fm.get("title", paper_id)
            except (ValueError, yaml.YAMLError):
                pass

        # Extract relevant excerpt (paragraph containing the concept)
        excerpt = _extract_relevant_excerpt(content, concept)

        results.append({
            "paper_id": paper_id,
            "importance": importance,
            "title": title[:80],
            "excerpt": excerpt,
        })

    # Sort by importance descending
    results.sort(key=lambda x: -x["importance"])
    return results


def _extract_relevant_excerpt(content: str, concept: str, context_chars: int = 500) -> str:
    """Extract the most relevant paragraph containing the concept."""
    # Skip frontmatter
    if content.startswith("---"):
        try:
            end = content.index("---", 3)
            content = content[end + 3:]
        except ValueError:
            pass

    # Find the concept in content
    lower_content = content.lower()
    concept_lower = concept.lower()
    pos = lower_content.find(concept_lower)
    if pos == -1:
        return ""

    # Extract surrounding context
    start = max(0, pos - context_chars // 2)
    end = min(len(content), pos + len(concept) + context_chars // 2)

    # Extend to paragraph boundaries
    while start > 0 and content[start] != "\n":
        start -= 1
    while end < len(content) and content[end] != "\n":
        end += 1

    excerpt = content[start:end].strip()

    # Trim to reasonable length
    lines = excerpt.split("\n")
    if len(lines) > 15:
        # Keep lines around the match
        for i, line in enumerate(lines):
            if concept_lower in line.lower():
                start_line = max(0, i - 5)
                end_line = min(len(lines), i + 10)
                lines = lines[start_line:end_line]
                break

    return "\n".join(lines)


def _find_thin_notes(domain: str = None, physio_only: bool = False) -> list[dict]:
    """Find notes that need enrichment."""
    thin_notes = []

    folders = OV_FOLDERS
    if domain:
        if domain in folders:
            folders = {domain: folders[domain]}
        else:
            print(f"[WARN] Domain {domain} not found")
            return []

    for folder_name, folder_path in folders.items():
        note_dir = os.path.join(folder_path, "Note")
        if not os.path.isdir(note_dir):
            continue

        for fname in sorted(os.listdir(note_dir)):
            if not fname.endswith(".md"):
                continue
            stem = fname[:-3]
            filepath = os.path.join(note_dir, fname)
            frontmatter, body, content_lines = _read_note(filepath)

            if content_lines >= THIN_THRESHOLD:
                continue

            is_physio = _is_boosted_topic(stem + " " + body)
            if physio_only and not is_physio:
                continue

            rel_path = os.path.relpath(filepath, VAULT_ROOT).replace("\\", "/")
            thin_notes.append({
                "stem": stem,
                "domain": folder_name,
                "path": rel_path,
                "abs_path": filepath,
                "frontmatter": frontmatter,
                "body": body,
                "content_lines": content_lines,
                "is_boosted": is_physio,
            })

    # Sort: physio first, then by content_lines ascending (emptiest first)
    thin_notes.sort(key=lambda x: (not x["is_boosted"], x["content_lines"]))
    return thin_notes


def generate_task_file(
    notes: list[dict],
    batch_name: str = None,
    max_papers_per_note: int = 5,
) -> str:
    """Generate a markdown task file for Claude Code to process."""
    if not batch_name:
        batch_name = datetime.now().strftime("%Y%m%d_%H%M")

    os.makedirs(TASKS_DIR, exist_ok=True)
    output_path = os.path.join(TASKS_DIR, f"enrich_batch_{batch_name}.md")

    # Load style reference
    style_ref = _load_style_reference()
    style_note_name = os.path.basename(STYLE_REFERENCE_NOTE)[:-3] if style_ref else ""

    lines = [
        f"# 概念筆記充實任務（basic 等級）- {batch_name}",
        "",
        f"> 產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 筆記數量：{len(notes)}",
        f"> 目標等級：**basic（10-15 行）** — 讓筆記可搜尋、可引用即可",
        "",
        "---",
        "",
        "## 使用方式",
        "",
        "請在 Claude Code 中執行以下指令：",
        "",
        "```",
        f"讀取 {os.path.relpath(output_path, VAULT_ROOT).replace(chr(92), '/')} 中的每個任務，",
        "針對每個概念筆記：",
        "1. 瀏覽來源論文的相關段落（路徑已提供），確保定義正確",
        "2. 寫出 basic 等級的內容（一句定義 + 核心要點 + 連結）",
        "3. 不需要寫「應用」和「待解決問題」區段 — 深化留給問題驅動模式",
        "4. 在筆記結尾加上 <!-- AI-ENRICHED - NEEDS REVIEW --> 標記",
        "```",
        "",
        "---",
        "",
        "## 目標筆記格式（basic 等級）",
        "",
        "```markdown",
        "---",
        "cssclasses:",
        '  - "[[相關筆記1]]"',
        '  - "[[相關筆記2]]"',
        "---",
        "#### 待整理",
        "",
        "## 一句話版",
        "> **概念名稱** — 一句話解釋核心概念。",
        "",
        "## 核心概念",
        "- 重點 1（2-3 個即可）",
        "- 重點 2",
        "",
        "## 相關筆記",
        "- [[相關概念1]]（3-5 個連結）",
        "- [[相關概念2]]",
        "```",
        "",
    ]

    # Embed lightweight style reference if available
    if style_ref:
        lines.extend([
            "---",
            "",
            f"## 風格參考（來自 {style_note_name}.md 前 30 行）",
            "",
            "```markdown",
            style_ref,
            "```",
            "",
        ])

    lines.extend(["---", ""])

    for i, note in enumerate(notes, 1):
        physio_tag = " 🌱" if note["is_boosted"] else ""

        lines.extend([
            f"## 任務 {i}/{len(notes)}: [[{note['stem']}]]{physio_tag}",
            "",
            f"- **檔案路徑**：`{note['path']}`",
            f"- **所屬領域**：{note['domain']}",
            f"- **目前內容行數**：{note['content_lines']}",
            "",
        ])

        # Current content
        if note["body"].strip():
            lines.extend([
                "### 目前內容",
                "",
                "```markdown",
                note["body"].strip(),
                "```",
                "",
            ])
        else:
            lines.append("### 目前內容：（空）\n")

        # Find related papers
        papers = _find_papers_mentioning(note["stem"])
        if not papers:
            # Try partial match for Chinese terms
            papers = _find_papers_mentioning(note["stem"][:2]) if len(note["stem"]) >= 2 else []

        papers = papers[:max_papers_per_note]

        if papers:
            lines.extend([
                f"### 來源論文摘錄（{len(papers)} 篇）",
                "",
            ])
            for p in papers:
                lines.extend([
                    f"#### [[{p['paper_id']}]] (importance: {p['importance']})",
                    f"- **路徑**：`OV-Papers/PDF-md/{p['paper_id']}.md`",
                    f"- **標題**：{p['title']}",
                    "",
                ])
                if p["excerpt"]:
                    lines.extend([
                        "**相關段落：**",
                        "",
                        f"> {p['excerpt'][:400]}",
                        "",
                    ])
        else:
            lines.append("### 來源論文：（未找到直接引用此概念的論文，請從領域知識充實）\n")

        lines.extend(["", "---", ""])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Prepare enrichment task files for Claude Code"
    )
    parser.add_argument("--domain", type=str, default=None,
                        help="Only process notes in this OV-* domain")
    parser.add_argument("--note", type=str, default=None,
                        help="Process a single note by name")
    parser.add_argument("--physio-only", action="store_true",
                        help="Only process plant physiology related notes")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Max notes per task file (default: 10)")
    parser.add_argument("--max-papers", type=int, default=3,
                        help="Max papers per note (default: 3)")
    args = parser.parse_args()

    if args.note:
        # Single note mode — find it
        found = None
        for folder_name, folder_path in OV_FOLDERS.items():
            note_dir = os.path.join(folder_path, "Note")
            filepath = os.path.join(note_dir, f"{args.note}.md")
            if os.path.exists(filepath):
                frontmatter, body, content_lines = _read_note(filepath)
                rel_path = os.path.relpath(filepath, VAULT_ROOT).replace("\\", "/")
                found = {
                    "stem": args.note,
                    "domain": folder_name,
                    "path": rel_path,
                    "abs_path": filepath,
                    "frontmatter": frontmatter,
                    "body": body,
                    "content_lines": content_lines,
                    "is_boosted": _is_boosted_topic(args.note + " " + body),
                }
                break
        if not found:
            print(f"[ERROR] Note not found: {args.note}")
            return
        notes = [found]
    else:
        notes = _find_thin_notes(
            domain=args.domain,
            physio_only=args.physio_only,
        )

    if not notes:
        print("[prepare_enrich_tasks] No thin notes found matching criteria.")
        return

    print(f"[prepare_enrich_tasks] Found {len(notes)} thin notes")
    physio_count = sum(1 for n in notes if n["is_boosted"])
    print(f"  Plant physiology related: {physio_count}")

    # Split into batches
    batch_num = 0
    for start in range(0, len(notes), args.batch_size):
        batch = notes[start : start + args.batch_size]
        batch_num += 1
        batch_name = f"batch{batch_num:02d}_{datetime.now().strftime('%Y%m%d')}"

        if args.domain:
            batch_name = f"{args.domain}_{batch_name}"
        if args.physio_only:
            batch_name = f"physio_{batch_name}"
        if args.note:
            batch_name = f"single_{args.note}"

        output = generate_task_file(
            batch,
            batch_name=batch_name,
            max_papers_per_note=args.max_papers,
        )
        print(f"  Generated: {os.path.relpath(output, VAULT_ROOT)}")

    print(f"\n[prepare_enrich_tasks] Done. {batch_num} task file(s) generated in:")
    print(f"  {os.path.relpath(TASKS_DIR, VAULT_ROOT)}/")
    print(f"\n使用方式：在 Claude Code 中請它讀取 task file 並逐一充實筆記。")


if __name__ == "__main__":
    main()
