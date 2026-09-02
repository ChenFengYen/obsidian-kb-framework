---
type: convention
rule_id: KB-HISTORY-001
applies_to: [all-agents]
triggers:
  - note-write
keywords:
  - superseded-method
  - rules-file-trim
enforcement: review
severity: warning
status: active
---
# Preserve note and convention history

## In one line

> Present the current state in full and earlier stages compactly, but always leave a path back. When trimming a rules file, move what you remove into a sibling history file rather than deleting it.

## Knowledge notes

This applies to notes that **accumulate stages** - project notes and methodology notes. Concept notes and tutorials usually have no history to archive, and the two kinds are easy to tell apart. **Size is a symptom, not the test**: the test is whether the note has evolved.

- The current method, conclusions, limits, open items, and file locations stay in full.
- Earlier stages compress to a date, the core conclusion, and a link to the source.
- Large ranking tables and cell-by-cell results move to the source data or report; the note keeps the comparison that mattered.
- Superseded methods, **and directions tried but not adopted**, go into a history section with the date and the reason. The first was once authoritative and got replaced; the second was never adopted, but "this path was walked, and here is why it does not work" is equally part of what is known. An abandoned direction usually needs **one paragraph**, at the end of the note.
- A caveat that still holds is never archived merely for being old.

## Agent rules files

When pulling version records or outdated sections out of an agent contract, first create a sibling `<name>_HISTORY` file holding the original text, then trim the main file.

## Why the two differ

An ordinary knowledge note can rely on version control and source links for its history. An agent's rule history has to be **discoverable without archaeology** - the next agent reads files, it does not read your commit log - so it gets a file of its own.

## Related

- `Notes teach, they do not log edits` - the complementary rule, and the one most often misread as contradicting this one. That rule removes the *author's editing process*; this one preserves *changes in the subject matter*. Read both before deciding whether a passage stays.
- `Fixed operation vocabulary for knowledge base access` - a soft DELETE marks a note superseded rather than removing it, for the reason given here.
