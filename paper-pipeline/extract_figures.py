"""
Batch extract figures from PDF files into PDF-assets/.

Usage:
    python extract_figures.py                    # Process next 10 unprocessed papers
    python extract_figures.py --batch-size 5     # Process 5 papers
    python extract_figures.py --paper-id NAME    # Process single paper
    python extract_figures.py --dry-run          # Preview without extracting
"""
import argparse
import io
import json
import os
import sys

from config import (
    PDF_RAW_DIR,
    PDF_ASSETS_DIR,
    PDF_MD_DIR,
    MIN_FIGURE_WIDTH,
    PORTRAIT_ASPECT_RANGE,
)
from status_tracker import (
    get_papers,
    get_paper_id,
    get_priority_queue,
    update_paper_status,
)


def extract_figures_from_pdf(paper_id: str, dry_run: bool = False) -> dict:
    """Extract figures from a single PDF.

    Returns manifest dict with extraction results.
    """
    try:
        import fitz
        from PIL import Image
    except ImportError as e:
        print(f"[extract_figures] Missing dependency: {e}")
        print("  Install with: pip install pymupdf pillow")
        sys.exit(1)

    pdf_path = os.path.join(PDF_RAW_DIR, f"{paper_id}.pdf")
    if not os.path.exists(pdf_path):
        print(f"  [SKIP] PDF not found: {pdf_path}")
        return {"paper_id": paper_id, "status": "pdf_not_found", "total_figures": 0, "figures": []}

    # Check if figures already extracted
    existing = [
        f
        for f in os.listdir(PDF_ASSETS_DIR)
        if f.startswith(f"{paper_id}_fig") and f.endswith(".png")
    ]
    if existing:
        print(f"  [SKIP] {len(existing)} figures already exist for {paper_id}")
        return {
            "paper_id": paper_id,
            "status": "already_extracted",
            "total_figures": len(existing),
            "figures": existing,
        }

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # Phase 1: Scan all images and count dimension signatures
    # Images that appear on many pages with identical dimensions are likely
    # decorative elements (headers, footers, watermarks), not figures.
    dim_page_count = {}  # (w, h) -> set of pages
    all_candidates = []  # (page_idx, xref, w, h)
    seen_xrefs = set()  # Deduplicate by xref (same image reused across pages)

    for page_idx, page in enumerate(doc):
        images = page.get_images(full=True)
        for img_info in images:
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            w = base_image["width"]
            h = base_image["height"]

            # Skip small images
            if w < MIN_FIGURE_WIDTH:
                continue

            # Skip author portraits on last 2 pages
            is_last_pages = page_idx >= total_pages - 2
            aspect = w / h if h > 0 else 0
            if (
                is_last_pages
                and w < MIN_FIGURE_WIDTH
                and PORTRAIT_ASPECT_RANGE[0] < aspect < PORTRAIT_ASPECT_RANGE[1]
            ):
                continue

            # Skip duplicate xrefs (same embedded image object)
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            dim_key = (w, h)
            dim_page_count.setdefault(dim_key, set()).add(page_idx)
            all_candidates.append((page_idx, xref, w, h))

    # Phase 2: Filter out repeated decorative images
    # If images with the same dimensions appear on > 40% of pages, skip them
    repeat_threshold = max(3, total_pages * 0.4)
    repeated_dims = {
        dim for dim, pages in dim_page_count.items()
        if len(pages) > repeat_threshold
    }
    if repeated_dims:
        print(f"  Skipping {len(repeated_dims)} repeated image dimension(s)")

    # Phase 3: Extract filtered figures
    fig_num = 0
    figures = []

    for page_idx, xref, w, h in all_candidates:
        if (w, h) in repeated_dims:
            continue

        fig_num += 1
        filename = f"{paper_id}_fig{fig_num}.png"
        filepath = os.path.join(PDF_ASSETS_DIR, filename)
        aspect = w / h if h > 0 else 0

        fig_entry = {
            "filename": filename,
            "page": page_idx + 1,
            "width": w,
            "height": h,
            "aspect": round(aspect, 2),
        }
        figures.append(fig_entry)

        if not dry_run:
            base_image = doc.extract_image(xref)
            img_data = base_image["image"]
            pil_img = Image.open(io.BytesIO(img_data))
            pil_img.save(filepath, "PNG")
            print(f"  Extracted: {filename} (page {page_idx+1}, {w}x{h})")
        else:
            print(f"  [DRY-RUN] Would extract: {filename} (page {page_idx+1}, {w}x{h})")

    doc.close()

    manifest = {
        "paper_id": paper_id,
        "status": "extracted" if not dry_run else "dry_run",
        "total_figures": fig_num,
        "figures": figures,
    }

    # Save manifest
    if not dry_run and figures:
        manifest_path = os.path.join(PDF_ASSETS_DIR, f"{paper_id}_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Batch extract figures from PDFs")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--paper-id", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.makedirs(PDF_ASSETS_DIR, exist_ok=True)

    if args.paper_id:
        # Single paper mode
        print(f"[extract_figures] Processing: {args.paper_id}")
        result = extract_figures_from_pdf(args.paper_id, dry_run=args.dry_run)
        print(f"  Result: {result['total_figures']} figures")
        return

    # Batch mode — get papers that need figure extraction
    papers = get_papers(status="processed", verified="no")
    queue = get_priority_queue(papers)

    # Filter: skip papers that already have figures
    to_process = []
    for row in queue:
        pid = get_paper_id(row)
        if not pid:
            continue
        # Skip if figures already exist in PDF-assets
        existing = [
            f
            for f in os.listdir(PDF_ASSETS_DIR)
            if f.startswith(f"{pid}_fig") and f.endswith(".png")
        ]
        if existing:
            continue
        # Skip if no PDF exists
        if not os.path.exists(os.path.join(PDF_RAW_DIR, f"{pid}.pdf")):
            continue
        # Skip textbooks initially
        if "textbook" in row.get("type", "").lower():
            continue
        to_process.append(row)

    batch = to_process[: args.batch_size]
    print(f"[extract_figures] Processing {len(batch)} of {len(to_process)} pending papers")
    print()

    results = []
    for row in batch:
        pid = get_paper_id(row)
        print(f"Processing: {pid}")
        result = extract_figures_from_pdf(pid, dry_run=args.dry_run)
        results.append(result)

        # Update status tracker
        if not args.dry_run and result["status"] == "extracted":
            update_paper_status(pid, figures_extracted="[yes]")

        print()

    # Summary
    total_figs = sum(r.get("total_figures", 0) for r in results)
    extracted = [r for r in results if r["status"] == "extracted"]
    print(f"[extract_figures] Done. Extracted {total_figs} figures from {len(extracted)} papers.")


if __name__ == "__main__":
    main()
