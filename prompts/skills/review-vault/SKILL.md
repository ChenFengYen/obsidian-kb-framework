---
name: review-vault
description: Review vault structure, links, MOCs, and actionable governance issues
disable-model-invocation: true
---
# Review the vault

1. Read `AGENTS.md`, `vault_config.yaml`, `Home.md`, and the Convention MOC.
2. Run `python tools/vault_health.py --summary` and `python tools/note_graph.py --json`.
3. Inspect representative MOCs and notes before interpreting counts.
4. Prioritize broken navigation, unreviewed output, unclear concepts, missing MOC placement, and weak cross-domain relationships.
5. Propose a short action list. Do not edit notes until the user approves the scope.

Do not use line count as a proxy for note quality. A concise note may be complete; a long note may still be disconnected or unsupported.
