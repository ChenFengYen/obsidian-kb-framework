---
type: convention
rule_id: KB-EVIDENCE-004
applies_to: [all-agents]
triggers:
  - claim-writing
  - note-write
keywords:
  - ai-generated-field
  - citation
  - formula
  - identifier
enforcement: review
severity: error
status: active
---
# AI generated fields require verification

AI-proposed citations, identifiers, formulas, and factual metadata remain unverified until checked against an authoritative source. Store verification state explicitly and never let placeholder completeness imply trust.
