---
type: convention
rule_id: KB-ENCODING-001
applies_to: [all-agents]
triggers:
  - cjk-text
  - destructive-op
keywords:
  - windows
  - utf-8
  - non-ascii
  - markdown-edit
enforcement: lint
severity: error
status: active
---
# Windows UTF-8 file safety

Use explicit UTF-8 for terminal output and file I/O. Prefer patches for focused Markdown edits. After bulk edits, inspect the diff and scan for replacement characters, private-use characters, and mojibake.
