"""
Batch rename Pasted images and update all markdown references.

Finds each image file in the vault, renames it, and updates all
![[old name]] references (including size suffixes like |500) in .md files.

Usage:
    python rename_images.py --plan plan_file.txt        # Execute a rename plan
    python rename_images.py --plan plan_file.txt --dry   # Dry run (no changes)
"""
import argparse
import os
import re
import sys

VAULT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"}


def find_image(filename: str) -> str | None:
    """Find the full path of an image file in the vault."""
    for dirpath, _, filenames in os.walk(VAULT_ROOT):
        base = os.path.basename(dirpath)
        if base.startswith(".") or base in ("PDF-raw", "__pycache__"):
            continue
        if filename in filenames:
            return os.path.join(dirpath, filename)
    return None


def find_all_md_files() -> list[str]:
    """Find all .md files in the vault."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(VAULT_ROOT):
        base = os.path.basename(dirpath)
        if base.startswith(".") or base in ("PDF-raw", "__pycache__"):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            continue
        for f in filenames:
            if f.endswith(".md"):
                md_files.append(os.path.join(dirpath, f))
    return md_files


def update_references(
    md_files: list[str], old_name: str, new_name: str, dry: bool = False
) -> list[str]:
    """Update all ![[old_name]] references to ![[new_name]] in md files.

    Handles size suffixes like |500, |500x300, and escaped pipes like \\|500.
    Returns list of modified file paths.
    """
    # Match ![[old_name]] with optional |size or \|size suffix
    # The old_name may contain special regex chars (spaces, parens)
    escaped = re.escape(old_name)
    pattern = re.compile(
        r"(!\[\[)" + escaped + r"(\s*(?:\\?\|[^\]]*)?)\]\]"
    )
    modified = []

    for md_path in md_files:
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            continue

        new_content = pattern.sub(r"\g<1>" + new_name + r"\2]]", content)
        if new_content != content:
            rel = os.path.relpath(md_path, VAULT_ROOT)
            if dry:
                count = len(pattern.findall(content))
                safe_rel = rel.encode("ascii", "replace").decode("ascii")
                print(f"  Would update {count} ref(s) in {safe_rel}")
            else:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                count = len(pattern.findall(content))
                safe_rel = rel.encode("ascii", "replace").decode("ascii")
                print(f"  Updated {count} ref(s) in {safe_rel}")
            modified.append(rel)

    return modified


def parse_plan(plan_path: str) -> list[tuple[str, str]]:
    """Parse a rename plan file. Format: old_name -> new_name (one per line)."""
    pairs = []
    with open(plan_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if " -> " not in line:
                print(f"Skipping invalid line: {line}")
                continue
            old, new = line.split(" -> ", 1)
            pairs.append((old.strip(), new.strip()))
    return pairs


def main():
    parser = argparse.ArgumentParser(description="Batch rename images")
    parser.add_argument("--plan", required=True, help="Path to rename plan file")
    parser.add_argument(
        "--dry", action="store_true", help="Dry run (no actual changes)"
    )
    args = parser.parse_args()

    pairs = parse_plan(args.plan)
    if not pairs:
        print("No rename pairs found in plan file.")
        return

    print(f"{'[DRY RUN] ' if args.dry else ''}Processing {len(pairs)} renames...\n")

    md_files = find_all_md_files()
    print(f"Found {len(md_files)} markdown files to scan.\n")

    success = 0
    failed = 0

    for old_name, new_name in pairs:
        print(f"--- {old_name} -> {new_name}")

        # Find the image
        img_path = find_image(old_name)
        if not img_path:
            print(f"  ERROR: Image not found in vault!")
            failed += 1
            continue

        new_path = os.path.join(os.path.dirname(img_path), new_name)
        rel_old = os.path.relpath(img_path, VAULT_ROOT)

        if os.path.exists(new_path):
            print(f"  ERROR: Target already exists: {new_path}")
            failed += 1
            continue

        # Rename file
        if args.dry:
            print(f"  Would rename: {rel_old}")
        else:
            os.rename(img_path, new_path)
            print(f"  Renamed: {rel_old}")

        # Update references
        modified = update_references(md_files, old_name, new_name, dry=args.dry)
        if not modified:
            print(f"  (no markdown references found)")

        success += 1
        print()

    print(f"Done: {success} succeeded, {failed} failed.")


if __name__ == "__main__":
    main()
