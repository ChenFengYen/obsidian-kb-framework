"""
Inject [[concept]] wiki-links into paper markdown files.

Links first occurrence of each concept per major section.
Creates backups before modifying.

Usage:
    python inject_links.py                   # Process all unlinked papers
    python inject_links.py --paper-id NAME   # Process single paper
    python inject_links.py --dry-run         # Preview changes
    python inject_links.py --report          # Generate link_report.md only
"""
import argparse
import json
import os
import re
import shutil
from datetime import datetime

from config import (
    PDF_MD_DIR,
    BACKUP_DIR,
    SECTION_MARKERS,
    LINK_REPORT_FILE,
    SCAN_DIRS,
    VAULT_ROOT,
)
from concept_index import build_concept_index, get_matching_terms
from status_tracker import (
    get_papers,
    get_paper_id,
    get_priority_queue,
    update_paper_status,
)


# Directories excluded when SCAN_DIRS is "all"
_EXCLUDED_DIRS = {".obsidian", "PDF-raw", "Pic", ".git", "node_modules", ".trash"}


def _resolve_scan_files() -> list[str]:
    """Resolve SCAN_DIRS config into a list of .md file paths."""
    import glob as _glob

    if SCAN_DIRS == "all":
        md_files = []
        for root, dirs, files in os.walk(VAULT_ROOT):
            dirs[:] = [d for d in dirs if d not in _EXCLUDED_DIRS]
            for f in files:
                if f.endswith(".md"):
                    md_files.append(os.path.join(root, f))
        return md_files

    md_files = []
    for rel_dir in SCAN_DIRS:
        abs_dir = os.path.join(VAULT_ROOT, rel_dir)
        if os.path.isdir(abs_dir):
            md_files.extend(_glob.glob(os.path.join(abs_dir, "*.md")))
    return md_files


def _split_into_sections(content: str) -> list[tuple[str, str]]:
    """Split markdown into (header, body) tuples by major sections.

    Uses emoji section markers from config.
    """
    # Find all section boundaries
    pattern = r"^(# [🧾🎯💡🔬📊🧠🧩🧭].+)$"
    boundaries = []
    for m in re.finditer(pattern, content, re.MULTILINE):
        boundaries.append((m.start(), m.group(1)))

    if not boundaries:
        return [("", content)]

    sections = []
    for i, (start, header) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(content)
        body = content[start + len(header) : end]
        sections.append((header, body))

    # Include content before first section (frontmatter etc.)
    if boundaries[0][0] > 0:
        sections.insert(("__frontmatter__", content[: boundaries[0][0]]))

    return sections


def _is_in_protected_zone(text: str, pos: int) -> bool:
    """Check if position is inside frontmatter, code block, or existing [[link]]."""
    # Check frontmatter (--- ... ---)
    fm_match = re.match(r"^---\n.*?\n---", text, re.DOTALL)
    if fm_match and pos < fm_match.end():
        return True

    # Check code blocks
    for m in re.finditer(r"```.*?```", text, re.DOTALL):
        if m.start() <= pos < m.end():
            return True

    # Check existing [[ ]] links
    for m in re.finditer(r"\[\[.*?\]\]", text):
        if m.start() <= pos < m.end():
            return True

    # Check inline code `...`
    for m in re.finditer(r"`[^`]+`", text):
        if m.start() <= pos < m.end():
            return True

    # Check markdown image ![[...]]
    for m in re.finditer(r"!\[\[.*?\]\]", text):
        if m.start() <= pos < m.end():
            return True

    return False


def inject_links_into_paper(
    paper_id: str,
    matching_terms: list[tuple[str, str]],
    dry_run: bool = False,
    md_path_override: str | None = None,
) -> list[str]:
    """Inject [[concept]] links into a paper's markdown.

    Returns list of linked concept stems.
    """
    md_path = md_path_override or os.path.join(PDF_MD_DIR, f"{paper_id}.md")
    if not os.path.exists(md_path):
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections
    section_pattern = r"^(# [🧾🎯💡🔬📊🧠🧩🧭].+)$"
    section_starts = [(m.start(), m.group(1)) for m in re.finditer(section_pattern, content, re.MULTILINE)]

    # Build section ranges
    sections = []
    for i, (start, header) in enumerate(section_starts):
        end = section_starts[i + 1][0] if i + 1 < len(section_starts) else len(content)
        sections.append((start, end, header))

    if not sections:
        # Treat entire content as one section
        sections = [(0, len(content), "__all__")]

    linked_concepts = []
    replacements = []  # (start, end, replacement_text)

    for term, stem in matching_terms:
        # Track: only link first occurrence per section
        for sec_start, sec_end, sec_header in sections:
            # Skip frontmatter section
            if sec_header == "__frontmatter__" or "基本資訊" in sec_header:
                continue

            section_text = content[sec_start:sec_end]

            # Build search pattern for the term
            escaped = re.escape(term)
            is_ascii = term.isascii()

            if not is_ascii:
                # Chinese/mixed terms: no word boundaries (CJK chars are all \w)
                pattern = re.compile(escaped)
            elif len(term) <= 4:
                # Short ASCII terms: use word boundaries to avoid partial matches
                pattern = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
            else:
                # Longer ASCII terms: plain match, case-insensitive
                pattern = re.compile(escaped, re.IGNORECASE)

            for m in pattern.finditer(section_text):
                abs_pos = sec_start + m.start()
                abs_end = sec_start + m.end()

                # Check if already linked or in protected zone
                if _is_in_protected_zone(content, abs_pos):
                    continue

                # Check if already part of a replacement
                overlap = False
                for rs, re_, _ in replacements:
                    if not (abs_end <= rs or abs_pos >= re_):
                        overlap = True
                        break
                if overlap:
                    continue

                # Replace with [[stem]]
                original_text = content[abs_pos:abs_end]
                if stem == original_text:
                    replacement = f"[[{stem}]]"
                else:
                    replacement = f"[[{stem}|{original_text}]]"

                replacements.append((abs_pos, abs_end, replacement))
                if stem not in linked_concepts:
                    linked_concepts.append(stem)
                break  # Only first occurrence per section

    if not replacements:
        return []

    if dry_run:
        print(f"  [DRY-RUN] {paper_id}: would link {len(linked_concepts)} concepts")
        for concept in linked_concepts[:10]:
            print(f"    - {concept}")
        if len(linked_concepts) > 10:
            print(f"    ... and {len(linked_concepts) - 10} more")
        return linked_concepts

    # Backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"{paper_id}.md")
    if not os.path.exists(backup_path):
        shutil.copy2(md_path, backup_path)

    # Apply replacements (reverse order to preserve positions)
    replacements.sort(key=lambda x: x[0], reverse=True)
    new_content = content
    for start, end, repl in replacements:
        new_content = new_content[:start] + repl + new_content[end:]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  Linked {len(linked_concepts)} concepts in {paper_id}.md")
    return linked_concepts


def generate_link_report(all_results: dict[str, list[str]]):
    """Generate link_report.md with per-paper and global stats."""
    lines = [
        f"# Link Injection Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## Per-Paper Summary",
        "",
        "| Paper | Concepts Linked | Count |",
        "| --- | --- | --- |",
    ]

    concept_counts = {}  # concept → count of papers referencing it

    for paper_id, concepts in sorted(all_results.items()):
        if not concepts:
            continue
        concept_str = ", ".join(f"[[{c}]]" for c in concepts[:5])
        if len(concepts) > 5:
            concept_str += f" +{len(concepts)-5} more"
        lines.append(f"| [[{paper_id}]] | {concept_str} | {len(concepts)} |")

        for c in concepts:
            concept_counts[c] = concept_counts.get(c, 0) + 1

    lines.extend([
        "",
        "---",
        "",
        "## Most Referenced Concepts (Hub Notes)",
        "",
        "| Concept | Papers Referencing |",
        "| --- | --- |",
    ])

    for concept, count in sorted(concept_counts.items(), key=lambda x: -x[1])[:30]:
        lines.append(f"| [[{concept}]] | {count} |")

    # Orphan concepts (never referenced)
    from concept_index import build_concept_index
    index = build_concept_index()
    all_stems = set(info["stem"] for info in index["notes"].values())
    referenced = set(concept_counts.keys())
    orphans = all_stems - referenced

    lines.extend([
        "",
        "---",
        "",
        f"## Orphan Notes (never referenced by papers): {len(orphans)}",
        "",
    ])
    for orphan in sorted(orphans):
        lines.append(f"- [[{orphan}]]")

    with open(LINK_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[inject_links] Report saved to {LINK_REPORT_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Inject concept links into paper markdown")
    parser.add_argument("--paper-id", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", action="store_true", help="Only generate report from existing data")
    parser.add_argument("--batch-size", type=int, default=0, help="Limit papers to process (0=all)")
    parser.add_argument("--rescan", action="store_true",
                        help="Rescan ALL papers (including already-linked) for new concept notes")
    args = parser.parse_args()

    # Build concept index
    index = build_concept_index()
    matching_terms = get_matching_terms(index)
    print(f"[inject_links] {len(matching_terms)} matching terms loaded")

    all_results = {}

    if args.paper_id:
        concepts = inject_links_into_paper(args.paper_id, matching_terms, dry_run=args.dry_run)
        all_results[args.paper_id] = concepts
        if not args.dry_run and concepts:
            update_paper_status(args.paper_id, links_injected="[yes]")
    elif not args.report:
        # Batch process
        if args.rescan:
            # Rescan files in configured SCAN_DIRS for new concepts
            scan_files = _resolve_scan_files()
            queue = []
            for md_path in scan_files:
                pid = os.path.splitext(os.path.basename(md_path))[0]
                if pid:
                    queue.append({"_md_path": md_path, "_paper_id": pid})
            print(f"[inject_links] RESCAN mode: checking {len(queue)} files across {SCAN_DIRS}")
        else:
            papers = get_papers(status="processed", verified="no")
            queue = get_priority_queue(papers)

        if args.batch_size > 0:
            queue = queue[: args.batch_size]

        print(f"[inject_links] Processing {len(queue)} papers")
        print()

        for row in queue:
            if isinstance(row, dict) and "_md_path" in row:
                pid = row["_paper_id"]
                md_path = row["_md_path"]
            else:
                pid = get_paper_id(row)
                if not pid:
                    continue
                md_path = os.path.join(PDF_MD_DIR, f"{pid}.md")

            if not os.path.exists(md_path):
                continue

            concepts = inject_links_into_paper(
                pid, matching_terms, dry_run=args.dry_run, md_path_override=md_path
            )
            all_results[pid] = concepts

            if not args.dry_run and concepts:
                try:
                    update_paper_status(pid, links_injected="[yes]")
                except Exception:
                    pass  # Non-paper files won't have status entries

    # Generate report
    if all_results or args.report:
        generate_link_report(all_results)

    # Summary
    linked_papers = sum(1 for v in all_results.values() if v)
    total_links = sum(len(v) for v in all_results.values())
    print(f"\n[inject_links] Done. {linked_papers} papers linked, {total_links} total concept links.")


if __name__ == "__main__":
    main()
