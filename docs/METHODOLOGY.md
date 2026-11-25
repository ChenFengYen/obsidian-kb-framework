# Methodology

## Knowledge network

The vault uses `Home -> MOCs -> Notes` as a navigation pattern. Folders provide ownership and tooling boundaries; deliberate links express relationships.

A MOC explains how concepts relate, where the user enters the topic, and which questions remain open. It is not an alphabetical directory.

## Progressive integration levels

`Home -> MOCs -> Notes` describes spatial navigation. As a vault matures, notes also fall into four functional integration levels. Introduce later levels only when the volume of notes justifies them:

| Level | Tracks | Core question | Linking and storage pattern |
|---|---|---|---|
| **L1 Concepts & Methods** | Ideas, principles, techniques, tools, terms | What is this, and how does it work? | Atomic notes + deliberate wikilinks + topic MOCs |
| **L2 Sources & Artifacts** | Books, articles, specs, courses, case studies, experiment or test records | What is the evidence, and under what boundary conditions? | Structured source notes with stable keys (e.g., citekey, URL, run ID) linked to L1 |
| **L3 Organizations & People** | Teams, institutions, communities, maintainers, authors, collaborators | Who produced this, what is their trajectory, and where do we overlap? | **Data layer + thinking layer split** (see below): structured metadata on L2 sources, selective promotion to L3 notes |
| **L4 Decisions & Projects** | Project goals, trade-offs, design choices, open questions | Which option should I choose next, and why was this decided? | Project MOCs + comparison or decision notes citing L1-L3 without duplicating raw facts |

The same four levels apply across domains:

| Level | Academic research | Software & engineering | General learning & practice |
|---|---|---|---|
| **L1 Concepts & Methods** | Theories, metrics, algorithms | Protocols, architecture patterns, toolchains | Mental models, workflows, methods |
| **L2 Sources & Artifacts** | Papers, textbooks, experiment logs | RFCs, documentation, benchmarks, postmortems | Books, course notes, industry reports |
| **L3 Organizations & People** | Research groups, institutes, scholars (DOI / ROR / ORCID) | Open-source orgs, core teams, vendors (GitHub org / domain) | Authors, practitioners, communities, partners |
| **L4 Decisions & Projects** | Research gaps, study design, manuscript strategy | ADRs, technical selection, roadmaps | Project plans, action items, retrospectives |

### Separating data layer from thinking layer at L3

Not every level should use the same linking mechanism. Turning every author, company, or institution mentioned in L2 sources into a wikilink creates thousands of broken links or empty stubs, and plain name strings collide across people and renamed organizations.

Handle L3 in two layers instead:

1. **Data layer (on L2 sources)**: store normalized organization or team names in source frontmatter as plain YAML lists (not wikilinks), backed by a single **canonical entity lookup table** that maps aliases, renamed or merged entities, and stable external IDs (such as ROR, ORCID, or organization URLs) while filtering non-entity noise (such as campus names or funders misparsed as affiliations).
2. **Thinking layer (selective L3 notes)**: create an Organization / Team note (or a Person note for direct collaborators) only when repeated citations or real interactions make that entity worth tracking. Keep hand-written synthesis in the upper half (workstreams, key roles, overlap with your work, interaction log) and use a dynamic query (e.g., Dataview) at the bottom to pull all matching L2 sources automatically.

## Question-driven growth

Questions act as pressure tests for the vault:

1. Search existing knowledge.
2. Synthesize an answer with traceable sources.
3. Identify missing, weak, or contradictory knowledge.
4. Propose a focused update.
5. Write only after approval when the vault contract requires it.

## Quality model

Do not classify note quality by line count. Evaluate conceptual clarity, boundaries, evidence, outgoing and incoming relationships, MOC placement, and usefulness for future questions.

## Automation boundary

Automation is appropriate for deterministic discovery and validation. Links, conceptual decomposition, evidence interpretation, and MOC structure require contextual judgment. Legacy bulk tools remain optional and must use dry-run plus review.
