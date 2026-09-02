---
type: convention
rule_id: KB-ACCESS-001
applies_to: [all-agents]
triggers:
  - kb-access
  - destructive-op
keywords:
  - read-note
  - write-note
  - shell-read
  - note-delete
  - enforcement-layer
enforcement: review
severity: warning
status: active
---
# Fixed operation vocabulary for knowledge base access

## In one line

> Every action on the knowledge base maps to exactly one tool, and the set of operations is closed at five. The dividing line in one sentence: **computing a number *about* the content with a shell command is fine; reading the content *itself* with one is not.**

Scope is the knowledge layer - notes and any agent memory store. Scratch files and script working directories are outside it.

## The five operations

| Operation | Tool role | Precondition |
|---|---|---|
| CREATE | the write tool | SEARCH first, to confirm it does not already exist |
| SEARCH | the content- and filename-search tools | none |
| FETCH | the read tool, whole file, no line limit | none |
| UPDATE | the edit tool | the same file has been FETCHed in this session |
| DELETE | mark superseded and remove from indexes | a hard delete needs human approval |

Names differ between agent platforms; the roles do not. Map them once, at the top of your agent contract, and use the role names everywhere else.

**Keeping SEARCH and FETCH separate is the part most often skipped.** Both are "reading" in CRUD terms, but what they deliver differs by an order of magnitude: three matching lines is not the same as having read the file. Merging them also creates a perverse incentive - to make the record look right, you load a 50,000-character file in full. Kept apart, "I searched it" and "I read it" become two statements that can each be made honestly.

The vocabulary is closed for the same reason a classification vocabulary is: an open list cannot be filtered or counted, so "what was actually done in that session" stops being answerable.

## Why FETCH is the read tool and not a shell command

Reading the same file three ways does not deliver the same thing:

| Difference | Read tool | `cat` / `head` / `sed -n` |
|---|---|---|
| Staleness marking | a memory file arrives with a "written N days ago, may be outdated" notice | none |
| Editability afterwards | satisfies the edit tool's precondition | does not; the edit is refused |
| Large files | delivers up to a large line budget | output over the limit is replaced by a short preview |

The first difference has the least visible consequence: content read through a shell arrives **without any staleness marking**, so the reader cannot tell whether this is three days old or three months old. That is the difference between literal retrieval and version-aware access.

The third is an instance of the "tools omit by default" family - the tool announces the truncation, but a downstream record saying only "read that file" will record a 2 KB preview as a whole file.

## The line between content and numbers

What is forbidden is reading **content** through a shell, not touching the knowledge base with one:

> If the output enters your reasoning as material, it must be FETCHed.
> If the output is only a statistic about the content, a shell command is the right tool.

So line counts, link-health checks, commit statistics, encoding scans, and file-size distributions all belong in the shell - and *should* be there, being orders of magnitude cheaper than loading whole files. The test is self-applying: **if I cited that output to argue something, it should have been FETCHed.**

## DELETE defaults to a soft delete

Removing a note or a rule means marking it superseded and taking it out of the indexes, not deleting the file:

- In the note: set its status to superseded or deprecated, and open the body with a pointer to whatever replaces it.
- In the indexes: remove it from maps and routing tables so it stops being served as the current answer.
- Hard deletion: requires human approval.

The reason matches the history-preservation rule - a superseded conclusion is itself knowledge, and a reader needs to know the old answer existed and why it no longer holds. Published work on agent memory systems argues for the same shift: from hard replacement to time-aware soft updates, marking an entry invalid rather than dropping it, which is preferable wherever traceability matters.

## Three layers: instruct, verify, block

Writing a rule down does not make it happen. The same rule placed in a different layer differs in kind, not degree:

```text
BLOCK     permission denials, hook decisions, hard-deny modes
          <- not an instruction. Non-compliance is impossible

VERIFY    validator scripts, health checks, scanners
          <- does not block, but skipping it leaves a traceable gap

INSTRUCT  agent contract, conventions, memory
          <- all prose. Its force is probabilistic
```

**Where a rule belongs:**

| Nature of the rule | Layer |
|---|---|
| Decidable from the text, and repairable after the fact | VERIFY. Formatting, links, naming |
| Irreversible, or crossing a safety boundary | BLOCK. Deletion, force push, writing outside the workspace |
| Requires semantic judgement | INSTRUCT only - and accept that it is probabilistic |

The test behind that table is three questions about executability: **can this rule be invoked, can its result be verified, can it compose with other rules?** A rule that answers "yes" three times should not stay in the prose layer; agent-memory research makes the same argument, that plain-text policies are structural guidance rather than callable actions and must be promoted to be reliable.

Practice bears this out: checks compiled into scripts - link counts, encoding scans - are never skipped, because each run must report a number. Rules left as prose accumulate a record of being missed.

Platform-specific interfaces for the BLOCK layer belong in your platform guide, not here.

## Judgement question

**If I used the wrong operation just now, where would I see it?**

"It would be refused" means the BLOCK layer. "There would be a trace afterwards" means the VERIFY layer. No concrete signal at all means the rule is currently a piece of prose, and its force should be estimated accordingly - not from how firmly it is worded.

## Related

- `Confirm the measurement method before trusting numbers` - this rule governs how an action is performed, that one how the resulting number is measured; both guard against "it looks finished".
- `Classification vocabularies must be closed` - the same closed-vocabulary principle applied to field values rather than actions.
- `Separate temporary work from durable knowledge` - defines which files are in the knowledge layer, and therefore in scope here.
- `Approval before destructive or published changes` - the approval boundary for a hard DELETE.
- `Preserve note and convention history` - why a soft delete keeps the entry.
