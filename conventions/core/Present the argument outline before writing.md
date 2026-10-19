---
type: convention
rule_id: KB-COLLAB-002
applies_to: [all-agents]
triggers:
  - note-write
  - task-scoping
keywords:
  - outline-first
  - argument-line
  - approval-scope
enforcement: review
severity: warning
status: active
---
# Present the argument outline before writing

## In one line

> Before writing to a note, hand over the argument outline in conversation: which files change, which sections are added, each section's core claim in one sentence, and which link carries which step of the argument. What is needed is confirmation of the argument, not an editing tool's confirmation dialog.

## A tool's confirmation dialog is not confirmation

The dialog asks "write these characters to this file?", not "is this line of argument right?". Both leave "the user confirmed" on the record, which is why one is easily mistaken for the other.

The test: **a confirmation that happens after the content is written is not a confirmation of the argument.**

## The cost argument

| When | What the user can choose |
|---|---|
| shown only once written | accept all of it, or reject it wholesale |
| outline first | change how one line connects, keep the rest |

The difference is cost, not courtesy. Asked after three thousand words, revising costs so much that only the two extremes remain; at the outline stage every decision is still cheap.

In practice **users change how the argument connects, not the wording** - which concept should attach to which, which section is really another note's content. That is exactly the layer an outline carries and a finished text resists.

## What the outline contains

1. Which files change, and whether each is new or rewritten.
2. Which sections each file gains or rewrites.
3. Each section's core claim, in one sentence.
4. How the concepts connect: which link carries which step of the argument, not just which links will appear.

Item 4 is the one most often dropped and the one that matters most. A list of links says what will be mentioned; the carrying relation says what work each link does in the argument - and only the latter is something one can object to.

## When it does not apply

- Purely mechanical fixes: typos, formatting, punctuation.
- Further application of a batch rule that was already approved.
- A single-point change the user explicitly asked to be made directly.

What these share is that there is no argument to discuss; an outline would degrade into reading out the characters about to change.

## Judgement question

**If the user disagrees with how this note is written, which sentence would they object to?**

If there is no answer, no claim has formed that anyone could object to - that is a table of contents, not an outline.

## Related

- `Feasibility before implementation` - a clear boundary: that rule decides whether to unfold a full plan, this one what to hand over before writing once it is unfolded.
- `Notes teach, they do not log edits` - directions rejected at the outline stage do not enter the notes; they belong to the editing process.
