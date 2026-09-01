---
type: convention
rule_id: KB-OUTPUT-001
applies_to: [all-agents]
triggers:
  - version-control
  - kb-access
keywords:
  - generated-output
  - analysis-script
  - temporary-file
enforcement: path-check
severity: error
status: active
---
# Separate temporary work from durable knowledge

Keep proposals, patches, review tables, one-off scripts, and unreviewed generated output outside the vault. Add only durable knowledge and reviewed results to the vault.
