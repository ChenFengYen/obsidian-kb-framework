#!/usr/bin/env python3
'''Validate Convention frontmatter and rule identifiers.

Four independent checks run over a Convention tree:

1. Frontmatter shape - every note carries the required fields with valid values.
2. Registry agreement - every rule_id is listed in the registry, and every id
   the registry marks `shipped` actually has a note. Downstream vaults keep
   domain rules under their own reserved prefix, which the registry declares
   but does not enumerate.
3. Link agreement - a rule name the registry wraps in [[ ]] must be a note that
   exists in the tree, and every note must be linked from its row.
4. Trigger vocabulary - every `triggers` value is a term the registry lists.
   Triggers say when a rule should come to mind, so they are only useful if
   several rules share a term; a value invented for one note can never be
   filtered for. Specific wording that no term covers belongs under `keywords`,
   an open field that is deliberately not a filter.

The registry is a Markdown table, not YAML. Its payload is a flat row of
scalars, so YAML's nesting and load-time type checking were never used, while a
Markdown table is readable in the vault it governs and its rule names are links
that appear in backlinks and the graph. Nothing about the numbering is stored
twice: the table is the authority, and check 3 is what keeps its links from
drifting away from the notes on disk.

Checks 2 and 3 are skipped when no registry file is present, so a vault that
tracks only its own Conventions can still run the frontmatter check alone.
'''

import argparse
import re
from pathlib import Path

import yaml

REQUIRED = {
    'type', 'rule_id', 'applies_to', 'triggers',
    'enforcement', 'severity', 'status',
}
VALID_ENFORCEMENT = {'review', 'approval', 'lint', 'path-check'}
VALID_SEVERITY = {'info', 'warning', 'error'}
VALID_STATUS = {'shipped', 'reserved'}
RULE_ID = re.compile(r'^[A-Z][A-Z0-9]*-[A-Z][A-Z0-9]*-\d{3}$')
WIKILINK = re.compile(r'^\[\[(.+)\]\]$')
RULE_COLUMNS = ['rule_id', 'name', 'name_zh', 'status', 'pack', 'former_ids']
PREFIX_COLUMNS = ['prefix', 'owner']
TRIGGER_COLUMNS = ['trigger', 'applies when']
LIST_FIELDS = ('applies_to', 'triggers', 'keywords')
EMPTY = {'', '—', '-'}
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


def _cells(line):
    '''Split one Markdown table row into trimmed cells.'''
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def _tables(text):
    '''Yield (header_cells, [row_cells, ...]) for every table in the text.

    A table is a header row followed by a separator row. Anything else is
    prose and is skipped, so the registry can carry its own explanation.
    '''
    lines = text.splitlines()
    index = 0
    while index < len(lines) - 1:
        line, following = lines[index], lines[index + 1]
        is_header = line.strip().startswith('|')
        is_separator = set(following.strip()) <= set('|-: ') and '-' in following
        if not (is_header and following.strip().startswith('|') and is_separator):
            index += 1
            continue
        header = _cells(line)
        rows = []
        index += 2
        while index < len(lines) and lines[index].strip().startswith('|'):
            rows.append((index + 1, _cells(lines[index])))
            index += 1
        yield header, rows


def _value(cell):
    '''Strip decoration from a cell: backticks, placeholder dashes, link.'''
    text = cell.strip().strip('`').strip()
    if text in EMPTY:
        return '', False
    match = WIKILINK.match(text)
    if match:
        return match.group(1).strip(), True
    return text, False


def parse_registry(path):
    '''Return (rules, reserved_prefixes, trigger_vocabulary, errors).

    Structural problems are errors rather than silently short rows. A table
    cell that vanished takes a whole field with it, and a registry that parses
    to fewer rules than it lists would report a clean run - the exact failure
    mode this file exists to prevent.
    '''
    text = Path(path).read_text(encoding='utf-8-sig')
    rules, prefixes, triggers, errors = {}, [], [], []
    seen_rule_table = False

    for header, rows in _tables(text):
        if header[:1] == ['rule_id']:
            seen_rule_table = True
            if header != RULE_COLUMNS:
                errors.append(
                    f'{path}: rule table columns are {header}, expected {RULE_COLUMNS}'
                )
                continue
            for line_no, cells in rows:
                if len(cells) != len(RULE_COLUMNS):
                    errors.append(
                        f'{path}:{line_no}: row has {len(cells)} cells, '
                        f'expected {len(RULE_COLUMNS)}'
                    )
                    continue
                entry, linked = {}, []
                for column, cell in zip(RULE_COLUMNS, cells):
                    value, is_link = _value(cell)
                    entry[column] = value
                    if is_link:
                        linked.append((column, value))
                rule_id = entry['rule_id']
                if not RULE_ID.match(rule_id):
                    errors.append(f'{path}:{line_no}: malformed rule_id {rule_id!r}')
                    continue
                if rule_id in rules:
                    errors.append(f'{path}:{line_no}: duplicate rule_id {rule_id}')
                    continue
                if entry['status'] not in VALID_STATUS:
                    errors.append(
                        f'{path}:{line_no}: {rule_id} has status '
                        f'{entry["status"]!r}, expected one of {sorted(VALID_STATUS)}'
                    )
                if len(linked) > 1:
                    columns = ', '.join(column for column, _ in linked)
                    errors.append(
                        f'{path}:{line_no}: {rule_id} links more than one name ({columns}); '
                        'exactly one note may claim an id'
                    )
                entry['former_ids'] = [
                    part.strip().strip('`')
                    for part in entry['former_ids'].split(',')
                    if part.strip()
                ]
                entry['line'] = line_no
                entry['linked'] = linked[0][1] if len(linked) == 1 else None
                rules[rule_id] = entry
        elif header[:1] == ['prefix']:
            for _, cells in rows:
                value, _ = _value(cells[0])
                if value:
                    prefixes.append(value)
        elif header[:1] == ['trigger']:
            for line_no, cells in rows:
                value, _ = _value(cells[0])
                if not value:
                    continue
                if value in triggers:
                    errors.append(f'{path}:{line_no}: duplicate trigger {value}')
                    continue
                triggers.append(value)

    if not seen_rule_table:
        errors.append(f'{path}: no rule table found (expected a | rule_id | ... | header)')
    return rules, prefixes, triggers, errors


def check_triggers(triggers_by_path, vocabulary, registry_path):
    '''Every trigger a note declares must be a term the registry lists.

    Open triggers are the failure this check exists for: a value invented for
    one note can never be filtered for, so the field ends up looking like an
    index while retrieving nothing. Closing it is only meaningful if something
    enforces the closure, which is here.
    '''
    errors = []
    if not vocabulary:
        return errors
    allowed = set(vocabulary)
    for path, values in sorted(triggers_by_path.items(), key=lambda kv: str(kv[0])):
        for value in values:
            if value not in allowed:
                errors.append(
                    f'{path}: trigger {value!r} is not in the vocabulary in '
                    f'{registry_path}; use an existing term, put the specific '
                    'wording under `keywords`, or add the term deliberately'
                )
    return errors


def check_registry(seen, registry_path, strict=False):
    '''Compare the ids found on disk against the registry.

    The forward check - every id in use must be registered - always runs.
    The reverse checks - every `shipped` id must have a note, and every link
    must match a note - only hold when the tree being validated is the one the
    registry describes. Point this at a single domain folder, or at a vault
    that carries only some packs, and every absent id would look like an error,
    so they are opt-in.
    '''
    rules, prefixes, _, errors = parse_registry(registry_path)
    if not rules:
        errors.append(f'{registry_path}: registry lists no rules')
        return errors

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
            path = seen.get(rule_id)
            if entry.get('status') == 'shipped' and path is None:
                errors.append(
                    f'{registry_path}: {rule_id} is marked shipped but no note claims it'
                )
            linked = entry.get('linked')
            line = entry.get('line')
            if path is None:
                if linked:
                    errors.append(
                        f'{registry_path}:{line}: {rule_id} links [[{linked}]] '
                        'but no note in this tree claims the id'
                    )
            elif linked is None:
                errors.append(
                    f'{registry_path}:{line}: {rule_id} is claimed by {path.name} '
                    'but its name is not linked; wrap it in [[ ]]'
                )
            elif linked != path.stem:
                errors.append(
                    f'{registry_path}:{line}: {rule_id} links [[{linked}]] '
                    f'but the note claiming it is {path.name}'
                )
    return errors


def validate(root, registry=None, strict=False):
    errors = []
    seen = {}
    triggers_by_path = {}
    found_registries = []
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
        # The registry lives beside the notes it governs and is a note itself,
        # so it is found rather than named. An id outlives the file that holds
        # it; so should the registry's own filename.
        if data.get('type') == 'registry':
            found_registries.append(path)
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
        for field in LIST_FIELDS:
            if field in data and not isinstance(data[field], list):
                errors.append(f'{path}: {field} must be a list')
        if isinstance(data.get('triggers'), list):
            triggers_by_path[path] = data['triggers']

    if registry:
        registry_path = Path(registry)
        if not registry_path.is_file():
            errors.append(f'{registry_path}: registry file not found')
            return errors
    elif len(found_registries) > 1:
        listed = ', '.join(str(path) for path in found_registries)
        errors.append(f'{root}: more than one registry found ({listed})')
        return errors
    else:
        registry_path = found_registries[0] if found_registries else None

    if registry_path is not None:
        errors.extend(check_registry(seen, registry_path, strict))
        _, _, vocabulary, _ = parse_registry(registry_path)
        errors.extend(check_triggers(triggers_by_path, vocabulary, registry_path))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='conventions')
    parser.add_argument(
        '--registry',
        help='Path to the registry note. Defaults to the file under <root> whose '
             'frontmatter says `type: registry`.',
    )
    parser.add_argument(
        '--strict-registry',
        action='store_true',
        help='Also require every `shipped` id to have a note, and every link to '
             'match it. Use when the root is the tree the registry describes, '
             'not a subset of it.',
    )
    args = parser.parse_args()

    errors = validate(args.root, args.registry, args.strict_registry)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('Convention validation passed: ' + str(Path(args.root).resolve()))


if __name__ == '__main__':
    main()
