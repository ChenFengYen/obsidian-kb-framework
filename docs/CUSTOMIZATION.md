# Customization

## Domains

Each domain has a description and optional routing keywords. Keywords suggest where material may belong; they do not authorize automatic links or note creation.

## Convention packs

Select only applicable packs in `vault_config.yaml`. Add a new pack when a rule is portable across users but conditional on a workflow, platform, or domain.

Every Convention requires:

- `type: convention`
- a stable `rule_id`
- list-valued `scope`, `applies_to`, and `triggers`
- `enforcement`, `severity`, and `status`

Run `python framework/validate_conventions.py --root conventions` after changes.

## Personal preferences

Keep personal paths, credentials, machine permissions, datasets, sample identifiers, and visual preferences out of framework packs. Store them in local configuration or a private vault Convention.

## Adapters and skills

Keep adapters thin. Shared behavior belongs in `AGENTS.md` or a Convention. Skills describe bounded workflows and should obey the same approval and trust boundaries.
