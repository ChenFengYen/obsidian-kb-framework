"""
Find missing concept candidates that should become new stub notes.

Sources (ranked by confidence):
1. YAML keywords — curated per-paper, highest confidence
2. Bold terms with English/acronyms — specific named methods/models
3. Existing [[red links]] in Final-md files

Filters:
- Generic activity/descriptor terms are excluded
- Terms appearing in >15% of papers are penalized
- Plant physiology terms are boosted (user knowledge gap)

Usage:
    python extract_candidates.py                  # Generate candidates_review.md
    python extract_candidates.py --min-refs 2     # Min 2 paper references
    python extract_candidates.py --keywords-only  # Only YAML keywords (high confidence)
"""
import argparse
import os
import re
import yaml
from collections import defaultdict
from datetime import datetime

from config import (
    PDF_MD_DIR,
    FINAL_MD_DIR,
    CANDIDATES_REVIEW_FILE,
    DOMAIN_MAP,
    DEFAULT_DOMAIN,
    GENERIC_BLOCKLIST,
    BOOST_PATTERNS,
)
from concept_index import build_concept_index


# GENERIC_BLOCKLIST and BOOST_PATTERNS are loaded from vault_config.yaml via config.py
# See vault_config.yaml.example for reference values.


def _is_boosted_term(term: str) -> bool:
    """Check if a term matches any boost patterns from config."""
    lower = term.lower()
    return any(pat in lower for pat in BOOST_PATTERNS)


def _is_specific_term(term: str) -> bool:
    """Check if a bold term is specific enough to be a concept note.

    Specific terms typically contain:
    - English acronyms/abbreviations (SAM, YOLO, FPN, NDVI)
    - Named methods/models (ResNet, Mask R-CNN)
    - English technical terms in parentheses
    - Known measurement units or indices
    """
    # Contains uppercase acronym (2+ consecutive uppercase letters)
    if re.search(r"[A-Z]{2,}", term):
        return True
    # Contains English technical term in parentheses
    if re.search(r"[（(][A-Za-z]", term):
        return True
    # Is primarily English (named model/method)
    ascii_ratio = sum(1 for c in term if c.isascii() and c.isalpha()) / max(len(term), 1)
    if ascii_ratio > 0.6 and len(term) >= 3:
        return True
    # Plant physiology terms are always interesting
    if _is_boosted_term(term):
        return True
    return False


def _read_yaml_frontmatter(filepath: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return {}

    if not content.startswith("---"):
        return {}
    try:
        end = content.index("---", 3)
        return yaml.safe_load(content[3:end]) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def _extract_bold_terms(filepath: str) -> list[str]:
    """Extract specific **bold terms** from markdown body.

    Only keeps terms that pass the specificity filter:
    - Contains English acronyms/names
    - Is a plant physiology term
    - Contains parenthetical English translation
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    # Skip frontmatter
    if content.startswith("---"):
        try:
            end = content.index("---", 3)
            content = content[end + 3:]
        except ValueError:
            pass

    # Template section labels
    template_labels = {
        "文章標題 title", "作者 authors", "年份 year", "期刊 journal",
        "期刊點數 / 影響因子 if", "出版社 publisher", "出版社所在地 country/region",
        "資料來源 source", "文章類型 article type", "領域分類 field/category",
        "自動分類 domains", "關鍵詞 keywords",
        "重要度 importance", "方法品質 method quality",
        "實際應用性 applicability", "可讀性 readability",
        "主要研究議題 main research question", "研究背景 background",
        "重要已有研究 prior studies", "知識缺口 knowledge gap",
        "研究動機 motivation", "創新點 innovations",
        "與過往方法差異 differences from previous work",
        "作者聲稱的主要貢獻 claimed contributions",
        "研究設計 research design", "材料 / 數據來源 materials / data source",
        "使用技術 / 模型 / 儀器 tools / models / instruments",
        "參數設定 parameters", "分析流程 workflow",
        "結果詮釋 interpretation of results",
        "與先前研究比較 comparison with previous studies",
        "優勢 strengths", "限制 limitations",
        "是否達成研究目的 fulfillment of objectives",
        "未來研究方向 future work", "作者提出 author suggestions",
        "個人建議 my suggestions",
        "方法描述是否充分？", "是否提供程式碼/資料集？",
        "可重現性 reproducibility", "潛在偏誤 bias / limitations",
        "實務應用性 practical applications",
    }

    terms = []
    for m in re.finditer(r"\*\*([^*]+?)\*\*", content):
        term = m.group(1).strip()
        if len(term) <= 2 or len(term) >= 60 or "\n" in term:
            continue
        if term.lower().strip() in template_labels:
            continue
        # Skip template artifacts and figure/table refs
        if any(term.startswith(p) for p in [
            "圖 ", "圖1", "圖2", "圖3", "圖4", "圖5", "圖6", "圖7", "圖8", "圖9",
            "表 ", "表1", "表2", "表3", "表4", "表5",
            "Fig", "Table", "✔", "✗", "❌",
            "DOI", "doi",
        ]):
            continue
        # Skip figure references like "圖1 (Figure 1)"
        if re.match(r"^圖\d", term) or re.match(r"^表\d", term):
            continue
        # Only keep specific terms
        if _is_specific_term(term):
            terms.append(term)

    return terms


def _extract_red_links(filepath: str) -> list[str]:
    """Extract [[links]] from a file, to check which are 'red' (non-existent)."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    links = []
    for m in re.finditer(r"\[\[([^|\]]+?)(?:\|[^\]]+?)?\]\]", content):
        link = m.group(1).strip()
        if link and not link.endswith(".png") and not link.endswith(".pdf"):
            links.append(link)

    return links


def _guess_domain(paper_fm: dict) -> str:
    """Guess the target OV-* domain from a paper's frontmatter fields."""
    fields = []
    if "field" in paper_fm:
        f = paper_fm["field"]
        if isinstance(f, list):
            fields.extend(f)
        elif isinstance(f, str):
            fields.append(f)

    for field in fields:
        key = field.lower().strip()
        if key in DOMAIN_MAP:
            return DOMAIN_MAP[key]

    keywords = paper_fm.get("keywords", [])
    if isinstance(keywords, list):
        for kw in keywords:
            if isinstance(kw, str):
                key = kw.lower().strip()
                if key in DOMAIN_MAP:
                    return DOMAIN_MAP[key]

    return DEFAULT_DOMAIN


def find_candidates(min_refs: int = 1, keywords_only: bool = False) -> dict:
    """Find concept candidates not in the existing index.

    Returns dict with structure:
    {term: {count, papers, avg_importance, suggested_domain, source, is_boosted}}
    """
    index = build_concept_index()
    existing_notes = set(index["notes"].keys())
    existing_aliases = set(index["alias_map"].keys())
    all_known = existing_notes | existing_aliases

    # Track sources separately
    candidates = defaultdict(lambda: {
        "count": 0,
        "papers": [],
        "importances": [],
        "domains": [],
        "source": set(),  # "keyword", "bold", "red_link"
    })

    total_papers = 0

    # Scan all PDF-md files
    for fname in os.listdir(PDF_MD_DIR):
        if not fname.endswith(".md"):
            continue
        total_papers += 1
        paper_id = fname[:-3]
        filepath = os.path.join(PDF_MD_DIR, fname)
        fm = _read_yaml_frontmatter(filepath)

        importance = 3
        if "rating" in fm and isinstance(fm["rating"], dict):
            try:
                importance = int(fm["rating"].get("importance", 3))
            except (ValueError, TypeError):
                importance = 3

        domain = _guess_domain(fm)

        # Source 1: YAML keywords (high confidence)
        keywords = fm.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                if not kw or not isinstance(kw, str):
                    continue
                norm = kw.lower().strip()
                if norm not in all_known and len(kw) > 2:
                    candidates[kw]["count"] += 1
                    candidates[kw]["papers"].append(paper_id)
                    candidates[kw]["importances"].append(importance)
                    candidates[kw]["domains"].append(domain)
                    candidates[kw]["source"].add("keyword")

        # Source 2: Specific bold terms (only if not keywords-only mode)
        if not keywords_only:
            bold_terms = _extract_bold_terms(filepath)
            for term in bold_terms:
                norm = term.lower().strip()
                if norm not in all_known and len(term) > 2:
                    if paper_id not in candidates[term].get("papers", []):
                        candidates[term]["count"] += 1
                        candidates[term]["papers"].append(paper_id)
                        candidates[term]["importances"].append(importance)
                        candidates[term]["domains"].append(domain)
                        candidates[term]["source"].add("bold")

    # Source 3: Red links from Final-md
    if not keywords_only and os.path.isdir(FINAL_MD_DIR):
        for fname in os.listdir(FINAL_MD_DIR):
            if not fname.endswith(".md"):
                continue
            paper_id = fname[:-3]
            filepath = os.path.join(FINAL_MD_DIR, fname)
            links = _extract_red_links(filepath)
            for link in links:
                norm = link.lower().strip()
                if norm not in all_known:
                    if paper_id not in candidates[link].get("papers", []):
                        candidates[link]["count"] += 1
                        candidates[link]["papers"].append(paper_id)
                        candidates[link]["importances"].append(3)
                        candidates[link]["domains"].append(DEFAULT_DOMAIN)
                        candidates[link]["source"].add("red_link")

    # Filter, score, and classify
    generic_threshold = max(3, total_papers * 0.15)  # >15% papers = too generic
    result = {}

    for term, info in candidates.items():
        if info["count"] < min_refs:
            continue

        # Skip blocklisted generic terms
        if term.lower().strip() in {g.lower() for g in GENERIC_BLOCKLIST}:
            continue

        # Penalize terms appearing in too many papers (likely generic)
        is_too_common = info["count"] > generic_threshold

        avg_imp = (
            sum(info["importances"]) / len(info["importances"])
            if info["importances"]
            else 3
        )

        # Scoring with source weighting
        source_bonus = 1.0
        if "keyword" in info["source"]:
            source_bonus = 1.5  # Keywords are curated, higher trust
        if "red_link" in info["source"]:
            source_bonus = max(source_bonus, 1.3)  # Red links = user intent

        is_boosted = _is_boosted_term(term)
        boost_bonus = 1.5 if is_boosted else 1.0

        # Penalize overly common terms
        commonality_penalty = 0.5 if is_too_common else 1.0

        score = info["count"] * avg_imp * source_bonus * boost_bonus * commonality_penalty

        # Determine suggested domain — physio terms → OV-Bioinformatics
        domain_counts = defaultdict(int)
        for d in info["domains"]:
            domain_counts[d] += 1
        suggested_domain = max(domain_counts, key=domain_counts.get)
        if is_boosted and suggested_domain == DEFAULT_DOMAIN:
            suggested_domain = "OV-Bioinformatics"

        result[term] = {
            "count": info["count"],
            "papers": info["papers"],
            "avg_importance": round(avg_imp, 1),
            "score": round(score, 1),
            "suggested_domain": suggested_domain,
            "source": sorted(info["source"]),
            "is_boosted": is_boosted,
            "is_too_common": is_too_common,
        }

    return result


def generate_candidates_report(candidates: dict):
    """Generate candidates_review.md organized by category."""
    lines = [
        f"# Proposed Concept Stubs - {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "> [!important] 人工審核",
        "> 勾選要建立的概念筆記，然後執行 `python create_stubs.py` 來建立。",
        "> 未勾選的項目會被跳過。",
        "",
        "---",
        "",
    ]

    # Separate by category
    physio = {t: c for t, c in candidates.items() if c["is_boosted"]}
    kw_only = {
        t: c for t, c in candidates.items()
        if not c["is_boosted"] and "keyword" in c["source"]
    }
    bold_only = {
        t: c for t, c in candidates.items()
        if not c["is_boosted"] and "keyword" not in c["source"]
    }

    def _render_section(title: str, items: dict, show_source: bool = False):
        if not items:
            return
        sorted_items = sorted(items.items(), key=lambda x: -x[1]["score"])
        lines.append(f"## {title} ({len(items)})")
        lines.append("")
        for term, info in sorted_items:
            domain = info["suggested_domain"]
            src = ", ".join(info["source"])
            papers_str = ", ".join(f"[[{p}]]" for p in info["papers"][:5])
            if len(info["papers"]) > 5:
                papers_str += f" +{len(info['papers'])-5} more"

            tag = ""
            if info.get("is_too_common"):
                tag = " ⚠️ generic"

            source_tag = f" [{src}]" if show_source else ""

            lines.append(
                f"- [ ] \"{term}\" → {domain}/Note/"
                f" ({info['count']} papers, imp {info['avg_importance']}){source_tag}{tag}"
            )
            lines.append(f"  - Papers: {papers_str}")
        lines.append("")

    _render_section(
        "🌱 Plant Physiology / Biology (知識補強重點)",
        physio,
        show_source=True,
    )
    _render_section(
        "🔑 High-Confidence Keywords (from YAML)",
        kw_only,
        show_source=False,
    )
    _render_section(
        "📝 From Paper Content (bold terms / red links)",
        bold_only,
        show_source=True,
    )

    lines.extend([
        "---",
        "",
        f"Total candidates: {len(candidates)}",
        f"Plant physiology: {len(physio)}",
        f"YAML keywords: {len(kw_only)}",
        f"Bold/red links: {len(bold_only)}",
    ])

    with open(CANDIDATES_REVIEW_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[extract_candidates] Report saved to {CANDIDATES_REVIEW_FILE}")
    print(f"  Total: {len(candidates)}")
    print(f"  Plant physiology: {len(physio)}")
    print(f"  YAML keywords: {len(kw_only)}")
    print(f"  Bold/red links: {len(bold_only)}")


def main():
    parser = argparse.ArgumentParser(description="Find missing concept candidates")
    parser.add_argument("--min-refs", type=int, default=1)
    parser.add_argument(
        "--keywords-only",
        action="store_true",
        help="Only use YAML keywords (highest confidence)",
    )
    args = parser.parse_args()

    candidates = find_candidates(
        min_refs=args.min_refs,
        keywords_only=args.keywords_only,
    )
    generate_candidates_report(candidates)


if __name__ == "__main__":
    main()
