---
type: convention
rule_id: KB-DATA-001
applies_to: [all-agents]
triggers:
  - data-parse
keywords:
  - csv
  - yaml
  - json
enforcement: review
severity: error
status: active
---
# Use structured parsers for structured data

Use a parser that understands the data format. Do not split CSV on commas, edit YAML as arbitrary text, or infer JSON structure with regular expressions when a standard parser is available.
