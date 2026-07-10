---
type: convention
rule_id: KB-FRONTMATTER-001
scope: [vault-writing]
applies_to: [all-agents]
triggers: [frontmatter, yaml, metadata]
enforcement: lint
severity: error
status: active
---
# Frontmatter remains structured

Use valid YAML and stable field types. Represent unknown scalar values as `null`, lists as YAML lists, and quoted wikilinks as strings. Validate metadata after automated edits.
