---
type: convention
rule_id: KB-VCS-001
applies_to: [all-agents]
triggers:
  - version-control
  - note-structure
keywords:
  - directory-rename
  - gitignore-edit
  - commit-size-check
enforcement: review
severity: error
status: active
---
# Ignore rules must survive directory renames

## In one line

> An ignore file holds path strings. Rename the directory and the rule goes quietly dead. The rename and the ignore-rule update must happen in one batch, and the result must be tested with the tool's own "why is this ignored" command - not by reading the rule.

## Rules

- **When moving or renaming any directory covered by an ignore rule, update the ignore file in the same batch of actions.** Not afterwards.
- **Test after changing it**: run the version-control system's ignore-check command against a representative file for every rule you touched. Output means it took effect. Reading the rule string is not verification.
- **Prefer a pattern over a path**: `__pycache__/` beats `some/dir/scripts/__pycache__/`. The former holds at any depth and survives every future rename; bind to a path only when you really do mean that one location.
- **Ignore rules do not apply to already-tracked files.** Removing a tracked file from version control requires an explicit untrack; be aware that this deletes the local copy on other machines at their next pull, so confirm a second copy exists first.
- **In an auto-committing environment, measure the push size after any large rename and before pushing.**

## Why it matters

The failure is **silent**. Nothing warns you; the status command says nothing; files that were being ignored simply become untracked. Where a plugin or a scheduled job commits automatically, the very next commit sweeps all of them into version control.

A measured example: a repository reorganisation renamed a documents directory, and four ignore rules written against the old name became blanks. Roughly 600 PDFs - about 3 GB - plus compiled Python artefacts were committed automatically. The push then exceeded the hosting provider's single-push size limit and returned a generic server error. **The error message pointed nowhere near the actual cause.**

## Diagnosis and recovery

**Measure what a push will send** before sending it: list the objects unique to your branch and ask the object database for each one's type and size.

⚠️ The format string must include the field carrying the rest of the line. Omit it and each "hash + path" line is parsed as one object name, every lookup misses, and the measurement returns a false zero.

**Do not** estimate push size from the size of a self-contained pack or bundle. Those must stand alone, so they include old blobs reachable through renamed paths; one measured case inflated to 410 MiB against an actual transfer of 6.35 MiB, because a real push negotiates with the remote and skips objects it already has.

**The cost of recovery changes the moment you push:**

| Timing | What it takes |
|---|---|
| Not yet pushed | Soft-reset to the remote tip, fix the ignore file, untrack the paths, recommit |
| Already pushed | History rewrite plus a force push, affecting every other clone |

So **deal with it the moment you notice**, rather than pushing first.

**Space is not reclaimed automatically** after cleanup. Three steps are needed: delete every branch and tag still pointing at the old commits, expire the unreachable reflog entries, then garbage-collect with pruning. Skip any one and the old objects remain reachable and survive. Expire only the unreachable entries, so other operations keep their recovery points.

## Related

- `Approval before destructive or published changes` - the human checkpoint before commit and push, upstream of this rule.
- `Separate temporary work from durable knowledge` - which artefacts should never have been in version control at all.
- `Confirm the measurement method before trusting numbers` - the false zero above is that rule's first failure class, met here in the wild.
- `Windows UTF-8 file safety` - the same accident shape: a rule applied mechanically, its actual effect never tested.
