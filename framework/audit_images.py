"""
Audit all images in the Obsidian vault.

Scans every Pic/ directory, PDF-assets/, and the vault root for image files.
Cross-references with ![[...]] embeds in all .md files to identify:
  - Referenced vs unreferenced images
  - Naming patterns (Pasted image / citekey_fig / descriptive / phenotyping / other)
  - Stray images outside of Pic/ directories
  - Double-extension issues

Outputs a structured report to OV-Papers/scripts/image_audit_report.md.

Usage:
    python audit_images.py              # Full audit
    python audit_images.py --unreferenced-only   # Only list unreferenced images
    python audit_images.py --domain OV-Docker     # Audit a single domain
"""
import argparse
import os
import re
from collections import defaultdict
from datetime import datetime

from config import VAULT_ROOT, OV_FOLDERS, PDF_ASSETS_DIR

# ── Image extensions ─────────────────────────────────────────
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"}

# ── Output ───────────────────────────────────────────────────
REPORT_FILE = os.path.join(
    VAULT_ROOT, "OV-Papers", "scripts", "image_audit_report.md"
)

# ── Naming pattern classifiers ───────────────────────────────
PASTED_RE = re.compile(r"^Pasted image \d{14}\.png$")
CITEKEY_FIG_RE = re.compile(r"^[a-z]+\d{4}[a-z]*_(?:fig|tab)\w*\.png$", re.I)
PHENO_OUTPUT_RE = re.compile(
    r"^\d{4}B?\d{0,2}[-_].*\d{8}[-_]\d{4,6}.*\.(jpg|png)$", re.I
)


def classify_name(filename: str) -> str:
    """Classify an image filename into a naming category."""
    if PASTED_RE.match(filename):
        return "Pasted image (無語意)"
    if CITEKEY_FIG_RE.match(filename):
        return "citekey_fig (論文圖表)"
    if PHENO_OUTPUT_RE.match(filename):
        return "phenotyping output"
    # Double extension
    base, ext = os.path.splitext(filename)
    if os.path.splitext(base)[1].lower() in IMAGE_EXTENSIONS:
        return "double extension ⚠️"
    # Has meaningful words (at least one letter segment > 2 chars)?
    if re.search(r"[a-zA-Z\u4e00-\u9fff]{3,}", base):
        return "descriptive"
    return "other"


# ── Scanning helpers ─────────────────────────────────────────


def find_images(root_dir: str, recursive: bool = False) -> list[dict]:
    """Return list of image info dicts under root_dir."""
    images = []
    if not os.path.isdir(root_dir):
        return images
    if recursive:
        for dirpath, _, filenames in os.walk(root_dir):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
                    full = os.path.join(dirpath, f)
                    images.append(
                        {
                            "filename": f,
                            "path": full,
                            "relpath": os.path.relpath(full, VAULT_ROOT),
                            "size": os.path.getsize(full),
                            "category": classify_name(f),
                        }
                    )
    else:
        for f in os.listdir(root_dir):
            full = os.path.join(root_dir, f)
            if os.path.isfile(full) and os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
                images.append(
                    {
                        "filename": f,
                        "path": full,
                        "relpath": os.path.relpath(full, VAULT_ROOT),
                        "size": os.path.getsize(full),
                        "category": classify_name(f),
                    }
                )
    return images


def find_all_references(domain_filter: str | None = None) -> dict[str, list[str]]:
    """
    Scan all .md files for ![[...]] image embeds.

    Returns {image_filename: [list of .md files that reference it]}.
    """
    # Handle both ![[file|size]] and ![[file\|size]] (escaped pipe in tables)
    embed_re = re.compile(r"!\[\[([^\]|\\]+?)(?:\\?\|[^\]]*?)?\]\]")
    refs: dict[str, list[str]] = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(VAULT_ROOT):
        # Skip hidden dirs, PDF-raw, PDF-assets, .obsidian
        base = os.path.basename(dirpath)
        if base.startswith(".") or base in ("PDF-raw", "PDF-assets", "__pycache__"):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            continue
        # Domain filter
        if domain_filter:
            rel = os.path.relpath(dirpath, VAULT_ROOT)
            top = rel.split(os.sep)[0]
            if top.startswith("OV-") and top != domain_filter:
                continue

        for f in filenames:
            if not f.endswith(".md"):
                continue
            md_path = os.path.join(dirpath, f)
            try:
                with open(md_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except (UnicodeDecodeError, PermissionError):
                continue
            for match in embed_re.finditer(content):
                ref_name = match.group(1).strip()
                # Obsidian ![[file]] uses just filename, no path
                refs[ref_name].append(os.path.relpath(md_path, VAULT_ROOT))
    return refs


# ── Report generation ────────────────────────────────────────


def generate_report(
    all_images: list[dict],
    references: dict[str, list[str]],
    root_images: list[dict],
) -> str:
    """Build the audit report as a markdown string."""
    lines = []
    w = lines.append

    ref_set = set(references.keys())

    # Mark each image as referenced or not
    for img in all_images:
        img["referenced"] = img["filename"] in ref_set
        img["referenced_by"] = references.get(img["filename"], [])

    total = len(all_images)
    referenced = sum(1 for i in all_images if i["referenced"])
    unreferenced = total - referenced
    total_size_mb = sum(i["size"] for i in all_images) / (1024 * 1024)

    # Category counts
    cat_counts: dict[str, int] = defaultdict(int)
    for img in all_images:
        cat_counts[img["category"]] += 1

    # ── Header ──
    w("# 圖片盤點報告")
    w("")
    w(f"> 產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    w(f"> 腳本：`audit_images.py`")
    w("")
    w("## 總覽")
    w("")
    w(f"| 指標 | 數值 |")
    w(f"|:--|:--|")
    w(f"| 圖片總數 | {total} |")
    w(f"| 被引用 | {referenced} |")
    w(f"| 未引用 | {unreferenced} |")
    w(f"| 總大小 | {total_size_mb:.1f} MB |")
    w("")

    # ── Category breakdown ──
    w("## 命名類型分佈")
    w("")
    w("| 類型 | 數量 | 佔比 |")
    w("|:--|:--|:--|")
    for cat in sorted(cat_counts, key=lambda c: -cat_counts[c]):
        pct = cat_counts[cat] / total * 100 if total else 0
        w(f"| {cat} | {cat_counts[cat]} | {pct:.0f}% |")
    w("")

    # ── Per-location breakdown ──
    w("## 各目錄明細")
    w("")

    # Group by directory
    by_dir: dict[str, list[dict]] = defaultdict(list)
    for img in all_images:
        parent = os.path.dirname(img["relpath"])
        by_dir[parent].append(img)

    for dir_path in sorted(by_dir.keys()):
        imgs = by_dir[dir_path]
        dir_ref = sum(1 for i in imgs if i["referenced"])
        dir_unref = len(imgs) - dir_ref
        dir_size = sum(i["size"] for i in imgs) / (1024 * 1024)
        w(f"### {dir_path or '(vault 根目錄)'}")
        w(f"- 圖片數：{len(imgs)}（引用 {dir_ref} / 未引用 {dir_unref}）")
        w(f"- 大小：{dir_size:.1f} MB")
        w("")

        # Show each image
        w("| 檔名 | 類型 | 大小 | 引用狀態 |")
        w("|:--|:--|:--|:--|")
        for img in sorted(imgs, key=lambda i: i["filename"]):
            size_kb = img["size"] / 1024
            ref_status = "✅ 被引用" if img["referenced"] else "❌ 未引用"
            if img["referenced_by"]:
                ref_by = ", ".join(img["referenced_by"][:3])
                if len(img["referenced_by"]) > 3:
                    ref_by += f" +{len(img['referenced_by'])-3}"
                ref_status += f" ({ref_by})"
            w(f"| `{img['filename']}` | {img['category']} | {size_kb:.0f} KB | {ref_status} |")
        w("")

    # ── Root stray images ──
    if root_images:
        w("## ⚠️ 根目錄散落圖片")
        w("")
        w(f"共 {len(root_images)} 張圖片在 vault 根目錄，建議移至對應 Pic/ 目錄。")
        w("")
        for img in root_images:
            w(f"- `{img['filename']}` ({img['size']/1024:.0f} KB) — {img['category']}")
        w("")

    # ── Double extension issues ──
    double_ext = [i for i in all_images if i["category"] == "double extension ⚠️"]
    if double_ext:
        w("## ⚠️ 雙重副檔名")
        w("")
        w("以下檔案有重複的副檔名（如 `.png.png`），建議修正：")
        w("")
        for img in double_ext:
            w(f"- `{img['relpath']}`")
        w("")

    # ── Unreferenced images ──
    unref = [i for i in all_images if not i["referenced"]]
    if unref:
        w("## 未引用圖片清單")
        w("")
        w(f"共 {len(unref)} 張圖片未被任何 .md 檔案引用。")
        w("可能是過時、冗餘，或僅透過外部方式使用。")
        w("")
        w("| 路徑 | 類型 | 大小 |")
        w("|:--|:--|:--|")
        for img in sorted(unref, key=lambda i: i["relpath"]):
            w(f"| `{img['relpath']}` | {img['category']} | {img['size']/1024:.0f} KB |")
        w("")

    # ── Naming convention reference ──
    w("## 命名規範建議")
    w("")
    w("| 類型 | 建議格式 | 範例 |")
    w("|:--|:--|:--|")
    w("| 論文圖表 | `{citekey}_fig{N}.png` | `cao2025blessing_fig1.png` |")
    w("| 領域截圖 | `{domain}_{topic}_{description}.png` | `docker_error_wsl2.png` |")
    w("| 表型資料 | `{batchID}_{sampleID}_{date}_{time}.jpg` | （維持現有格式） |")
    w("| 系統截圖 | `{system}_{description}.png` | `ubuntu_disk_space.png` |")
    w("")
    w("**漸進式重命名**：在 Obsidian 中按 F2 重命名圖片，會自動更新所有引用。")
    w("建議優先處理「Pasted image」類型中被引用的圖片（未引用的可暫時忽略或刪除）。")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Audit images in Obsidian vault")
    parser.add_argument(
        "--domain", help="Only audit a specific OV-* domain (e.g. OV-Docker)"
    )
    parser.add_argument(
        "--unreferenced-only",
        action="store_true",
        help="Only list unreferenced images",
    )
    args = parser.parse_args()

    all_images: list[dict] = []

    # 1. Scan Pic/ directories in each OV-* folder
    folders = OV_FOLDERS
    if args.domain:
        if args.domain not in OV_FOLDERS:
            print(f"Unknown domain: {args.domain}")
            print(f"Available: {', '.join(sorted(OV_FOLDERS))}")
            return
        folders = {args.domain: OV_FOLDERS[args.domain]}

    for name, folder_path in sorted(folders.items()):
        pic_dir = os.path.join(folder_path, "Pic")
        all_images.extend(find_images(pic_dir, recursive=False))

    # 2. Scan PDF-assets/
    if not args.domain or args.domain == "OV-Papers":
        all_images.extend(find_images(PDF_ASSETS_DIR, recursive=False))

    # 3. Scan vault root for stray images
    root_images = find_images(VAULT_ROOT, recursive=False)
    all_images.extend(root_images)

    print(f"Found {len(all_images)} images across vault")

    # 4. Scan all .md files for ![[...]] references
    print("Scanning markdown references...")
    references = find_all_references(domain_filter=args.domain)
    print(f"Found {len(references)} unique image references")

    # 5. Generate report
    report = generate_report(all_images, references, root_images)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    # Print summary
    referenced = sum(1 for i in all_images if i.get("referenced"))
    unreferenced = len(all_images) - referenced
    print(f"\nReport written to: {REPORT_FILE}")
    print(f"  Total: {len(all_images)}")
    print(f"  Referenced: {referenced}")
    print(f"  Unreferenced: {unreferenced}")

    # Category summary
    cats: dict[str, int] = defaultdict(int)
    for i in all_images:
        cats[i["category"]] += 1
    print("\nBy naming type:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        # Sanitize for Windows console encoding
        safe_cat = cat.encode("ascii", "replace").decode("ascii")
        print(f"  {safe_cat}: {count}")


if __name__ == "__main__":
    main()
