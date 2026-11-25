# Note templates

Templates are starting points, not completeness checklists. Keep only sections that help the concept.

## Concept note

```markdown
# Concept name

## Definition and boundary

Explain what the concept is, what it is not, and how it differs from nearby concepts.

## Key relationships

Describe meaningful links in sentences.

## Evidence or examples

Record traceable support and uncertainty when relevant.

## Open questions

- Add questions that can guide future work.
```

## MOC

```markdown
# Domain name

Orient the reader to the domain and the perspective of this vault.

## Relationship group

Explain why the linked concepts belong together and how they interact.

## Current focus

Describe the active learning, research, or application angle.

## Open questions

- Add unresolved questions.
```

## Experiment record

When the research pack is enabled, include question, experimental unit, data and protocol versions, groups, inclusion rules, methods, environment, run identifier, outputs, and deviations.

## Organization or team note

Use at **L3 (Organizations & People)** only for groups or organizations that recur across sources or involve direct interaction. Keep synthesis hand-written and let queries pull matching L2 sources automatically.

```markdown
---
type: organization
entity: Canonical Organization Name
entity_id: "optional external ID (e.g., ROR or org URL)"
up:
  - "[[Relevant Domain MOC]]"
related:
  - "[[Relevant Project or Concept]]"
---

One-paragraph orientation: what this group is known for and why it matters to this vault.

## Core workstreams

Explain the main lines of work and how they connect, citing L2 sources as evidence.

## Overlap with my work

Note which tools, standards, datasets, or ideas intersect with active projects.

## Key people and roles

| Person | Focus / workstream | Notable outputs | Notes |
|---|---|---|---|
| Name | Role or line of work | [[source-key]] | Current affiliation or context |

## Interaction log

- YYYY-MM-DD — Meeting, visit, or discussion summary and follow-ups.

## Related sources in this vault

Query L2 sources whose frontmatter `organizations` (or `institutions`) list contains the canonical name above.
```

## Canonical entity lookup table

Pair L3 notes with a single lookup table so L2 source frontmatter stays consistent across renames, sub-units, and automated backfills. Store plain canonical names in source frontmatter (block lists, not wikilinks), and keep identifier mappings in the table:

```yaml
# Example snippet in an L2 source note's frontmatter
organizations:
  - "Canonical Organization Name"
regions:
  - "DE"
```

Include two tables in the lookup file:

1. **Canonical entities**: `Canonical name | Primary ID | Legacy / merged IDs | Aliases | Region | Notes` — set the granularity rule explicitly (typically top-level independent organization; record departments or sub-labs in the source body).
2. **Ignore list**: `External ID | Common raw label | Category | Condition | Reason` — record recurring false positives (such as research park names, funders, or redundant parent umbrellas) so automated or agent-assisted backfills converge over time instead of repeating the same cleanup.
