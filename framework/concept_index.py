"""
Build and cache a concept note registry from all OV-*/Note/ folders.

Usage:
    python concept_index.py          # Build/refresh concept_index.json
    python concept_index.py --force  # Force rebuild (ignore cache)
"""
import json
import os
import re
import sys
from pathlib import Path

from config import (
    OV_FOLDERS, CONCEPT_INDEX_CACHE, VAULT_ROOT,
    STEM_BLOCKLIST, ALIAS_BLOCKLIST, MIN_ALIAS_LENGTHGTH,
)


def _extract_aliases(note_path: str) -> list[str]:
    """Extract potential aliases from a note's content.

    Looks for:
    - Parenthetical English terms: 中文名（English Term）
    - Bold terms in first few lines: **term**
    - Known abbreviation patterns: YOLO, CNN, etc.
    """
    aliases = []
    try:
        with open(note_path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # Only scan first 2000 chars
    except (OSError, UnicodeDecodeError):
        return aliases

    # Stopwords: too generic to be useful as aliases
    stopwords = {
        "the", "a", "an", "and", "or", "of", "in", "on", "at", "to",
        "for", "is", "it", "by", "as", "with", "from", "not", "no",
        "yes", "all", "any", "can", "may", "will", "has", "had",
        "get", "set", "new", "old", "one", "two", "use", "see",
        "e.g", "i.e", "etc", "fig", "tab", "ref", "eq",
    }

    # Pattern: 中文（English） or 中文 (English)
    for m in re.finditer(r"[（(]([A-Za-z][\w\s\-/.]+?)[）)]", content):
        term = m.group(1).strip()
        # Require minimum 5 chars, max 50 chars for English aliases
        if 5 <= len(term) <= 50:
            if term.lower() not in stopwords:
                aliases.append(term)

    # Pattern: **bold term** in early content (first 500 chars)
    early = content[:500]
    for m in re.finditer(r"\*\*(.+?)\*\*", early):
        term = m.group(1).strip()
        # Require 5-50 chars, no punctuation (skip sentences)
        if 5 <= len(term) <= 50 and "。" not in term and "，" not in term:
            if term.lower() not in stopwords:
                aliases.append(term)

    return aliases


def build_concept_index(force: bool = False) -> dict:
    """Scan all OV-*/Note/ folders and build concept registry.

    Returns dict with structure:
    {
        "notes": {
            "normalized_stem": {
                "stem": "Original Stem",
                "path": "relative/path/from/vault",
                "domain": "OV-FolderName",
                "aliases": ["alias1", "alias2"]
            }
        },
        "alias_map": {
            "normalized_alias": "normalized_stem"
        }
    }
    """
    # Check cache
    if not force and os.path.exists(CONCEPT_INDEX_CACHE):
        cache_mtime = os.path.getmtime(CONCEPT_INDEX_CACHE)
        # Check if any Note folder has newer files
        needs_refresh = False
        for folder_name, folder_path in OV_FOLDERS.items():
            note_dir = os.path.join(folder_path, "Note")
            if not os.path.isdir(note_dir):
                continue
            for fname in os.listdir(note_dir):
                fpath = os.path.join(note_dir, fname)
                if os.path.getmtime(fpath) > cache_mtime:
                    needs_refresh = True
                    break
            if needs_refresh:
                break

        if not needs_refresh:
            with open(CONCEPT_INDEX_CACHE, "r", encoding="utf-8") as f:
                print(f"[concept_index] Using cached index: {CONCEPT_INDEX_CACHE}")
                return json.load(f)

    print("[concept_index] Building concept index...")
    notes = {}
    alias_map = {}

    for folder_name, folder_path in OV_FOLDERS.items():
        note_dir = os.path.join(folder_path, "Note")
        if not os.path.isdir(note_dir):
            continue

        for fname in os.listdir(note_dir):
            if not fname.endswith(".md"):
                continue
            stem = fname[:-3]  # Remove .md
            norm = stem.lower().strip()
            rel_path = os.path.relpath(
                os.path.join(note_dir, fname), VAULT_ROOT
            ).replace("\\", "/")

            note_path = os.path.join(note_dir, fname)
            aliases = _extract_aliases(note_path)

            notes[norm] = {
                "stem": stem,
                "path": rel_path,
                "domain": folder_name,
                "aliases": aliases,
            }

            # Register aliases
            for alias in aliases:
                alias_norm = alias.lower().strip()
                if alias_norm != norm and alias_norm not in alias_map:
                    alias_map[alias_norm] = norm

    index = {"notes": notes, "alias_map": alias_map}

    # Cache to JSON
    os.makedirs(os.path.dirname(CONCEPT_INDEX_CACHE), exist_ok=True)
    with open(CONCEPT_INDEX_CACHE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    total_notes = len(notes)
    total_aliases = len(alias_map)
    print(f"[concept_index] Indexed {total_notes} notes, {total_aliases} aliases")
    print(f"[concept_index] Saved to {CONCEPT_INDEX_CACHE}")
    return index


def get_matching_terms(index: dict) -> list[tuple[str, str]]:
    """Return list of (match_term, note_stem) sorted longest-first.

    This is used by inject_links.py to match concepts in paper text.
    Longest-first ensures "Segment Anything Model" matches before "Segment".
    """
    # STEM_BLOCKLIST, ALIAS_BLOCKLIST, MIN_ALIAS_LENGTHGTH loaded from config.
    # See vault_config.yaml.example for reference values.
    MIN_ENGLISH_LEN = 3   # For pure-ASCII note stems (structural, not domain-specific)

    terms = []

    for norm, info in index["notes"].items():
        stem = info["stem"]

        # Skip note stems that are too short or generic
        if stem.lower() in STEM_BLOCKLIST:
            continue
        # For pure ASCII stems, require minimum length
        if stem.isascii() and len(stem) < MIN_ENGLISH_LEN:
            continue

        terms.append((stem, stem))

        # Add aliases (with stricter filtering)
        for alias in info["aliases"]:
            if alias.lower() in ALIAS_BLOCKLIST:
                continue
            if alias.isascii() and len(alias) < MIN_ALIAS_LENGTH:
                continue
            terms.append((alias, stem))

    # Sort by length descending (longest match first)
    terms.sort(key=lambda x: len(x[0]), reverse=True)
    return terms


if __name__ == "__main__":
    force = "--force" in sys.argv
    index = build_concept_index(force=force)
    print(f"\nDomains covered:")
    domain_counts = {}
    for info in index["notes"].values():
        d = info["domain"]
        domain_counts[d] = domain_counts.get(d, 0) + 1
    for d, c in sorted(domain_counts.items()):
        print(f"  {d}: {c} notes")
