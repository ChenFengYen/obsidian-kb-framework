"""
Create approved concept stub notes from candidates_review.md.

Only creates stubs for items that are checked (- [x]) in the review file.

Usage:
    python create_stubs.py              # Create checked stubs
    python create_stubs.py --dry-run    # Preview what would be created
"""
import argparse
import os
import re
from datetime import datetime

from config import (
    CANDIDATES_REVIEW_FILE,
    OV_FOLDERS,
    VAULT_ROOT,
)


def parse_approved_candidates(filepath: str = CANDIDATES_REVIEW_FILE) -> list[dict]:
    """Parse candidates_review.md and return checked items."""
    if not os.path.exists(filepath):
        print(f"[create_stubs] File not found: {filepath}")
        print("  Run extract_candidates.py first.")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    approved = []
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]
        # Match checked items: - [x] "term" → domain/Note/ (N papers, ...)
        m = re.match(
            r'^- \[x\] "(.+?)" → ([\w-]+)/Note/',
            line,
            re.IGNORECASE,
        )
        if m:
            term = m.group(1)
            domain = m.group(2)

            # Look for papers line below
            papers = []
            if i + 1 < len(lines):
                papers_line = lines[i + 1]
                paper_matches = re.findall(r"\[\[(\w+)\]\]", papers_line)
                papers = paper_matches

            approved.append({
                "term": term,
                "domain": domain,
                "papers": papers,
            })
        i += 1

    return approved


def create_stub_note(
    term: str,
    domain: str,
    papers: list[str],
    dry_run: bool = False,
) -> bool:
    """Create a stub note in the appropriate OV-*/Note/ folder.

    Returns True if created successfully.
    """
    if domain not in OV_FOLDERS:
        print(f"  [WARN] Unknown domain {domain}, using default path")
        domain = "OV-MachineLearning"

    note_dir = os.path.join(OV_FOLDERS[domain], "Note")
    if not os.path.isdir(note_dir):
        os.makedirs(note_dir, exist_ok=True)

    # Sanitize filename
    safe_name = term.replace("/", "-").replace("\\", "-").replace(":", "-")
    filepath = os.path.join(note_dir, f"{safe_name}.md")

    if os.path.exists(filepath):
        print(f"  [SKIP] Already exists: {filepath}")
        return False

    # Build cssclasses from source papers
    cssclasses = [f'"[[{p}]]"' for p in papers[:5]]

    # Build related notes (from same domain)
    related = []
    for fname in os.listdir(note_dir):
        if fname.endswith(".md") and fname != f"{safe_name}.md":
            related.append(fname[:-3])
        if len(related) >= 3:
            break

    # Generate stub content
    content_lines = [
        "---",
        "cssclasses:",
    ]
    for cls in cssclasses:
        content_lines.append(f"  - {cls}")
    content_lines.extend([
        "---",
        "#### 待整理 (Auto-generated stub)",
        "",
        "## 定義",
        f"{term} -- 此概念筆記由批次處理自動建立，需人工補充內容。",
        "",
        "## 來源論文",
    ])
    for p in papers:
        content_lines.append(f"- [[{p}]]")
    content_lines.extend([
        "",
        "## 相關筆記",
    ])
    for r in related:
        content_lines.append(f"- [[{r}]]")
    content_lines.extend([
        "",
        "## 待解決問題",
        "- 此概念的核心定義是什麼？",
        "- 它如何應用於我的研究？",
        "",
    ])

    content = "\n".join(content_lines)

    if dry_run:
        print(f"  [DRY-RUN] Would create: {filepath}")
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Created: {filepath}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Create approved concept stub notes")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    approved = parse_approved_candidates()
    if not approved:
        print("[create_stubs] No approved candidates found.")
        print("  Edit candidates_review.md and check items with [x].")
        return

    print(f"[create_stubs] Found {len(approved)} approved candidates")
    print()

    created = 0
    for item in approved:
        result = create_stub_note(
            item["term"],
            item["domain"],
            item["papers"],
            dry_run=args.dry_run,
        )
        if result:
            created += 1

    print(f"\n[create_stubs] Done. Created {created} stub notes.")


if __name__ == "__main__":
    main()
