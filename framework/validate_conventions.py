#!/usr/bin/env python3
'''Validate Convention frontmatter and rule identifiers.'''

import argparse
from pathlib import Path

import yaml

REQUIRED = {
    'type', 'rule_id', 'scope', 'applies_to', 'triggers',
    'enforcement', 'severity', 'status',
}
VALID_ENFORCEMENT = {'review', 'approval', 'lint', 'path-check'}
VALID_SEVERITY = {'info', 'warning', 'error'}


def frontmatter(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError('missing YAML frontmatter')
    parts = text.split('---', 2)
    return yaml.safe_load(parts[1]) or {}


def validate(root):
    errors = []
    seen = {}
    files = sorted(Path(root).rglob('*.md'))
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
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='conventions')
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('Convention validation passed: ' + str(Path(args.root).resolve()))


if __name__ == '__main__':
    main()
