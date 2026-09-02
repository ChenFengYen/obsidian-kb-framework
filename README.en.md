# obsidian-kb-framework

A portable framework for building an Obsidian knowledge base with terminal AI agents.

The framework treats agent collaboration rules as a product surface. It separates trusted agent instructions, reusable Conventions, ordinary knowledge notes, and mechanical validation.

Chinese version: [README.md](README.md)

## Design

This repository is a template, not a knowledge base. `setup.py` reads
`vault_config.yaml` and generates a vault that can be version-controlled on its
own. Files exist on both sides, but they do different jobs.

```text
obsidian-kb-framework/                     the template; not anyone's vault
|
+-- AGENTS.md                              rules for an agent changing the framework
+-- setup_v2.py                            the generator; it renders the vault's AGENTS.md
+-- prompts/
|   +-- CLAUDE.md GEMINI.md AgentRules.md  thin adapters, copied verbatim into the vault
|   +-- skills/                            init-domain review-vault suggest-next debrief
+-- conventions/
|   +-- registry.md                        sole authority for KB-* ids and triggers
|   +-- core/ obsidian/                    default packs
|   +-- research/ windows-zh-tw/           optional packs
+-- framework/                             validate_conventions vault_health note_graph
+-- paper-pipeline/ zotero-tools/          optional modules, off by default
+-- templates/ examples/ docs/ tests/
        |
        |   python setup.py                vault_config.yaml decides what is installed
        v
your-vault/                                the product; its own git repository
|
+-- AGENTS.md                              startup authority, the only full rule set
+-- CLAUDE.md GEMINI.md AgentRules.md      thin adapters; Codex reads AGENTS.md itself
+-- vault_config.yaml
+-- Home.md
+-- <Domain>/
|   +-- Map/ Note/ Pic/                    Map holds <Domain>_MOC.md
+-- KnowledgeBase/
|   +-- Convention/                        rules from the selected packs, plus registry.md
|   +-- Map/                               Knowledge Base Conventions.md
+-- tools/                                 copied from framework/
+-- .claude/skills/
+-- Papers/                                created only with zotero or paper_pipeline on
    +-- PDF-raw/ PDF-md/ Final-md/ PDF-assets/ scripts/
```

**No single filename is read by every agent**, so the full rule set lives in
`AGENTS.md` alone and everything else is a thin adapter. An adapter that starts
holding rules of its own has become a second source of truth.

The two `AGENTS.md` files are different documents for different jobs. The one at
the repository root addresses whoever changes the framework. The one in a vault
is *rendered* by `setup_v2.py` from `vault_config.yaml` — which packs and modules
are enabled decides which rows the task-routing table gains. It is not a copy of
a template file, so changing the generated rules means changing the generator.

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
