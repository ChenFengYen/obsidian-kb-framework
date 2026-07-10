# User guide

## Ask questions

Ask the agent a real question. It searches the vault, synthesizes an answer, and identifies gaps or contradictions. A proposed note update remains a proposal until approved under the vault contract.

## Add knowledge

Place durable concepts in a domain `Note` directory and connect them deliberately to a MOC or related note. Sources and project records may use separate locations when configured.

## Review structure

Use `/review-vault` for a contextual review and `python tools/vault_health.py --summary` for deterministic signals. Counts guide investigation; they do not define quality.

## End a session

Use `/debrief` to identify durable conclusions, corrections, decisions, or feedback. Confirm destinations before writing.

## Legacy automation

Automatic link injection, stub creation, and batch enrichment were removed in v2. Preview changes and review each approved batch before applying it.
