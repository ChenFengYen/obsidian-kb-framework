#!/usr/bin/env python3
'''Validate Convention frontmatter and rule identifiers.

Two independent checks run over a Convention tree:

1. Frontmatter shape - every note carries the required fields with valid values.
2. Registry agreement - every rule_id is listed in the registry, and every id
   the registry marks `shipped` actually has a note. Downstream vaults keep
   domain rules under their own reserved prefix, which the registry declares
   but does not enumerate.

The registry check is skipped when no registry file is present, so a vault that
tracks only its own Conventions can still run the frontmatter check alone.
'''

import argparse
from pathlib import Path

import yaml

REQUIRED = {
    'type', 'rule_id', 'scope', 'applies_to', 'triggers',
    'enforcement', 'severity', 'status',
}
VALID_ENFORCEMENT = {'review', 'approval', 'lint', 'path-check'}
VALID_SEVERITY = {'info', 'warning', 'error'}
DEFAULT_REGISTRY = 'registry.yaml'
# Documentation that lives beside the Conventions but is not one of them.
NOT_A_CONVENTION = {'README.md'}


def frontmatter(path):
    # utf-8-sig, not utf-8: editors on Windows write a BOM, and a leading
    # U+FEFF makes the `---` test fail. That failure is silent in the worst
    # way - the file reports one parse error and none of its fields are ever
    # checked, so a tree of BOM'd notes can look thin on errors while being
    # entirely unvalidated.
    text = path.read_text(encoding='utf-8-sig')
    if not text.startswith('---\n'):
        raise ValueError('missing YAML frontmatter')
    parts = text.split('---', 2)
    return yaml.safe_load(parts[1]) or {}


def load_registry(path):
    '''Return (rules_by_id, reserved_prefixes) from a registry file.'''
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}
    rules = {}
    for entry in data.get('rules') or []:
        rule_id = entry.get('id')
        if rule_id:
            rules[rule_id] = entry
    prefixes = [
        item.get('prefix')
        for item in data.get('reserved_prefixes') or []
        if item.get('prefix')
    ]
    return rules, prefixes


def check_registry(seen, registry_path, strict=False):
    '''Compare the ids found on disk against the registry.

    The forward check - every id in use must be registered - always runs.
    The reverse check - every `shipped` id must have a note - only holds when
    the tree being validated is the one the registry describes. Point this at
    a single domain folder, or at a vault that carries only some packs, and
    every absent id would look like an error, so it is opt-in.
    '''
    errors = []
    rules, prefixes = load_registry(registry_path)
    if not rules:
        return [f'{registry_path}: registry lists no rules']

    for rule_id, path in sorted(seen.items(), key=lambda kv: str(kv[1])):
        if rule_id in rules:
            continue
        if any(rule_id.startswith(prefix) for prefix in prefixes):
            continue
        errors.append(
            f'{path}: rule_id {rule_id} is not in {registry_path}; '
            'add it there before using the id'
        )

    if strict:
        for rule_id, entry in sorted(rules.items()):
            if entry.get('status') == 'shipped' and rule_id not in seen:
                errors.append(
                    f'{registry_path}: {rule_id} is marked shipped but no note claims it'
                )
    return errors


def render_table(registry_path):
    '''Render the registry as a Markdown table.

    Printed on demand rather than committed anywhere. A second copy of the
    numbering that someone has to remember to update is exactly the drift the
    registry exists to prevent, so the readable view is generated, never stored.
    '''
    rules, prefixes = load_registry(registry_path)
    lines = ['| rule_id | 規約 | 狀態 | pack |', '|---|---|---|---|']
    for rule_id, entry in sorted(rules.items()):
        name = entry.get('name_zh') or entry.get('name', '')
        status = entry.get('status', '')
        pack = entry.get('pack', '—')
        former = entry.get('former_ids')
        if former:
            name += ' （舊號 ' + ', '.join(former) + '）'
        lines.append(f'| `{rule_id}` | {name} | {status} | {pack} |')
    if prefixes:
        lines.append('')
        lines.append('保留給下游 vault 的前綴：' + '、'.join(f'`{p}`' for p in prefixes))
    shipped = sum(1 for e in rules.values() if e.get('status') == 'shipped')
    lines.append('')
    lines.append(f'共 {len(rules)} 個編號：{shipped} 個 shipped、{len(rules) - shipped} 個 reserved。')
    return '\n'.join(lines)


def validate(root, registry=None, strict=False):
    errors = []
    seen = {}
    files = [
        path for path in sorted(Path(root).rglob('*.md'))
        if path.name not in NOT_A_CONVENTION
    ]
    if not files:
        return ['no Convention files found']
    for path in files:
        try:
            data = frontmatter(path)
        except Exception as exc:
            errors.append(f'{path}: {exc}')
            continue
        missing = REQUIRED - set(data)
        if missing:
            errors.append(f'{path}: missing {sorted(missing)}')
        if data.get('type') != 'convention':
            errors.append(f'{path}: type must be convention')
        rule_id = data.get('rule_id')
        if rule_id in seen:
            errors.append(f'{path}: duplicate rule_id {rule_id} also used by {seen[rule_id]}')
        elif rule_id:
            seen[rule_id] = path
        if data.get('enforcement') not in VALID_ENFORCEMENT:
            value = data.get('enforcement')
            errors.append(f'{path}: invalid enforcement {value}')
        if data.get('severity') not in VALID_SEVERITY:
            value = data.get('severity')
            errors.append(f'{path}: invalid severity {value}')
        for field in ('scope', 'applies_to', 'triggers'):
            if field in data and not isinstance(data[field], list):
                errors.append(f'{path}: {field} must be a list')

    registry_path = Path(registry) if registry else Path(root) / DEFAULT_REGISTRY
    if registry_path.is_file():
        errors.extend(check_registry(seen, registry_path, strict))
    elif registry:
        errors.append(f'{registry_path}: registry file not found')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='conventions')
    parser.add_argument(
        '--registry',
        help='Path to registry.yaml. Defaults to <root>/registry.yaml when present.',
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='Print the registry as a Markdown table and exit.',
    )
    parser.add_argument(
        '--strict-registry',
        action='store_true',
        help='Also require every `shipped` id to have a note. Use when the root '
             'is the tree the registry describes, not a subset of it.',
    )
    args = parser.parse_args()

    registry_path = Path(args.registry) if args.registry else Path(args.root) / DEFAULT_REGISTRY
    if args.list:
        if not registry_path.is_file():
            print(f'{registry_path}: registry file not found')
            raise SystemExit(1)
        print(render_table(registry_path))
        return

    errors = validate(args.root, args.registry, args.strict_registry)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('Convention validation passed: ' + str(Path(args.root).resolve()))


if __name__ == '__main__':
    main()
