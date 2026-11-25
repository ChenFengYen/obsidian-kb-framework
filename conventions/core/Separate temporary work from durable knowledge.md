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
  - data-table
enforcement: path-check
severity: error
status: active
---
# Separate temporary work from durable knowledge

Keep proposals, patches, review tables, one-off scripts, and unreviewed generated output outside the vault. Add only durable knowledge and reviewed results to the vault. **Data tables never go into the vault.**

## Where a data table goes

| Table | Default location | Rule |
|---|---|---|
| An intermediate table the agent produced - filtered, merged, summary statistics | the platform's scratch directory | moved to the project working directory only once the user decides to keep it |
| A table the user compiled or collected from outside | the project's working directory, outside the vault | the user decides where; the agent never copies it into the vault |
| Inside a note | an excerpted Markdown table only | with its sampling basis and the path of the full table |

**A note never cites a path in the scratch directory.** Scratch is cleared on reboot or routine cleanup, and the citation dies with it. Once a note needs a table, move the table to the working directory first.

## Why notes and tables stay apart

A note needs the excerpt that carries one argument, not the whole table. Coupling the two costs three things:

- In a vault that syncs through version control, every regeneration of a large table becomes a commit in everyone's history.
- The table separates from the script that produced it, so a reader gets the numbers without the basis.
- A table kept in both the project and the vault will drift.

The only exception is a user who explicitly asks, in the current request, for a table to be written into the vault.
