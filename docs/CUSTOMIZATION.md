# Customization

## Domains

Each domain has a description and optional routing keywords. Keywords suggest where material may belong; they do not authorize automatic links or note creation.

## Convention packs

Select only applicable packs in `vault_config.yaml`. Add a new pack when a rule is portable across users but conditional on a workflow, platform, or domain.

Every Convention requires:

- `type: convention`
- a stable `rule_id`, registered in `conventions/registry.yaml`
- list-valued `scope`, `applies_to`, and `triggers`
- `enforcement`, `severity`, and `status`

Write `triggers` as actions or materials, not topics. An agent needs the rule
when it is about to do something, not while it is thinking about a subject.

Run `python framework/validate_conventions.py --root conventions --strict-registry`
after changes, and `--list` to print the registry as a Markdown table. Drop
`--strict-registry` when validating a subset such as one domain folder: the
reverse check expects every `shipped` id to be present.

## Rule ids

`conventions/registry.yaml` is the only authority for the `KB-*` namespace.
Append to `rules`; never renumber an existing entry. An id stays claimed after
its Convention is superseded, because the number means something to anyone who
read it before.

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
