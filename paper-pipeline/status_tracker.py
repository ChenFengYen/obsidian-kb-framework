"""
Parse and update OV-Papers/PDF_status.md tracking table.

Usage:
    python status_tracker.py              # Print summary
    python status_tracker.py --add-cols   # Add figures_extracted, links_injected columns
"""
import os
import re
import sys

from config import PDF_STATUS_FILE


def parse_status_table(filepath: str = PDF_STATUS_FILE) -> list[dict]:
    """Parse PDF_status.md markdown table into list of dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    rows = []
    headers = None
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if headers is None:
            # Normalize header names
            headers = []
            for h in cells:
                h_clean = h.strip().lower()
                if "index" in h_clean:
                    headers.append("index")
                elif "filename" in h_clean:
                    headers.append("pdf_filename")
                elif "type" in h_clean:
                    headers.append("type")
                elif "status" in h_clean and "human" not in h_clean:
                    headers.append("status")
                elif "human" in h_clean or "verified" in h_clean:
                    headers.append("verified")
                elif "figure" in h_clean:
                    headers.append("figures_extracted")
                elif "link" in h_clean:
                    headers.append("links_injected")
                else:
                    headers.append(h.strip())
            continue
        # Skip separator row
        if all(c.replace("-", "").replace(" ", "") == "" for c in cells):
            continue
        row = {}
        for i, h in enumerate(headers):
            row[h] = cells[i].strip() if i < len(cells) else ""
        rows.append(row)

    return rows


def get_paper_id(row: dict) -> str:
    """Extract paper ID (stem without .pdf) from a row."""
    return row.get("pdf_filename", "").replace(".pdf", "").strip()


def get_papers(
    status: str = None,
    verified: str = None,
    figures_extracted: str = None,
    links_injected: str = None,
    paper_type: str = None,
) -> list[dict]:
    """Filter papers by criteria."""
    rows = parse_status_table()
    result = []
    for row in rows:
        if status and status.lower() not in row.get("status", "").lower():
            continue
        if verified is not None:
            v = row.get("verified", "")
            if verified.lower() == "yes" and "[yes]" not in v.lower():
                continue
            if verified.lower() == "no" and "[no]" not in v.lower():
                continue
        if figures_extracted is not None:
            fe = row.get("figures_extracted", "")
            if figures_extracted.lower() not in fe.lower():
                continue
        if links_injected is not None:
            li = row.get("links_injected", "")
            if links_injected.lower() not in li.lower():
                continue
        if paper_type:
            t = row.get("type", "").lower()
            if paper_type.lower() not in t:
                continue
        result.append(row)
    return result


def get_priority_queue(rows: list[dict] = None) -> list[dict]:
    """Sort papers by priority tier for processing.

    Tier 1: importance >= 4 (need to read YAML from PDF-md)
    Tier 2: research or review type
    Tier 3: remaining, alphabetical
    Textbooks are last.
    """
    if rows is None:
        rows = get_papers(status="processed", verified="no")

    from config import PDF_MD_DIR
    import yaml

    scored = []
    for row in rows:
        paper_id = get_paper_id(row)
        ptype = row.get("type", "").lower()
        importance = 3  # default

        # Try to read importance from YAML frontmatter
        md_path = os.path.join(PDF_MD_DIR, f"{paper_id}.md")
        if os.path.exists(md_path):
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.startswith("---"):
                    end = content.index("---", 3)
                    fm = yaml.safe_load(content[3:end])
                    if fm and "rating" in fm and "importance" in fm["rating"]:
                        importance = int(fm["rating"]["importance"])
            except Exception:
                pass

        # Tier scoring
        if importance >= 4:
            tier = 1
        elif "research" in ptype or "review" in ptype:
            tier = 2
        elif "textbook" in ptype:
            tier = 4
        else:
            tier = 3

        scored.append((tier, -importance, paper_id, row))

    scored.sort(key=lambda x: (x[0], x[1], x[2]))
    return [item[3] for item in scored]


def add_tracking_columns():
    """Add figures_extracted and links_injected columns to PDF_status.md."""
    with open(PDF_STATUS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if columns already exist
    if "figures_extracted" in content.lower() or "links_injected" in content.lower():
        print("[status_tracker] Tracking columns already exist.")
        return

    lines = content.split("\n")
    new_lines = []
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            new_lines.append(line)
            continue

        cells = line.split("|")
        # Header row
        if i == 0 or (
            "index" in line.lower() and "filename" in line.lower()
        ):
            # Find the position — insert before the closing |
            new_lines.append(
                line.rstrip()
                + " figures_extracted | links_injected |"
            )
        # Separator row
        elif all(
            c.replace("-", "").replace(" ", "") == ""
            for c in line.split("|")[1:-1]
            if c.strip()
        ):
            new_lines.append(line.rstrip() + " --- | --- |")
        # Data rows
        else:
            new_lines.append(line.rstrip() + " [no] | [no] |")

    with open(PDF_STATUS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print("[status_tracker] Added figures_extracted and links_injected columns.")


def update_paper_status(paper_id: str, **kwargs):
    """Update specific columns for a paper in PDF_status.md.

    kwargs can include: figures_extracted, links_injected, verified
    """
    with open(PDF_STATUS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filename = f"{paper_id}.pdf"
    new_lines = []
    updated = False

    # First, identify column positions from header
    headers = []
    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "filename" in line.lower():
            header_idx = i
            headers = [c.strip().lower() for c in line.split("|")[1:-1]]
            break

    col_map = {}
    for idx, h in enumerate(headers):
        if "index" in h:
            col_map["index"] = idx
        elif "filename" in h:
            col_map["pdf_filename"] = idx
        elif "type" in h and "status" not in h:
            col_map["type"] = idx
        elif "status" in h and "human" not in h:
            col_map["status"] = idx
        elif "human" in h or "verified" in h:
            col_map["verified"] = idx
        elif "figure" in h:
            col_map["figures_extracted"] = idx
        elif "link" in h:
            col_map["links_injected"] = idx

    for line in lines:
        if filename in line and line.strip().startswith("|"):
            cells = line.split("|")
            # cells[0] is empty (before first |), cells[-1] is after last |
            inner = [c for c in cells[1:-1]]

            for key, value in kwargs.items():
                if key in col_map:
                    cidx = col_map[key]
                    if cidx < len(inner):
                        # Preserve spacing
                        old = inner[cidx]
                        padding = len(old) - len(old.lstrip())
                        inner[cidx] = " " * max(1, padding) + value + " "

            new_line = "|" + "|".join(inner) + "|\n"
            new_lines.append(new_line)
            updated = True
        else:
            new_lines.append(line)

    if updated:
        with open(PDF_STATUS_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return updated


if __name__ == "__main__":
    if "--add-cols" in sys.argv:
        add_tracking_columns()
    else:
        rows = parse_status_table()
        processed = [r for r in rows if "processed" in r.get("status", "").lower()
                      and "unprocessed" not in r.get("status", "").lower()]
        verified = [r for r in rows if "[yes]" in r.get("verified", "")]
        print(f"Total entries: {len(rows)}")
        print(f"Processed: {len(processed)}")
        print(f"Human verified: {len(verified)}")
        print(f"Pending review: {len(processed) - len(verified)}")

        # Show type distribution
        types = {}
        for r in rows:
            t = r.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        print("\nType distribution:")
        for t, c in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {t}: {c}")
