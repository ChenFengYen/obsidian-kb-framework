---
type: convention
rule_id: KB-CHANGE-001
scope: [agent-operation]
applies_to: [all-agents]
triggers: [delete, breaking-change, commit, tag, push]
enforcement: approval
severity: error
status: active
---
# Approval before destructive or published changes

Before deletion, breaking changes, commit, tag, or push, report the scope, removed material, compatibility and data risks, tests, and proposed message. Obtain explicit approval before proceeding.
