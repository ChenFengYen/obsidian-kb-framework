---
type: convention
rule_id: KB-DATA-003
applies_to: [all-agents]
triggers:
  - data-archive
  - data-parse
keywords:
  - file-discovery
  - derived-output
  - rerun
  - pipeline
enforcement: review
severity: error
status: active
---
# Separate source and derived data

Source discovery must use explicit directories, manifests, or allowlisted patterns. Derived outputs must not be rediscovered as new inputs. Test reruns for idempotence and unexpected file-count growth.
