# obsidian-kb-framework

A portable framework for building an Obsidian knowledge base with terminal AI agents.

The framework treats agent collaboration rules as a product surface. It separates trusted agent instructions, reusable Conventions, ordinary knowledge notes, and mechanical validation.

Chinese version: [README.md](README.md)

## Design

```text
AGENTS.md                    trusted bootstrap and safety contract
        |
        +-- Convention packs    reusable rules, rationale, scope, exceptions
        +-- skills              task workflows
        +-- tools               health and graph analysis
        |
Home -> MOCs -> Notes        user knowledge network
```

Ordinary notes and imported sources are knowledge data, not instructions. The default workflow is question-driven: search the vault, synthesize an answer, identify gaps, and propose focused updates.

## Portable Defaults

- Cross-agent `AGENTS.md` bootstrap
- Thin adapters for Claude, Gemini, and legacy tools
- Core and Obsidian Convention packs
- Deliberate links instead of keyword-based link injection
- Note quality based on clarity, evidence, relationships, and discoverability
- Proposal-first batch, destructive, and published changes
- No personal paths, domain-specific priorities, or tool permissions in generated vaults

## Quick Start

```bash
git clone https://github.com/ChenFengYen/obsidian-kb-framework.git
cd obsidian-kb-framework
pip install -r requirements.txt
python setup.py --config vault_config.yaml.example --target ./my-knowledge-base
```

Open the generated directory as an Obsidian vault and start a terminal AI agent there. Agents that support `AGENTS.md` read it directly; generated adapters route other tools to the same contract.

## Convention Packs

| Pack | Purpose | Default |
|---|---|---|
| `core` | collaboration safety, provenance, data boundaries, AI verification | yes |
| `obsidian` | link and frontmatter integrity | yes |
| `research` | experiment specifications and evidence strength | optional |
| `windows-zh-tw` | Windows UTF-8 and non-ASCII file safety | optional |

Select packs in `vault_config.yaml`:

```yaml
conventions:
  packs:
    - core
    - obsidian
    - research
```

## Optional Modules

`zotero` and `paper_pipeline` are optional. The v1 automatic link, stub, and batch-enrichment tools are not installed by v2.

## Validation

```bash
python framework/validate_conventions.py --root conventions
python -m unittest discover -s tests -v
```

The tests generate clean General and Neuroscience vaults, validate Convention metadata, check module boundaries, and scan generated output for private or domain-specific leakage.

## Documentation

- [Setup](docs/SETUP.md)
- [Agent architecture](docs/AI_AGENT_GUIDE.md)
- [Methodology](docs/METHODOLOGY.md)
- [Customization](docs/CUSTOMIZATION.md)

## License

MIT
