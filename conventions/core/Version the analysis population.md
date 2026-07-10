---
type: convention
rule_id: KB-DATA-002
scope: [data-analysis, experiment-provenance]
applies_to: [all-agents]
triggers: [cohort, inclusion, exclusion, control, comparison]
enforcement: review
severity: error
status: active
---
# Version the analysis population

Define the analysis population before computation. Record inclusion and exclusion criteria, control or reference samples, dataset version, and expected counts. Validate actual counts before producing comparisons.
