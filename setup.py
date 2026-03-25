#!/usr/bin/env python3
"""
Interactive setup script for obsidian-kb-framework.

Creates a new Obsidian vault with LYT structure, configured for
AI-assisted knowledge building.

Usage:
    python setup.py                     # Interactive mode
    python setup.py --config my.yaml    # Use existing config
    python setup.py --target ./my-vault # Specify output directory
"""
import argparse
import os
import shutil
import sys
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _input(prompt, default=None):
    """Prompt with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def _yes_no(prompt, default=True):
    """Yes/no prompt."""
    suffix = "[Y/n]" if default else "[y/N]"
    result = input(f"{prompt} {suffix}: ").strip().lower()
    if not result:
        return default
    return result in ("y", "yes")


def interactive_config():
    """Build vault_config.yaml through interactive prompts."""
    print("\n=== 知識庫建設框架 — 互動式設定 ===\n")

    vault_name = _input("知識庫名稱", "My Research KB")
    language = _input("語言 (zh-TW / en)", "zh-TW")

    # Domains
    print("\n--- 領域設定 ---")
    print("輸入你的研究/學習領域（每行一個，空行結束）：")
    print("格式：名稱, 描述, 關鍵字1;關鍵字2;...")
    print("範例：MachineLearning, 機器學習/電腦視覺, machine learning;deep learning;computer vision")
    print()

    domains = {}
    while True:
        line = input("> ").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split(",", 2)]
        if len(parts) < 2:
            print("  格式：名稱, 描述[, 關鍵字1;關鍵字2]")
            continue
        name = parts[0].replace(" ", "")
        desc = parts[1]
        keywords = [k.strip() for k in parts[2].split(";")] if len(parts) > 2 else []
        domains[name] = {"description": desc, "keywords": keywords}
        print(f"  [OK]OV-{name}")

    if not domains:
        print("至少需要一個領域。使用預設：General")
        domains = {"General": {"description": "General knowledge", "keywords": []}}

    default_domain = _input("預設領域", list(domains.keys())[0])

    # Learning
    print("\n--- 學習目標 ---")
    experience = _input("經驗等級 (beginner/intermediate/advanced)", "beginner")
    focus = _input("目前學習焦點（可留空）", "")

    print("輸入學習目標（每行一個，空行結束）：")
    goals = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        goals.append(line)

    # Modules
    print("\n--- 可選模組 ---")
    use_zotero = _yes_no("啟用 Zotero 文獻管理？", False)
    use_paper = _yes_no("啟用論文處理管線（PDF 圖表提取）？", False)

    # Capture mode
    print("\n--- 知識捕獲模式 ---")
    print("  1. debrief — 僅 session 結束時回顧")
    print("  2. inline+debrief — 對話中即時標示 + 結束回顧（推薦）")
    print("  3. journal+debrief — 建立探索日誌 + 結束回顧")
    capture = _input("選擇 (1/2/3)", "2")
    capture_map = {"1": "debrief", "2": "inline+debrief", "3": "journal+debrief"}
    capture_mode = capture_map.get(capture, "inline+debrief")

    # Build YAML
    config = {
        "vault_name": vault_name,
        "language": language,
        "domains": domains,
        "default_domain": default_domain,
        "section_markers": [
            "# 🧾 基本資訊", "# 🎯 研究主題與背景", "# 💡 創新與貢獻",
            "# 🔬 研究方法", "# 📊 結果", "# 🧠 討論",
            "# 🧩 補充分析", "# 🧭 與我的研究關聯",
        ] if language == "zh-TW" else [
            "# Background", "# Methods", "# Results",
            "# Discussion", "# Significance",
        ],
        "figures_section": "## 圖表整理" if language == "zh-TW" else "## Figures",
        "filtering": {
            "generic_blocklist": [],
            "boost_patterns": [],
            "alias_blocklist": [],
            "stem_blocklist": ["uv", "id", "ip", "os", "io"],
            "min_alias_length": 12,
        },
        "link_injection": {"scan_dirs": ["OV-Papers/PDF-md"]},
        "enrichment": {"style_reference": None, "target_level": "basic", "batch_size": 10},
        "capture": {"mode": capture_mode},
        "modules": {"zotero": use_zotero, "paper_pipeline": use_paper},
        "learning": {
            "goals": goals,
            "current_focus": focus,
            "experience_level": experience,
        },
        "user_profile": {"research_areas": [], "knowledge_gaps": []},
        "preferences": {
            "note_language": language,
            "moc_style": "narrative",
            "link_format": "citekey",
            "auto_rescan": True,
        },
    }

    return config


def write_yaml(config, path):
    """Write config dict to YAML file."""
    try:
        import yaml
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except ImportError:
        # Fallback: write minimal YAML manually
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"vault_name: \"{config['vault_name']}\"\n")
            f.write(f"language: \"{config['language']}\"\n")
            f.write(f"default_domain: \"{config['default_domain']}\"\n")
            f.write("domains:\n")
            for name, info in config["domains"].items():
                f.write(f"  {name}:\n")
                f.write(f"    description: \"{info['description']}\"\n")
                f.write(f"    keywords:\n")
                for kw in info.get("keywords", []):
                    f.write(f"      - \"{kw}\"\n")
            f.write(f"\ncapture:\n  mode: \"{config['capture']['mode']}\"\n")
            f.write(f"\nmodules:\n  zotero: {str(config['modules']['zotero']).lower()}\n")
            f.write(f"  paper_pipeline: {str(config['modules']['paper_pipeline']).lower()}\n")
            f.write(f"\nlearning:\n  experience_level: \"{config['learning']['experience_level']}\"\n")
            f.write(f"  current_focus: \"{config['learning']['current_focus']}\"\n")
            f.write(f"  goals:\n")
            for g in config["learning"]["goals"]:
                f.write(f"    - \"{g}\"\n")


def render_template(template_path, context):
    """Simple {{variable}} template rendering (no Jinja2 dependency)."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Handle simple {% if %} blocks (remove if condition is falsy)
    import re
    # Remove Jinja2 blocks for simplicity — just strip template tags
    content = re.sub(r"\{%.*?%\}\n?", "", content)
    # Replace {{ var }} with empty string (will be filled by AI agent)
    content = re.sub(r"\{\{.*?\}\}", "", content)
    return content


def create_vault(config, target_dir):
    """Create the vault directory structure and files."""
    print(f"\n=== 建立知識庫: {target_dir} ===\n")

    os.makedirs(target_dir, exist_ok=True)

    # Create domain directories
    for name in config["domains"]:
        for subdir in ("Map", "Note", "Pic"):
            path = os.path.join(target_dir, f"OV-{name}", subdir)
            os.makedirs(path, exist_ok=True)
            print(f"  [OK]OV-{name}/{subdir}/")

    # Create OV-Papers structure
    for subdir in ("PDF-md", "PDF-raw", "PDF-assets", "Final-md",
                    "Template", "scripts", "enrich-tasks"):
        os.makedirs(os.path.join(target_dir, "OV-Papers", subdir), exist_ok=True)
    print("  [OK]OV-Papers/ (with subdirectories)")

    # Write vault_config.yaml
    write_yaml(config, os.path.join(target_dir, "vault_config.yaml"))
    print("  [OK]vault_config.yaml")

    # Copy framework scripts
    fw_src = os.path.join(SCRIPT_DIR, "framework")
    fw_dst = os.path.join(target_dir, "OV-Papers", "scripts")
    for fname in os.listdir(fw_src):
        src = os.path.join(fw_src, fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(fw_dst, fname))
    print(f"  [OK]Copied {len(os.listdir(fw_src))} scripts to OV-Papers/scripts/")

    # Copy skills
    skills_src = os.path.join(SCRIPT_DIR, "prompts", "skills")
    skills_dst = os.path.join(target_dir, ".claude", "skills")
    if os.path.isdir(skills_src):
        shutil.copytree(skills_src, skills_dst, dirs_exist_ok=True)
        print(f"  [OK]Copied skills to .claude/skills/")

    # Copy settings
    settings_src = os.path.join(SCRIPT_DIR, "prompts", "settings.local.json")
    if os.path.isfile(settings_src):
        os.makedirs(os.path.join(target_dir, ".claude"), exist_ok=True)
        shutil.copy2(settings_src, os.path.join(target_dir, ".claude", "settings.local.json"))

    # Generate CLAUDE.md (simplified — just copy template for now, AI will customize)
    claude_src = os.path.join(SCRIPT_DIR, "prompts", "CLAUDE.md.j2")
    if os.path.isfile(claude_src):
        content = render_template(claude_src, config)
        with open(os.path.join(target_dir, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK]CLAUDE.md")

    # Generate Home.md
    home_content = f"# {config['vault_name']}\n\n"
    home_content += "## 知識領域\n\n"
    for name, info in config["domains"].items():
        home_content += f"[[{name}_MOC]] — {info['description']}\n"
    home_content += "\n## 工具\n\n"
    home_content += "- `/review-vault` — 檢查知識庫健康狀態\n"
    home_content += "- `/suggest-next` — AI 推薦下一步\n"
    home_content += "- `/onboard` — 新筆記入庫\n"
    with open(os.path.join(target_dir, "Home.md"), "w", encoding="utf-8") as f:
        f.write(home_content)
    print("  [OK]Home.md")

    # Generate MOC stubs
    for name, info in config["domains"].items():
        moc_content = f"# {name}\n\n"
        moc_content += f"<!-- {info['description']} 的內容地圖 -->\n\n"
        moc_content += "## 概覽\n\n（用你自己的話描述這個領域）\n\n"
        moc_content += "## 核心概念\n\n（按邏輯分組組織你學到的概念）\n\n"
        moc_content += "## 待釐清\n\n- （開放問題）\n"
        moc_path = os.path.join(target_dir, f"OV-{name}", "Map", f"{name}_MOC.md")
        with open(moc_path, "w", encoding="utf-8") as f:
            f.write(moc_content)
    print(f"  [OK]{len(config['domains'])} MOC stubs")

    # Generate .claudeignore
    ignore_content = "# Obsidian internal\n.obsidian/\n\n"
    ignore_content += "# Raw PDFs\nOV-Papers/PDF-raw/\n\n"
    ignore_content += "# Images\nOV-*/Pic/*.png\nOV-*/Pic/*.jpg\n\n"
    ignore_content += "# Git/Python\n.git/\n__pycache__/\n*.pyc\n"
    with open(os.path.join(target_dir, ".claudeignore"), "w", encoding="utf-8") as f:
        f.write(ignore_content)
    print("  [OK].claudeignore")

    # Generate empty enrich-inbox.md
    with open(os.path.join(target_dir, "OV-Papers", "enrich-inbox.md"), "w", encoding="utf-8") as f:
        f.write("# Concept Enrichment Queue\n\n<!-- QuickAdd 產生的概念筆記佇列 -->\n")
    print("  [OK]enrich-inbox.md")

    # Optional: copy paper-pipeline
    if config["modules"].get("paper_pipeline"):
        pp_src = os.path.join(SCRIPT_DIR, "paper-pipeline")
        if os.path.isdir(pp_src):
            for fname in os.listdir(pp_src):
                src = os.path.join(pp_src, fname)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(fw_dst, fname))
            print("  [OK]Paper pipeline scripts copied")

    # Optional: copy zotero-tools
    if config["modules"].get("zotero"):
        zt_src = os.path.join(SCRIPT_DIR, "zotero-tools")
        zt_dst = os.path.join(target_dir, "zotero-tools")
        if os.path.isdir(zt_src):
            shutil.copytree(zt_src, zt_dst, dirs_exist_ok=True)
            print("  [OK]Zotero tools copied")

    # Copy docs
    docs_src = os.path.join(SCRIPT_DIR, "docs")
    docs_dst = os.path.join(target_dir, "OV-Papers")
    for fname in ("NOTE_TEMPLATES.md", "PIPELINE_OPS_GUIDE.md", "SCRIPTS_REFERENCE.md"):
        src = os.path.join(docs_src, fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(docs_dst, fname))

    print(f"\n=== 完成！===")
    print(f"\n下一步：")
    print(f"  1. 用 Obsidian 開啟 {target_dir}")
    print(f"  2. 在該目錄啟動 AI 代理（如 claude）")
    print(f"  3. 輸入 /init-domain 讓 AI 引導你開始建設知識庫")
    print(f"  4. 或直接開始提問，AI 會在問題驅動模式中幫你建立筆記")


def main():
    parser = argparse.ArgumentParser(description="Setup a new knowledge base vault")
    parser.add_argument("--config", help="Path to existing vault_config.yaml")
    parser.add_argument("--target", help="Target directory for the vault")
    args = parser.parse_args()

    if args.config:
        import yaml
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        config = interactive_config()

    target = args.target or _input("\n輸出目錄", "./my-knowledge-base")
    target = os.path.abspath(target)

    if os.path.exists(target) and os.listdir(target):
        if not _yes_no(f"目錄 {target} 已存在且非空，繼續？", False):
            print("取消。")
            return

    create_vault(config, target)


if __name__ == "__main__":
    main()
