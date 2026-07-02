"""Shared configuration for an installed obsidian-kb-framework vault."""
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_vault_root():
    directory = _THIS_DIR
    for _ in range(5):
        if os.path.isfile(os.path.join(directory, "vault_config.yaml")):
            return directory
        directory = os.path.dirname(directory)
    return os.path.normpath(os.path.join(_THIS_DIR, os.pardir, os.pardir))


VAULT_ROOT = _find_vault_root()
_CONFIG = {}
_config_path = os.path.join(VAULT_ROOT, "vault_config.yaml")
if os.path.isfile(_config_path):
    try:
        import yaml
        with open(_config_path, "r", encoding="utf-8") as handle:
            _CONFIG = yaml.safe_load(handle) or {}
    except ImportError:
        print("Warning: pyyaml not installed. Using defaults.", file=sys.stderr)
    except Exception as exc:
        print(f"Warning: Failed to load vault_config.yaml: {exc}", file=sys.stderr)


def _cfg(key_path, default=None):
    value = _CONFIG
    for key in key_path.split("."):
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


PAPERS_ROOT = os.path.join(VAULT_ROOT, "OV-Papers")
PDF_RAW_DIR = os.path.join(PAPERS_ROOT, "PDF-raw")
PDF_MD_DIR = os.path.join(PAPERS_ROOT, "PDF-md")
FINAL_MD_DIR = os.path.join(PAPERS_ROOT, "Final-md")
PDF_ASSETS_DIR = os.path.join(PAPERS_ROOT, "PDF-assets")
SCRIPTS_DIR = os.path.join(PAPERS_ROOT, "scripts")
BACKUP_DIR = os.path.join(PDF_MD_DIR, ".backup")
PDF_STATUS_FILE = os.path.join(PAPERS_ROOT, "PDF_status.md")


def _build_ov_folders():
    domains = _cfg("domains", {})
    if domains:
        return {
            f"OV-{name}": os.path.join(VAULT_ROOT, f"OV-{name}")
            for name in domains
        }
    if not os.path.isdir(VAULT_ROOT):
        return {}
    return {
        name: os.path.join(VAULT_ROOT, name)
        for name in os.listdir(VAULT_ROOT)
        if name.startswith("OV-") and os.path.isdir(os.path.join(VAULT_ROOT, name))
    }


OV_FOLDERS = _build_ov_folders()
DEFAULT_DOMAIN = f"OV-{_cfg('default_domain', 'General')}"
SECTION_MARKERS = _cfg("section_markers", [])
FIGURES_SECTION = _cfg("figures_section", "## 圖表整理")

_figure = _cfg("figure_extraction", {})
MIN_FIGURE_WIDTH = _figure.get("min_width", 500)
PORTRAIT_ASPECT_RANGE = tuple(_figure.get("portrait_aspect_range", [0.7, 1.4]))
GRAPHICAL_ABSTRACT_MIN_WIDTH = _figure.get("graphical_abstract_min_width", 800)

_modules = _cfg("modules", {})
ZOTERO_ENABLED = bool(_modules.get("zotero", False))
PAPER_PIPELINE_ENABLED = bool(_modules.get("paper_pipeline", False))
LEARNING = _cfg("learning", {})
CAPTURE_MODE = _cfg("capture.mode", "inline+debrief")
PREFERENCES = _cfg("preferences", {})
USER_PROFILE = _cfg("user_profile", {})
