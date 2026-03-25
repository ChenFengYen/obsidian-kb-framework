"""
Configuration loader for obsidian-kb-framework.

Reads vault_config.yaml from the vault root directory.
All other scripts import from this module — the public interface
(OV_FOLDERS, DOMAIN_MAP, SECTION_MARKERS, etc.) is unchanged.
"""
import os
import sys

# ── Locate vault root ─────────────────────────────────────────
# The framework/ directory sits inside OV-Papers/scripts/ (installed vault)
# or directly under the framework repo. Walk up until we find vault_config.yaml.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_vault_root():
    """Walk up from script dir to find vault_config.yaml."""
    d = _THIS_DIR
    for _ in range(5):  # max 5 levels up
        if os.path.isfile(os.path.join(d, "vault_config.yaml")):
            return d
        d = os.path.dirname(d)
    # Fallback: assume parent of parent (original OV-Papers/scripts layout)
    return os.path.normpath(os.path.join(_THIS_DIR, os.pardir, os.pardir))

VAULT_ROOT = _find_vault_root()

# ── Load YAML config ──────────────────────────────────────────
_CONFIG = {}
_config_path = os.path.join(VAULT_ROOT, "vault_config.yaml")

if os.path.isfile(_config_path):
    try:
        import yaml
        with open(_config_path, "r", encoding="utf-8") as f:
            _CONFIG = yaml.safe_load(f) or {}
    except ImportError:
        print("Warning: pyyaml not installed. Using default config.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to load vault_config.yaml: {e}", file=sys.stderr)


def _cfg(key_path: str, default=None):
    """Get nested config value by dot-separated path. e.g. 'filtering.min_alias_length'"""
    keys = key_path.split(".")
    val = _CONFIG
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val


# ── OV-Papers paths ──────────────────────────────────────────
PAPERS_ROOT = os.path.join(VAULT_ROOT, "OV-Papers")
PDF_RAW_DIR = os.path.join(PAPERS_ROOT, "PDF-raw")
PDF_MD_DIR = os.path.join(PAPERS_ROOT, "PDF-md")
FINAL_MD_DIR = os.path.join(PAPERS_ROOT, "Final-md")
PDF_ASSETS_DIR = os.path.join(PAPERS_ROOT, "PDF-assets")
SCRIPTS_DIR = os.path.join(PAPERS_ROOT, "scripts")
TEMPLATE_DIR = os.path.join(PAPERS_ROOT, "Template", "ParsePDF")

PDF_STATUS_FILE = os.path.join(PAPERS_ROOT, "PDF_status.md")
CONCEPT_INDEX_CACHE = os.path.join(SCRIPTS_DIR, "concept_index.json")

BACKUP_DIR = os.path.join(PDF_MD_DIR, ".backup")

REVIEW_QUEUE_FILE = os.path.join(PAPERS_ROOT, "review_queue.md")
CANDIDATES_REVIEW_FILE = os.path.join(PAPERS_ROOT, "candidates_review.md")
LINK_REPORT_FILE = os.path.join(PAPERS_ROOT, "link_report.md")

# ── Domain folders (from YAML or fallback) ────────────────────
def _build_ov_folders():
    domains = _cfg("domains", {})
    if domains:
        return {
            f"OV-{name}": os.path.join(VAULT_ROOT, f"OV-{name}")
            for name in domains
        }
    # Fallback: scan filesystem for OV-* directories
    folders = {}
    if os.path.isdir(VAULT_ROOT):
        for entry in os.listdir(VAULT_ROOT):
            if entry.startswith("OV-") and os.path.isdir(os.path.join(VAULT_ROOT, entry)):
                folders[entry] = os.path.join(VAULT_ROOT, entry)
    return folders

OV_FOLDERS = _build_ov_folders()

# ── Domain routing map (from YAML or fallback) ────────────────
def _build_domain_map():
    domains = _cfg("domains", {})
    dmap = {}
    for name, info in domains.items():
        if isinstance(info, dict):
            for kw in info.get("keywords", []):
                dmap[kw.lower()] = f"OV-{name}"
    return dmap

DOMAIN_MAP = _build_domain_map()
DEFAULT_DOMAIN = f"OV-{_cfg('default_domain', 'MachineLearning')}"

# ── Section markers ───────────────────────────────────────────
SECTION_MARKERS = _cfg("section_markers", [
    "# 🧾 基本資訊",
    "# 🎯 研究主題與背景",
    "# 💡 創新與貢獻",
    "# 🔬 研究方法",
    "# 📊 結果",
    "# 🧠 討論",
    "# 🧩 補充分析",
    "# 🧭 與我的研究關聯",
])

FIGURES_SECTION = _cfg("figures_section", "## 圖表整理")

# ── Figure extraction settings ────────────────────────────────
_fig = _cfg("figure_extraction", {})
MIN_FIGURE_WIDTH = _fig.get("min_width", 500) if isinstance(_fig, dict) else 500
_par = _fig.get("portrait_aspect_range", [0.7, 1.4]) if isinstance(_fig, dict) else [0.7, 1.4]
PORTRAIT_ASPECT_RANGE = tuple(_par)
GRAPHICAL_ABSTRACT_MIN_WIDTH = _fig.get("graphical_abstract_min_width", 800) if isinstance(_fig, dict) else 800

# ── Filtering lists (from YAML or fallback) ───────────────────
_filt = _cfg("filtering", {})

GENERIC_BLOCKLIST = set(_filt.get("generic_blocklist", [])) if isinstance(_filt, dict) else set()
BOOST_PATTERNS = _filt.get("boost_patterns", []) if isinstance(_filt, dict) else []
ALIAS_BLOCKLIST = set(_filt.get("alias_blocklist", [])) if isinstance(_filt, dict) else set()
STEM_BLOCKLIST = set(_filt.get("stem_blocklist", ["uv", "id", "ip", "os", "io"])) if isinstance(_filt, dict) else set()
MIN_ALIAS_LENGTH = _filt.get("min_alias_length", 12) if isinstance(_filt, dict) else 12

# ── Link injection settings ───────────────────────────────────
_link = _cfg("link_injection", {})
SCAN_DIRS = _link.get("scan_dirs", ["OV-Papers/PDF-md"]) if isinstance(_link, dict) else ["OV-Papers/PDF-md"]

# ── Enrichment settings ───────────────────────────────────────
_enrich = _cfg("enrichment", {})
_style_ref = _enrich.get("style_reference") if isinstance(_enrich, dict) else None
STYLE_REFERENCE_NOTE = os.path.join(VAULT_ROOT, _style_ref) if _style_ref else None
ENRICHMENT_TARGET = _enrich.get("target_level", "basic") if isinstance(_enrich, dict) else "basic"
BATCH_SIZE = _enrich.get("batch_size", 10) if isinstance(_enrich, dict) else 10

# ── Tasks directory ───────────────────────────────────────────
TASKS_DIR = os.path.join(PAPERS_ROOT, "enrich-tasks")

# ── Module flags ──────────────────────────────────────────────
_modules = _cfg("modules", {})
ZOTERO_ENABLED = _modules.get("zotero", False) if isinstance(_modules, dict) else False
PAPER_PIPELINE_ENABLED = _modules.get("paper_pipeline", False) if isinstance(_modules, dict) else False

# ── Learning & capture config (read by AI agent prompts) ──────
LEARNING = _cfg("learning", {})
CAPTURE_MODE = _cfg("capture.mode", "inline+debrief")
PREFERENCES = _cfg("preferences", {})
USER_PROFILE = _cfg("user_profile", {})
