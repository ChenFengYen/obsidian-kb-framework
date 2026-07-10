---
type: convention
rule_id: KB-LINK-001
scope: [vault-writing]
applies_to: [all-agents]
triggers: [wikilink, rename, link-repair]
enforcement: lint
severity: error
status: active
---
# Obsidian link safety

Create links that the vault can resolve. Do not add the `.md` suffix or link to external agent memory. Understand context before repairing links, and validate broken-link counts after changes.
