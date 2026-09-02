---
type: convention
rule_id: KB-WRITING-001
applies_to: [all-agents]
triggers:
  - note-write
keywords:
  - correction
  - epistemic-status
enforcement: review
severity: warning
status: active
---
# Notes teach, they do not log edits

## In one line

> A note states what currently holds and how strong the evidence currently is - not how the author got there. The editing process belongs in version control and in the agent's own project memory, never in the note.

## Phrasings to delete

- A correction callout dated and captioned "this section previously said…"
- "the original sentence also got X wrong", "this previously read…, now removed"
- "lesson learned:…", "I originally thought…, but that turned out to be wrong"
- Cross-references such as "see the correction above" or "was previously misclassified as…"

## How to rewrite

1. State the corrected fact directly, as an assertion, with its source.
2. **Promote the general rule that correction established into forward-looking guidance**, placed where a reader needs it. A finding that "attribute X cannot be inferred from an image" belongs in the note's opening description of how the observations were made - not in a footnote about a past mistake.
3. A specific number with no source is **deleted**, not annotated as "previously stated as N, now removed".
4. Dead ends and intermediate results go in the agent's project memory, which exists for exactly that and does not consume the knowledge base.

## What to keep: epistemic status is not history

| Keep | Delete |
|---|---|
| "this sentence currently has no source" | "this had no source, now added" |
| "unverified", "needs confirmation", "awaiting a new batch" | "was recorded as available, later found not to be" |
| Scope limits on a citation - materials, dose, extrapolation | "I cited the wrong paper at first" |

The test: **statements about the present strength of the evidence stay; statements about what the author did are removed.** They look alike, but the first is what a reader needs in order to decide whether this passage can be relied on, and the second matters only to whoever wrote it.

## Boundary with history preservation

`Preserve note and convention history` requires that superseded methods, and directions tried but not adopted, be kept in an archive section with dates and reasons. The two rules govern different things:

- **Changes in the subject matter** - a method superseded, a conclusion overturned by new data, an approach tried and found not to work - are themselves knowledge. Keep them, compactly, with a path back, under that rule.
- **The author's editing process** - what was written wrongly, which sentence changed - is not knowledge. It does not enter the note; its trace is version control and the project memory.

If an overturned **hypothesis** carries knowledge of its own, write it as a collapsed aside setting the claim beside the evidence against it, rather than as "I originally thought".

## Scope

Every note: concept notes, observation notes, tutorials, maps of content, pipeline documentation. Teaching material has fuller presentation rules of its own, from the same root - **the reader of a tutorial is your future self, who needs to know what to do, not which detours you took.**

## Related

- `Preserve note and convention history` - the complementary rule; these two must be read together, since the boundary above is what makes either usable.
- `Do not invent facts or thresholds` - why an unsourced number is deleted rather than annotated.
