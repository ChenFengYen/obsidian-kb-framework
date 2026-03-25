"""
Insert figure references into paper markdown files.

Inserts ![[paperID_figN.png|500]] into the 📊 結果 > 圖表整理 section.
Creates backups before modifying any file.

Usage:
    python insert_figures.py                   # Process all papers with figures
    python insert_figures.py --paper-id NAME   # Process single paper
    python insert_figures.py --dry-run         # Preview changes
"""
import argparse
import os
import re
import shutil
from datetime import datetime

from config import PDF_MD_DIR, PDF_ASSETS_DIR, BACKUP_DIR, FIGURES_SECTION
from status_tracker import update_paper_status


def get_papers_with_figures() -> dict[str, list[str]]:
    """Find papers that have extracted figures in PDF-assets/.

    Returns {paper_id: [fig1.png, fig2.png, ...]}
    """
    papers = {}
    for fname in os.listdir(PDF_ASSETS_DIR):
        if not fname.endswith(".png"):
            continue
        # Parse: paperID_figN.png
        match = re.match(r"^(.+)_fig(\d+)\.png$", fname)
        if match:
            paper_id = match.group(1)
            papers.setdefault(paper_id, []).append(fname)

    # Sort figures within each paper
    for pid in papers:
        papers[pid].sort(key=lambda f: int(re.search(r"fig(\d+)", f).group(1)))

    return papers


def has_figure_embeds(content: str, paper_id: str) -> bool:
    """Check if markdown already has figure embeds for this paper."""
    return f"![[{paper_id}_fig" in content


def insert_figures_into_md(
    paper_id: str, figures: list[str], dry_run: bool = False
) -> bool:
    """Insert figure references into a paper's markdown.

    Returns True if file was modified.
    """
    md_path = os.path.join(PDF_MD_DIR, f"{paper_id}.md")
    if not os.path.exists(md_path):
        print(f"  [SKIP] Markdown not found: {md_path}")
        return False

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already has figure embeds
    if has_figure_embeds(content, paper_id):
        print(f"  [SKIP] {paper_id} already has figure embeds")
        return False

    # Find the 圖表整理 section or 📊 結果 section
    # Try to find "## 圖表整理" first
    insert_marker = FIGURES_SECTION  # "## 圖表整理"
    results_marker = "# 📊 結果"

    lines = content.split("\n")
    insert_idx = None

    # Strategy 1: Find "## 圖表整理" and insert after it
    for i, line in enumerate(lines):
        if "圖表整理" in line and line.strip().startswith("#"):
            insert_idx = i + 1
            break

    # Strategy 2: Find "# 📊 結果" and insert after the first subheading or right after
    if insert_idx is None:
        for i, line in enumerate(lines):
            if "📊 結果" in line or "📊 結果" in line:
                # Look for a subsection header after this
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip().startswith("##"):
                        insert_idx = j + 1
                        break
                if insert_idx is None:
                    insert_idx = i + 1
                break

    # Strategy 3: Insert before 🧠 討論 section
    if insert_idx is None:
        for i, line in enumerate(lines):
            if "🧠 討論" in line:
                insert_idx = i
                break

    if insert_idx is None:
        print(f"  [WARN] Could not find insertion point for {paper_id}")
        # Fallback: append before last section
        insert_idx = len(lines) - 1

    # Build figure block
    fig_block = [
        "",
        "<!-- AUTO-INSERTED FIGURES - NEEDS HUMAN REVIEW -->",
        "",
    ]
    for fig_file in figures:
        fig_num = re.search(r"fig(\d+)", fig_file).group(1)
        fig_block.append(f"![[{fig_file}|500]]")
        fig_block.append(f"- **圖 {fig_num}**：（待補充說明）")
        fig_block.append("")

    if dry_run:
        print(f"  [DRY-RUN] Would insert {len(figures)} figures at line {insert_idx}")
        for line in fig_block:
            if line.startswith("![["):
                print(f"    {line}")
        return False

    # Backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"{paper_id}.md")
    shutil.copy2(md_path, backup_path)

    # Insert
    new_lines = lines[:insert_idx] + fig_block + lines[insert_idx:]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"  Inserted {len(figures)} figures into {paper_id}.md (line {insert_idx})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Insert figure references into markdown")
    parser.add_argument("--paper-id", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    papers_with_figs = get_papers_with_figures()
    print(f"[insert_figures] Found {len(papers_with_figs)} papers with extracted figures")

    if args.paper_id:
        if args.paper_id not in papers_with_figs:
            print(f"  No figures found for {args.paper_id}")
            return
        figures = papers_with_figs[args.paper_id]
        insert_figures_into_md(args.paper_id, figures, dry_run=args.dry_run)
        return

    modified = 0
    skipped = 0
    for paper_id, figures in sorted(papers_with_figs.items()):
        result = insert_figures_into_md(paper_id, figures, dry_run=args.dry_run)
        if result:
            modified += 1
            if not args.dry_run:
                update_paper_status(paper_id, figures_extracted="[yes]")
        else:
            skipped += 1

    print(f"\n[insert_figures] Done. Modified: {modified}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
