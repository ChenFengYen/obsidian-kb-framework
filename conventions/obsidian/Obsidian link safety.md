---
type: convention
rule_id: KB-LINK-001
applies_to: [all-agents]
triggers:
  - wikilink
keywords:
  - rename
  - link-repair
enforcement: lint
severity: error
status: active
---
# Obsidian link safety

Create links that the vault can resolve. Do not add the `.md` suffix or link to external agent memory. Understand context before repairing links, and validate broken-link counts after changes.
