#!/usr/bin/env python3
"""Vault health diagnostic tool.

Scans the Obsidian vault and optionally Zotero library to identify
structural issues: stub notes, orphaned concepts, broken links,
MOC coverage gaps, and Zotero-vault sync drift.

Outputs a Markdown report with suggested CLI commands to fix each issue.

Usage:
    python vault_health.py                # Full vault-side check
    python vault_health.py --zotero       # Include Zotero cross-check
    python vault_health.py --orphans      # Only orphan detection
    python vault_health.py --richness     # Only note richness stats
    python vault_health.py --broken-links # Only broken link scan
    python vault_health.py --summary      # One-paragraph summary
"""
import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

from config import (
    VAULT_ROOT, OV_FOLDERS, PDF_MD_DIR, PDF_RAW_DIR, SCRIPTS_DIR,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPORT_FILE = os.path.join(SCRIPTS_DIR, "vault_health_report.md")
MISSING_DOIS_FILE = os.path.join(SCRIPTS_DIR, "vault_health_missing.txt")

# Richness thresholds (content lines after YAML frontmatter)
RICHNESS_LEVELS = [
    ("stub", 0, 3),
    ("thin", 4, 9),
    ("basic", 10, 29),
    ("rich", 30, float("inf")),
]

# Wiki-link pattern: [[target]] or [[target|alias]]
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:[|#][^\]]*?)?\]\]")

# AI-ENRICHED marker
AI_ENRICHED_RE = re.compile(r"<!--\s*AI-ENRICHED")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _content_lines(filepath):
    """Count non-empty content lines after YAML frontmatter."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return 0

    # Strip YAML frontmatter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]

    lines = [l for l in text.strip().splitlines() if l.strip()]
    return len(lines)


def _classify_richness(line_count):
    """Return richness level name."""
    for name, lo, hi in RICHNESS_LEVELS:
        if lo <= line_count <= hi:
            return name
    return "rich"


def _list_md_files(directory):
    """List all .md files in a directory (non-recursive)."""
    if not os.path.isdir(directory):
        return []
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".md")
    ]


def _stem(filepath):
    """Get filename without extension."""
    return os.path.splitext(os.path.basename(filepath))[0]


def _extract_wikilinks(filepath):
    """Extract all wikilink targets from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return set()
    return set(WIKILINK_RE.findall(text))


def _all_md_files_recursive(root):
    """Walk root and yield all .md file paths."""
    for dirpath, _, filenames in os.walk(root):
        # Skip hidden dirs and PDF-raw
        basename = os.path.basename(dirpath)
        if basename.startswith(".") or basename == "PDF-raw":
            continue
        for f in filenames:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


# ---------------------------------------------------------------------------
# Build vault index (used by multiple checks)
# ---------------------------------------------------------------------------


def build_vault_index():
    """Build a mapping of all .md stems to their paths."""
    index = {}  # stem -> path
    for fpath in _all_md_files_recursive(VAULT_ROOT):
        stem = _stem(fpath)
        if stem not in index:
            index[stem] = fpath
    return index


# ---------------------------------------------------------------------------
# Check: Note richness
# ---------------------------------------------------------------------------


def check_richness():
    """Compute richness distribution per domain."""
    results = {}  # domain -> {level: [stems]}
    for domain, folder in sorted(OV_FOLDERS.items()):
        note_dir = os.path.join(folder, "Note")
        notes = _list_md_files(note_dir)
        dist = defaultdict(list)
        for fpath in notes:
            lc = _content_lines(fpath)
            level = _classify_richness(lc)
            dist[level].append(_stem(fpath))
        results[domain] = dict(dist)
    return results


# ---------------------------------------------------------------------------
# Check: Orphan concepts (not in any MOC)
# ---------------------------------------------------------------------------


def check_orphans():
    """Find concept notes not referenced by any Map/*.md."""
    # Collect all concept note stems per domain
    all_concepts = {}  # domain -> set of stems
    for domain, folder in sorted(OV_FOLDERS.items()):
        note_dir = os.path.join(folder, "Note")
        notes = _list_md_files(note_dir)
        all_concepts[domain] = {_stem(f) for f in notes}

    # Collect all wikilink targets from Map/ files across all domains
    moc_linked = set()
    for domain, folder in OV_FOLDERS.items():
        map_dir = os.path.join(folder, "Map")
        for fpath in _list_md_files(map_dir):
            moc_linked.update(_extract_wikilinks(fpath))

    # Also check Home.md
    home = os.path.join(VAULT_ROOT, "Home.md")
    if os.path.exists(home):
        moc_linked.update(_extract_wikilinks(home))

    # Find orphans per domain
    orphans = {}
    for domain, concepts in sorted(all_concepts.items()):
        domain_orphans = sorted(concepts - moc_linked)
        if domain_orphans:
            orphans[domain] = domain_orphans

    return orphans


# ---------------------------------------------------------------------------
# Check: Broken links
# ---------------------------------------------------------------------------


# Extensions that are embedded, not note links
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp",
                    ".canvas", ".pdf"}
# Single-char or example-only targets to skip
BROKEN_LINK_SKIP = {
    "A", "B", "C", "X", "target", "citekey", "另一個相關概念", "連結的概念",
    "conceptName", "fig", "gpu",
}


def check_broken_links(vault_index):
    """Find [[target]] where target.md doesn't exist.

    Skips image embeds, single-char placeholders, and non-vault files.
    """
    broken = defaultdict(list)  # target -> [source files]
    # Skip our own report file to avoid self-referencing
    skip_files = {os.path.normpath(REPORT_FILE)}
    for fpath in _all_md_files_recursive(VAULT_ROOT):
        if os.path.normpath(fpath) in skip_files:
            continue
        targets = _extract_wikilinks(fpath)
        for t in targets:
            # Skip image/canvas/pdf embeds
            if any(t.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                continue
            # Skip backslash-suffixed (Obsidian table escape artifacts)
            if t.endswith("\\"):
                continue
            # Skip single-char or known placeholders
            if t in BROKEN_LINK_SKIP or len(t) <= 1:
                continue
            if t not in vault_index:
                rel = os.path.relpath(fpath, VAULT_ROOT)
                broken[t].append(rel)

    return dict(broken)


# ---------------------------------------------------------------------------
# Check: MOC coverage
# ---------------------------------------------------------------------------


def check_moc_coverage():
    """Per domain: how many notes are covered by MOCs."""
    results = {}
    for domain, folder in sorted(OV_FOLDERS.items()):
        note_dir = os.path.join(folder, "Note")
        map_dir = os.path.join(folder, "Map")
        notes = {_stem(f) for f in _list_md_files(note_dir)}
        if not notes:
            continue

        # Links from this domain's MOCs
        linked = set()
        for fpath in _list_md_files(map_dir):
            linked.update(_extract_wikilinks(fpath))

        covered = notes & linked
        results[domain] = {
            "total": len(notes),
            "covered": len(covered),
            "pct": round(100 * len(covered) / len(notes)) if notes else 0,
        }
    return results


# ---------------------------------------------------------------------------
# Check: AI-ENRICHED pending review
# ---------------------------------------------------------------------------


def check_ai_enriched():
    """Find concept/paper notes with <!-- AI-ENRICHED --> marker."""
    pending = []
    # Only scan OV-*/Note/ directories (not skills, enrich-tasks, etc.)
    scan_dirs = []
    for folder in OV_FOLDERS.values():
        note_dir = os.path.join(folder, "Note")
        if os.path.isdir(note_dir):
            scan_dirs.append(note_dir)

    for scan_dir in scan_dirs:
        for fpath in _list_md_files(scan_dir):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    head = f.read(3000)
            except (OSError, UnicodeDecodeError):
                continue
            if AI_ENRICHED_RE.search(head):
                pending.append(os.path.relpath(fpath, VAULT_ROOT))
    return sorted(pending)


# ---------------------------------------------------------------------------
# Check: Concept → Paper backlinks
# ---------------------------------------------------------------------------


def check_concept_paper_backlinks():
    """Count how many concept notes reference at least one paper."""
    # Build set of paper stems
    paper_stems = {_stem(f) for f in _list_md_files(PDF_MD_DIR)}

    with_backlink = 0
    without_backlink = 0
    missing_examples = []

    for domain, folder in sorted(OV_FOLDERS.items()):
        note_dir = os.path.join(folder, "Note")
        for fpath in _list_md_files(note_dir):
            links = _extract_wikilinks(fpath)
            if links & paper_stems:
                with_backlink += 1
            else:
                without_backlink += 1
                if len(missing_examples) < 10:
                    missing_examples.append(_stem(fpath))

    return {
        "with": with_backlink,
        "without": without_backlink,
        "examples": missing_examples,
    }


# ---------------------------------------------------------------------------
# Check: Zotero (optional)
# ---------------------------------------------------------------------------


def check_zotero():
    """Cross-check Zotero library vs vault. Returns dict or None on error."""
    try:
        from dotenv import load_dotenv
        from pyzotero import zotero

        env_path = os.path.join(VAULT_ROOT, "zotero-ai-agent", ".env")
        load_dotenv(env_path)

        api_key = os.getenv("ZOTERO_API_KEY")
        lib_id = os.getenv("ZOTERO_LIBRARY_ID")
        lib_type = os.getenv("ZOTERO_LIBRARY_TYPE", "user")
        if not api_key or not lib_id:
            print("  Warning: ZOTERO_API_KEY/LIBRARY_ID not set, skipping Zotero check")
            return None

        zot = zotero.Zotero(lib_id, lib_type, api_key)
    except ImportError:
        print("  Warning: pyzotero not installed, skipping Zotero check")
        return None

    # Fetch all items (paginated)
    print("  Fetching Zotero library...")
    all_items = []
    start = 0
    while True:
        batch = zot.top(limit=100, start=start)
        if not batch:
            break
        all_items.extend(batch)
        if len(batch) < 100:
            break
        start += 100

    # Build Zotero DOI/title map
    zotero_items = []
    for item in all_items:
        d = item.get("data", {})
        if d.get("itemType") in ("attachment", "note"):
            continue
        zotero_items.append({
            "key": d.get("key", ""),
            "title": d.get("title", ""),
            "doi": d.get("DOI", ""),
            "tags": [t["tag"] for t in d.get("tags", [])],
        })

    # Vault paper stems
    vault_papers = {_stem(f) for f in _list_md_files(PDF_MD_DIR)}

    # PDF-raw files
    pdf_raw_files = set()
    if os.path.isdir(PDF_RAW_DIR):
        pdf_raw_files = {
            os.path.splitext(f)[0]
            for f in os.listdir(PDF_RAW_DIR)
            if f.endswith(".pdf")
        }

    # Zotero titles for fuzzy matching against vault stems
    # Can't match by citekey (BBT limitation), so match by title keywords
    zotero_titles = {zi["key"]: zi["title"] for zi in zotero_items}

    # Simple heuristic: vault stems are usually author+year+keyword
    # Check which Zotero items have NO matching vault stem
    matched_keys = set()
    for stem in vault_papers:
        # Extract year from stem (e.g., "yu2024timeseries" -> "2024")
        m = re.search(r"(\d{4})", stem)
        if not m:
            continue
        year = m.group(1)
        # Extract author prefix (letters before year)
        author = re.match(r"([a-z]+)", stem)
        author = author.group(1) if author else ""
        if len(author) < 2:
            continue
        # Match against Zotero items
        for zi in zotero_items:
            creators = zi.get("title", "").lower()
            # Check if title contains year (rough match)
            if year in (zi.get("doi", "") or "") or author in zi["title"].lower()[:30]:
                matched_keys.add(zi["key"])

    unmatched = [zi for zi in zotero_items if zi["key"] not in matched_keys]

    # Untagged count
    untagged = [zi for zi in zotero_items if not zi["tags"]]

    # PDF coverage: vault papers with matching PDF-raw
    papers_with_pdf = vault_papers & pdf_raw_files
    papers_without_pdf = vault_papers - pdf_raw_files

    # Write missing DOIs file
    missing_dois = [zi["doi"] for zi in unmatched if zi.get("doi")]
    if missing_dois:
        with open(MISSING_DOIS_FILE, "w", encoding="utf-8") as f:
            f.write("# Zotero papers not found in vault (DOIs)\n")
            f.write(f"# Generated by vault_health.py on {datetime.now():%Y-%m-%d}\n")
            for doi in sorted(missing_dois):
                f.write(f"{doi}\n")

    return {
        "total_zotero": len(zotero_items),
        "total_vault": len(vault_papers),
        "unmatched_count": len(unmatched),
        "unmatched_sample": [(zi["key"], zi["title"][:60]) for zi in unmatched[:15]],
        "untagged_count": len(untagged),
        "pdf_coverage": {
            "with_pdf": len(papers_with_pdf),
            "without_pdf": len(papers_without_pdf),
            "total": len(vault_papers),
        },
        "missing_dois_written": len(missing_dois),
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(checks, zotero_result=None):
    """Generate Markdown report string."""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Vault Health Report ({now})\n")

    # -- Richness --
    if "richness" in checks:
        lines.append("## 筆記充實度\n")
        lines.append("| 域 | Stub | Thin | Basic | Rich | Total | Stub+Thin率 |")
        lines.append("|:--|:--|:--|:--|:--|:--|:--|")
        richness = checks["richness"]
        worst_domain = None
        worst_rate = 0
        for domain, dist in sorted(richness.items()):
            counts = {level: len(dist.get(level, [])) for level, _, _ in RICHNESS_LEVELS}
            total = sum(counts.values())
            if total == 0:
                continue
            st_rate = round(100 * (counts["stub"] + counts["thin"]) / total)
            lines.append(
                f"| {domain} | {counts['stub']} | {counts['thin']} | "
                f"{counts['basic']} | {counts['rich']} | {total} | {st_rate}% |"
            )
            if st_rate > worst_rate and total >= 5:
                worst_rate = st_rate
                worst_domain = domain
        lines.append("")
        if worst_domain:
            lines.append(
                f"> 建議：`python prepare_enrich_tasks.py --domain {worst_domain}`\n"
            )

    # -- Orphans --
    if "orphans" in checks:
        orphans = checks["orphans"]
        total_orphans = sum(len(v) for v in orphans.values())
        lines.append(f"## 孤兒概念（未被任何 MOC 收錄）\n")
        lines.append(f"共 **{total_orphans}** 個孤兒，按域分佈：\n")
        for domain, names in sorted(orphans.items(), key=lambda x: -len(x[1])):
            sample = ", ".join(names[:5])
            more = f" ...+{len(names)-5}" if len(names) > 5 else ""
            lines.append(f"- **{domain}**: {len(names)} 個（{sample}{more}）")
        lines.append("")

    # -- Broken links --
    if "broken_links" in checks:
        broken = checks["broken_links"]
        lines.append(f"## 壞連結\n")
        if broken:
            lines.append(f"共 **{len(broken)}** 個壞連結：\n")
            for target, sources in sorted(broken.items())[:30]:
                src_list = ", ".join(sources[:3])
                more = f" +{len(sources)-3}" if len(sources) > 3 else ""
                lines.append(f"- `[[{target}]]` ← {src_list}{more}")
            if len(broken) > 30:
                lines.append(f"\n（還有 {len(broken)-30} 個未列出）")
        else:
            lines.append("無壞連結。")
        lines.append("")

    # -- MOC coverage --
    if "moc_coverage" in checks:
        cov = checks["moc_coverage"]
        lines.append("## MOC 覆蓋率\n")
        lines.append("| 域 | Note 總數 | 被 MOC 收錄 | 覆蓋率 |")
        lines.append("|:--|:--|:--|:--|")
        for domain, info in sorted(cov.items()):
            lines.append(
                f"| {domain} | {info['total']} | {info['covered']} | {info['pct']}% |"
            )
        lines.append("")

    # -- AI-ENRICHED --
    if "ai_enriched" in checks:
        pending = checks["ai_enriched"]
        lines.append(f"## AI-ENRICHED 待審\n")
        if pending:
            lines.append(f"共 **{len(pending)}** 篇待審核：\n")
            for p in pending:
                lines.append(f"- {p}")
        else:
            lines.append("無待審筆記。")
        lines.append("")

    # -- Concept-Paper backlinks --
    if "concept_paper" in checks:
        cp = checks["concept_paper"]
        total = cp["with"] + cp["without"]
        lines.append(f"## 概念→論文反向連結\n")
        lines.append(
            f"- 有引用論文的概念筆記：{cp['with']}/{total} "
            f"({round(100*cp['with']/total) if total else 0}%)"
        )
        lines.append(f"- 無引用論文的概念筆記：{cp['without']}/{total}")
        if cp["examples"]:
            lines.append(f"- 範例：{', '.join(cp['examples'][:8])}")
        lines.append("")

    # -- Zotero --
    if zotero_result:
        zr = zotero_result
        lines.append("## Zotero-Vault 交叉比對\n")
        lines.append(
            f"- Zotero 文獻：**{zr['total_zotero']}** 篇 / "
            f"Vault 論文筆記：**{zr['total_vault']}** 篇 / "
            f"落差估計：**~{zr['unmatched_count']}** 篇"
        )
        lines.append(f"- 無 tag 文獻：**{zr['untagged_count']}** 篇")
        pdf_cov = zr["pdf_coverage"]
        lines.append(
            f"- PDF 覆蓋率：{pdf_cov['with_pdf']}/{pdf_cov['total']} "
            f"論文筆記有對應 PDF-raw"
        )
        if zr["unmatched_sample"]:
            lines.append(f"\n落差樣本（前 15 篇）：\n")
            for key, title in zr["unmatched_sample"]:
                lines.append(f"- [{key}] {title}")
        if zr["missing_dois_written"]:
            lines.append(
                f"\n> DOI 清單已輸出至 `vault_health_missing.txt`（{zr['missing_dois_written']} 篇）\n"
                f"> 建議：`python import_papers.py --file vault_health_missing.txt --pdf --dry-run`"
            )
        if zr["untagged_count"]:
            lines.append(
                f"\n> 建議：`python suggest_tags.py --untagged --dry-run`"
            )
        lines.append("")

    # -- Summary actions --
    lines.append("## 建議行動（按優先度）\n")
    actions = []

    if "ai_enriched" in checks and checks["ai_enriched"]:
        n = len(checks["ai_enriched"])
        actions.append(f"審核 {n} 篇 AI-ENRICHED 筆記（品質風險）")

    if "richness" in checks:
        for domain, dist in checks["richness"].items():
            stub_count = len(dist.get("stub", []))
            if stub_count >= 5:
                actions.append(
                    f"充實 {domain} {stub_count} 個 stub "
                    f"→ `python prepare_enrich_tasks.py --domain {domain}`"
                )

    if zotero_result and zotero_result["unmatched_count"] > 0:
        actions.append(
            f"補齊 ~{zotero_result['unmatched_count']} 篇 Zotero 落差論文 "
            f"→ `python import_papers.py --file vault_health_missing.txt --pdf --dry-run`"
        )

    if "orphans" in checks:
        total_orphans = sum(len(v) for v in checks["orphans"].values())
        if total_orphans > 0:
            actions.append(f"將 {total_orphans} 個孤兒概念收錄進 MOC")

    if "broken_links" in checks and checks["broken_links"]:
        actions.append(f"修正 {len(checks['broken_links'])} 個壞連結")

    for i, action in enumerate(actions, 1):
        lines.append(f"{i}. {action}")

    if not actions:
        lines.append("無需立即行動。")

    lines.append("")
    return "\n".join(lines)


def generate_summary(checks, zotero_result=None):
    """Generate a one-paragraph summary for session start."""
    parts = []

    if "richness" in checks:
        total_notes = sum(
            sum(len(v) for v in dist.values())
            for dist in checks["richness"].values()
        )
        total_stubs = sum(
            len(dist.get("stub", []))
            for dist in checks["richness"].values()
        )
        parts.append(f"{total_notes} 概念筆記（{total_stubs} stub）")

    if "orphans" in checks:
        total_orphans = sum(len(v) for v in checks["orphans"].values())
        parts.append(f"{total_orphans} 孤兒")

    if "broken_links" in checks:
        parts.append(f"{len(checks['broken_links'])} 壞連結")

    if "ai_enriched" in checks:
        parts.append(f"{len(checks['ai_enriched'])} 篇待審")

    if zotero_result:
        parts.append(f"Zotero 落差 ~{zotero_result['unmatched_count']} 篇")

    return "Vault 狀態：" + "；".join(parts) + "。"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Vault health diagnostic tool"
    )
    parser.add_argument("--zotero", action="store_true",
                        help="Include Zotero cross-check (requires network)")
    parser.add_argument("--orphans", action="store_true",
                        help="Only run orphan detection")
    parser.add_argument("--richness", action="store_true",
                        help="Only run richness stats")
    parser.add_argument("--broken-links", action="store_true",
                        help="Only run broken link scan")
    parser.add_argument("--summary", action="store_true",
                        help="Output one-line summary only")
    args = parser.parse_args()

    # Determine which checks to run
    specific = args.orphans or args.richness or args.broken_links
    run_all = not specific

    print("Scanning vault...")
    vault_index = build_vault_index()
    print(f"  Found {len(vault_index)} .md files in vault")

    checks = {}

    if run_all or args.richness:
        print("  Checking note richness...")
        checks["richness"] = check_richness()

    if run_all or args.orphans:
        print("  Checking orphan concepts...")
        checks["orphans"] = check_orphans()

    if run_all or args.broken_links:
        print("  Checking broken links...")
        checks["broken_links"] = check_broken_links(vault_index)

    if run_all:
        print("  Checking MOC coverage...")
        checks["moc_coverage"] = check_moc_coverage()

        print("  Checking AI-ENRICHED pending...")
        checks["ai_enriched"] = check_ai_enriched()

        print("  Checking concept-paper backlinks...")
        checks["concept_paper"] = check_concept_paper_backlinks()

    zotero_result = None
    if args.zotero:
        print("  Checking Zotero...")
        zotero_result = check_zotero()

    if args.summary:
        print(generate_summary(checks, zotero_result))
        return

    report = generate_report(checks, zotero_result)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport written to: {REPORT_FILE}")
    print(generate_summary(checks, zotero_result))


if __name__ == "__main__":
    main()
