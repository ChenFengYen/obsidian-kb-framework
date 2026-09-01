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
python tools/validate_conventions.py --root KnowledgeBase/Convention
python tools/vault_health.py --summary
```

The Convention check reads `KnowledgeBase/Convention/registry.md`, which the
generator installs next to the Conventions themselves. It is an ordinary note,
so you can open it in the vault; it is also the authority the validator reads.
The check rejects a `rule_id` that is not registered, and — with
`--strict-registry` — a registered id marked `shipped` that no note claims, or a
rule name whose `[[ ]]` link does not match the note claiming the id. Domain
rules use their own reserved prefix; declare it in the registry before writing
the first one.

The only dependency is PyYAML, which is not in the standard library. Which
interpreter can run these scripts is therefore a property of the machine, not of
the vault: stopping at `ModuleNotFoundError: No module named 'yaml'` means the
wrong interpreter, not a broken rule set.

No tool-specific permissions are installed. Configure permissions locally according to the agent and operating environment.

## Modules

Enable modules in `vault_config.yaml` before generation. Zotero and paper processing create `Papers`; v2 does not install automatic link, stub, or batch-enrichment scripts.

Existing vaults should adopt v2 manually: add `AGENTS.md`, select Conventions, and validate behavior before changing established paths.
