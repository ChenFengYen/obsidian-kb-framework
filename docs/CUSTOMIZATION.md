# Customization

## Domains

Each domain has a description and optional routing keywords. Keywords suggest where material may belong; they do not authorize automatic links or note creation.

## Convention packs

Select only applicable packs in `vault_config.yaml`. Add a new pack when a rule is portable across users but conditional on a workflow, platform, or domain.

Every Convention requires:

- `type: convention`
- a stable `rule_id`, registered in `conventions/registry.md`
- list-valued `applies_to` and `triggers`
- `enforcement`, `severity`, and `status`

Write `triggers` as actions or materials, not topics. An agent needs the rule
when it is about to do something, not while it is thinking about a subject.
Every value must come from the trigger vocabulary in `conventions/registry.md`;
the validator rejects anything else.

That list is closed on purpose. Left open, each rule invents its own wording
and nothing repeats — a value used once can never be filtered for, so the field
ends up looking like an index while retrieving nothing. Measured on the
upstream vault before closing it: 162 distinct trigger values across 51 rules,
151 of them used exactly once.

Specific wording that no term covers goes under `keywords`, an open list that
is deliberately not a filter: it keeps the precise material (`impact-factor`,
`cssclasses`, `gitignore-edit`) findable by full-text search without pretending
to be a classification axis. Terms accumulate there until they justify a new
entry in the vocabulary.

## Finding the rules for a task

Two ways in, and they answer different questions.

```bash
python framework/validate_conventions.py --root conventions --index
python framework/validate_conventions.py --root conventions --for-trigger note-write
```

`--index` prints every rule as one line — id, triggers, name, one-line version.
It exists so that no task has to be classified before its rules can be found:
measured on the upstream vault, all 51 rules in full are ~99k characters while
the index is ~6.7k (6.7%), cheap enough to read whole. Recognising the rule that
bites is more reliable than recalling that it exists, and nothing notices when
recall fails.

`--for-trigger` narrows to one term once the task is clear. Do not replace it
with a grep: `^  - term$` misses every CRLF file and also matches the same word
sitting in `tags`, and on the upstream vault one term lost 2 of its 5 rules to
the first error while gaining 1 it does not have to the second.

A rule supplies its headline in one of two shapes: an `In one line` (or
`一句話版`) section holding a blockquote, or — for a rule whose whole body is a
single short paragraph — that paragraph. Past 400 characters the paragraph is
prose rather than a headline, and `--index` reports the rule as missing one
instead of pasting a wall of text into the listing.

Run `python framework/validate_conventions.py --root conventions --strict-registry`
after changes. Drop `--strict-registry` when validating a subset such as one
domain folder: the reverse checks expect every `shipped` id to be present.

## Rule ids

`conventions/registry.md` is the only authority for the `KB-*` namespace.
Append a row; never renumber an existing entry. An id stays claimed after its
Convention is superseded, because the number means something to anyone who read
it before.

The registry is a Markdown table rather than YAML because its payload is a flat
row of scalars — the nesting and load-time type checking a YAML file buys were
never used, while a table is readable in the vault it governs and its rule names
are links that show up in backlinks and the graph. The table is the authority,
not a rendering of one; nothing is stored twice.

A name wrapped in `[[ ]]` is the note that claims the id in that tree. Those
brackets are not maintained by hand: `--strict-registry` fails when a linked
name has no note, when a note has no link, or when a link names a different file
than the one carrying the id. Without that check the brackets would be a second
copy of "does this note exist", which is the drift the registry exists to
prevent.

`status: shipped` means the note is in this repository. `status: reserved` means
an upstream vault holds the number and the rule has not been made portable —
recorded so a new rule cannot silently reuse it. Downstream vaults keep
field-specific rules under their own prefix, declared in `reserved_prefixes`;
the validator accepts those and does not expect their content here.

The generated vault carries a registry reflecting the packs actually installed,
and its Convention MOC explains the scheme to whoever works in that vault.

## Personal preferences

Keep personal paths, credentials, machine permissions, datasets, sample identifiers, and visual preferences out of framework packs. Store them in local configuration or a private vault Convention.

## Adapters and skills

Keep adapters thin. Shared behavior belongs in `AGENTS.md` or a Convention. Skills describe bounded workflows and should obey the same approval and trust boundaries.
