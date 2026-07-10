# Setup

## Requirements

- Python 3.10 or newer
- PyYAML
- Obsidian
- A terminal AI agent with filesystem access

## Generate a vault

```bash
pip install -r requirements.txt
python setup.py --config vault_config.yaml.example --target ./my-knowledge-base
```

The target must be empty. The generator creates domains, `Home.md`, `AGENTS.md`, selected Conventions, thin adapters, core skills, and tools.

## Verify the result

```bash
cd my-knowledge-base
python tools/validate_conventions.py --root OV-KnowledgeBase/Convention
python tools/vault_health.py --summary
```

No tool-specific permissions are installed. Configure permissions locally according to the agent and operating environment.

## Modules

Enable modules in `vault_config.yaml` before generation. Zotero and paper processing create `OV-Papers`; v2 does not install automatic link, stub, or batch-enrichment scripts.

Existing vaults should adopt v2 manually: add `AGENTS.md`, select Conventions, and validate behavior before changing established paths.
