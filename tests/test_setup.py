import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import setup_v2
from framework.validate_conventions import (build_index, headline, parse_registry,
                                            rules_for_trigger, validate)

REGISTRY = ROOT / 'conventions' / 'registry.md'


def mutated_tree(tmp, mutate):
    '''Copy the Convention tree with one edit applied to the registry.'''
    tree = Path(tmp) / 'conventions'
    shutil.copytree(ROOT / 'conventions', tree)
    target = tree / 'registry.md'
    text = target.read_text(encoding='utf-8')
    changed = mutate(text)
    assert changed != text, 'the mutation did not change the registry'
    target.write_text(changed, encoding='utf-8')
    return tree


DOMAIN_TABLE = """

## Domain rule ids

| id | name_zh | lifecycle | note |
|---|---|---|---|
| `PHENO-QC-001` | [[Object level QC stays binary]] | active | — |
| `PHENO-TRAIT-002` | — | retired | downgraded into the table it governed |
"""


def with_domain_table(text):
    return text + DOMAIN_TABLE


def claiming(root, rule_id):
    '''Point one core Convention at another id, and return the tree.'''
    victim = root / 'conventions' / 'core' / 'Do not invent facts or thresholds.md'
    victim.write_text(
        victim.read_text(encoding='utf-8').replace('KB-EVIDENCE-001', rule_id),
        encoding='utf-8',
    )
    return root / 'conventions'


def all_text(root):
    suffixes = {'.md', '.yaml', '.yml', '.json', '.py', '.js'}
    chunks = []
    for path in Path(root).rglob('*'):
        if path.is_file() and path.suffix.lower() in suffixes:
            chunks.append(path.read_text(encoding='utf-8'))
    return '\n'.join(chunks)


class SetupTests(unittest.TestCase):
    def test_source_conventions_are_valid(self):
        self.assertEqual(validate(ROOT / 'conventions'), [])

    def test_invalid_convention_reports_schema_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.md'
            path.write_text('---\ntype: note\nseverity: fatal\n---\n', encoding='utf-8')
            errors = validate(tmp)
            self.assertTrue(any('missing' in error for error in errors))
            self.assertTrue(any('invalid severity' in error for error in errors))

    def test_general_defaults_are_portable(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'vault'
            setup_v2.create_vault(cfg, target)
            self.assertTrue((target / 'AGENTS.md').is_file())
            self.assertTrue((target / 'CLAUDE.md').is_file())
            self.assertTrue((target / 'GEMINI.md').is_file())
            self.assertTrue((target / 'AgentRules.md').is_file())
            self.assertFalse((target / 'Papers').exists())
            self.assertFalse((target / '.claude' / 'settings.local.json').exists())
            self.assertEqual(validate(target / 'KnowledgeBase' / 'Convention'), [])
            text = all_text(target)
            self.assertNotIn('ChenFengYen', text)
            self.assertNotIn('ObsidianWork', text)
            self.assertNotIn('Plant physiology', text)

    def test_agents_contract_is_whole_and_within_the_load_cap(self):
        '''The contract must carry its own end marker and fit in one load.

        Measured 2026-09-02 against Antigravity: a rules file is truncated at
        24,000 bytes with no error, so a contract can arrive with its ending
        missing while everything else looks normal. `AGENTS-EOF` is what makes
        that visible from inside a session; this test is what keeps the file
        small enough that it never happens.
        '''
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'vault'
            setup_v2.create_vault(cfg, target)
            agents = (target / 'AGENTS.md').read_text(encoding='utf-8')
            self.assertTrue(agents.rstrip().endswith('AGENTS-EOF'))
            self.assertIn('AGENTS-EOF', agents.split('## Startup self-check')[1])
            size = len((target / 'AGENTS.md').read_bytes())
            self.assertLess(size, 20000, 'AGENTS.md is approaching the 24,000-byte load cap')

    def test_agents_contract_carries_debrief_and_skills(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'vault'
            setup_v2.create_vault(cfg, target)
            agents = (target / 'AGENTS.md').read_text(encoding='utf-8')
            self.assertIn('## Conversation debrief', agents)
            self.assertIn('## Available skills', agents)
            for skill in setup_v2.CORE_SKILLS:
                self.assertIn('/' + skill, agents)

    def test_neuroscience_has_no_domain_leakage(self):
        path = ROOT / 'examples' / 'configs' / 'neuroscience.yaml'
        cfg = yaml.safe_load(path.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'neuro'
            setup_v2.create_vault(cfg, target)
            text = all_text(target)
            self.assertNotIn('植物表型', text)
            self.assertNotIn('Plant physiology', text)
            self.assertNotIn('Bioinformatics', text)
            self.assertFalse((target / 'Papers').exists())
            agents = (target / 'AGENTS.md').read_text(encoding='utf-8')
            self.assertNotIn('Zotero work', agents)
            self.assertNotIn('Paper processing', agents)

    def test_v1_batch_pipeline_scripts_are_not_installed(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'no_v1_batch'
            setup_v2.create_vault(cfg, target)
            text = all_text(target)
            self.assertNotIn('concept_index.py', text)
            self.assertNotIn('extract_candidates.py', text)
            self.assertNotIn('quickadd-create-concept.js', text)
            self.assertFalse((target / 'Papers').exists())

    def test_paper_module_installs_its_runtime_dependencies(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        cfg['modules']['paper_pipeline'] = True
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'papers'
            setup_v2.create_vault(cfg, target)
            scripts = target / 'Papers' / 'scripts'
            self.assertTrue((scripts / 'config.py').is_file())
            self.assertTrue((scripts / 'status_tracker.py').is_file())
            self.assertTrue((target / 'Papers' / 'PAPER_PROCESSING_GUIDE.md').is_file())
            result = subprocess.run(
                [sys.executable, str(scripts / 'insert_figures.py'), '--help'],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


class RegistryTests(unittest.TestCase):
    def test_unlisted_rule_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions', root / 'conventions')
            victim = root / 'conventions' / 'core' / 'Do not invent facts or thresholds.md'
            victim.write_text(
                victim.read_text(encoding='utf-8').replace('KB-EVIDENCE-001', 'KB-UNLISTED-999'),
                encoding='utf-8',
            )
            errors = validate(root / 'conventions', strict=True)
            self.assertTrue(any('KB-UNLISTED-999' in error for error in errors))
            self.assertTrue(any('shipped' in error for error in errors))

    def test_shipped_check_is_off_for_a_subset(self):
        # A single domain folder holds only some ids. Without opting in, the
        # absent ones must not be reported as missing notes.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions' / 'core', root / 'core')
            shutil.copy2(REGISTRY, root / 'core' / 'registry.md')
            errors = [str(e) for e in validate(root / 'core')]
            self.assertFalse([e for e in errors if 'marked shipped' in e], errors)
            strict = [str(e) for e in validate(root / 'core', strict=True)]
            self.assertTrue([e for e in strict if 'KB-LINK-001' in e])

    def test_reserved_prefix_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions', root / 'conventions')
            victim = root / 'conventions' / 'core' / 'Do not invent facts or thresholds.md'
            victim.write_text(
                victim.read_text(encoding='utf-8').replace('KB-EVIDENCE-001', 'PHENO-QC-001'),
                encoding='utf-8',
            )
            errors = validate(root / 'conventions')
            self.assertFalse([error for error in errors if 'PHENO-QC-001' in error])

    def test_enumerated_prefix_rejects_an_unlisted_id(self):
        # The rows are what asks for the check: once PHENO- is enumerated, an
        # id under it is no longer waved through by the prefix alone.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions', root / 'conventions')
            registry = root / 'conventions' / 'registry.md'
            registry.write_text(
                with_domain_table(registry.read_text(encoding='utf-8')),
                encoding='utf-8',
            )
            errors = [str(e) for e in validate(claiming(root, 'PHENO-XXX-999'))]
            self.assertTrue(
                [e for e in errors if 'PHENO-XXX-999' in e and 'domain table' in e],
                errors,
            )

    def test_enumerated_prefix_accepts_a_listed_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions', root / 'conventions')
            registry = root / 'conventions' / 'registry.md'
            registry.write_text(
                with_domain_table(registry.read_text(encoding='utf-8')),
                encoding='utf-8',
            )
            errors = [str(e) for e in validate(claiming(root, 'PHENO-QC-001'))]
            self.assertFalse([e for e in errors if 'PHENO-QC-001' in e], errors)

    def test_domain_rows_are_silent_for_a_prefix_not_scanned(self):
        # No single root covers every namespace. A run that sees no PHENO-
        # note must not report the enumerated PHENO- ids as missing.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions', root / 'conventions')
            registry = root / 'conventions' / 'registry.md'
            registry.write_text(
                with_domain_table(registry.read_text(encoding='utf-8')),
                encoding='utf-8',
            )
            errors = [str(e) for e in validate(root / 'conventions', strict=True)]
            self.assertFalse([e for e in errors if 'PHENO-' in e], errors)

    def test_retired_domain_id_cannot_be_claimed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'conventions', root / 'conventions')
            registry = root / 'conventions' / 'registry.md'
            registry.write_text(
                with_domain_table(registry.read_text(encoding='utf-8')),
                encoding='utf-8',
            )
            tree = claiming(root, 'PHENO-TRAIT-002')
            errors = [str(e) for e in validate(tree, strict=True)]
            self.assertTrue(
                [e for e in errors if 'PHENO-TRAIT-002' in e and 'retired' in e],
                errors,
            )

    def test_domain_lifecycle_vocabulary_is_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = mutated_tree(
                tmp,
                lambda text: with_domain_table(text).replace(
                    '| active | — |', '| archived | — |'
                ),
            )
            errors = [str(e) for e in validate(tree)]
            self.assertTrue(
                [e for e in errors if 'lifecycle' in e and 'archived' in e],
                errors,
            )

    def test_partial_pack_install_still_validates(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        cfg['conventions']['packs'] = ['core']
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'partial'
            setup_v2.create_vault(cfg, target)
            conventions = target / 'KnowledgeBase' / 'Convention'
            self.assertTrue((conventions / 'registry.md').is_file())
            self.assertEqual(validate(conventions, strict=True), [])
            rules, _, _, _, errors = parse_registry(conventions / 'registry.md')
            self.assertEqual(errors, [])
            shipped = {i for i, r in rules.items() if r['status'] == 'shipped'}
            self.assertIn('KB-EVIDENCE-001', shipped)      # core, installed
            self.assertNotIn('KB-LINK-001', shipped)       # obsidian, not installed
            self.assertIn('KB-LINK-001', rules)
            # A downgraded rule must lose its link too: a vault that does not
            # install the note must not carry a link that resolves to nothing.
            self.assertIsNone(rules['KB-LINK-001']['linked'])
            self.assertIsNotNone(rules['KB-EVIDENCE-001']['linked'])

    def test_generated_registry_keeps_its_explanation(self):
        # The prose above the table is the only place the numbering is
        # explained to whoever opens the vault. Rewriting the file from parsed
        # values would drop it without failing anything.
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'prose'
            setup_v2.create_vault(cfg, target)
            text = (target / 'KnowledgeBase' / 'Convention' / 'registry.md').read_text(
                encoding='utf-8')
            self.assertIn('type: registry', text)
            self.assertIn('never renumber an existing entry', text)


    def test_bom_prefixed_convention_is_still_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = (
                '---\ntype: convention\nrule_id: KB-EVIDENCE-001\n'
                'scope: [x]\napplies_to: [all-agents]\ntriggers: [y]\n'
                'enforcement: review\nseverity: error\nstatus: active\n---\n本文\n'
            )
            (root / 'bom.md').write_text('﻿' + body, encoding='utf-8')
            errors = [str(e) for e in validate(root)]
            # The BOM must not hide the file from field validation.
            self.assertFalse([e for e in errors if 'missing YAML frontmatter' in e], errors)

    def test_registry_parses_every_row(self):
        rules, prefixes, _, _, errors = parse_registry(REGISTRY)
        self.assertEqual(errors, [])
        self.assertIn('PHENO-', prefixes)
        # Every row the file lists must survive parsing. A parser that drops
        # rows reports a clean run on an incomplete registry.
        listed = REGISTRY.read_text(encoding='utf-8').count('\n| `KB-')
        self.assertEqual(len(rules), listed)
        for entry in rules.values():
            self.assertIn(entry['status'], {'shipped', 'reserved'})

    def test_every_trigger_is_in_the_vocabulary(self):
        _, _, _, vocabulary, errors = parse_registry(REGISTRY)
        self.assertEqual(errors, [])
        self.assertTrue(vocabulary)
        self.assertEqual(sorted(vocabulary), sorted(set(vocabulary)))
        used = set()
        for path in (ROOT / 'conventions').rglob('*.md'):
            text = path.read_text(encoding='utf-8-sig')
            if not text.startswith('---'):
                continue
            fm = yaml.safe_load(text.split('---', 2)[1]) or {}
            if fm.get('type') == 'convention':
                used |= set(fm.get('triggers') or [])
        self.assertEqual(used - set(vocabulary), set())

    def test_trigger_outside_the_vocabulary_is_rejected(self):
        # The whole point of closing the list is that closure is enforced.
        # Each case is a way an open value creeps back: invented wording, a
        # leftover from the pre-closure vocabulary, and a plain typo, which
        # would otherwise become a term that no other rule can ever share.
        victim = 'core/Approval before destructive or published changes.md'
        cases = {
            'invented': lambda t: t.replace('  - version-control', '  - git-stuff'),
            'pre-closure leftover':
                lambda t: t.replace('  - destructive-op', '  - breaking-change'),
            'typo': lambda t: t.replace('  - version-control', '  - version-controls'),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as tmp:
                    tree = Path(tmp) / 'conventions'
                    shutil.copytree(ROOT / 'conventions', tree)
                    target = tree / victim
                    target.write_text(mutate(target.read_text(encoding='utf-8')),
                                      encoding='utf-8')
                    errors = [str(e) for e in validate(tree)]
                    self.assertTrue([e for e in errors if 'vocabulary' in e], errors)

    def test_index_carries_every_rule_and_its_headline(self):
        # The index exists so that no task has to be classified before the
        # rules can be found, which only works if it is complete: a rule with
        # no headline is invisible in exactly the situation the index is for.
        index = build_index(ROOT / 'conventions')
        self.assertNotIn('# missing a one-line version', index)
        self.assertNotIn('(no one-line version)', index)
        rules, _, _, _, _ = parse_registry(REGISTRY)
        shipped = {i for i, r in rules.items() if r['status'] == 'shipped'}
        for rule_id in shipped:
            self.assertIn(rule_id, index)
        self.assertEqual(len(index.splitlines()), len(shipped))

    def test_index_reports_a_rule_with_no_headline(self):
        # Silence here would be the worst outcome: an incomplete index that
        # looks complete sends the agent on with rules it never saw.
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / 'conventions'
            shutil.copytree(ROOT / 'conventions', tree)
            victim = tree / 'core' / 'Do not invent facts or thresholds.md'
            text = victim.read_text(encoding='utf-8')
            # Past the cap the opening paragraph is prose, not a headline.
            victim.write_text(text.rstrip() + ' padding.' * 60 + '\n',
                              encoding='utf-8')
            index = build_index(tree)
            self.assertIn('# missing a one-line version: KB-EVIDENCE-001', index)

    def test_headline_joins_a_multi_line_blockquote(self):
        text = (
            '---\ntype: convention\n---\n\n'
            '## 一句話版\n\n> 第一行，\n> 第二行。\n\n## 下一節\n\n> 不該被吃進來\n'
        )
        self.assertEqual(headline(text), '第一行， 第二行。')
        self.assertIsNone(headline('---\ntype: convention\n---\n\n## 別的\n\n> x\n'))

    def test_trigger_retrieval_ignores_tags_and_survives_crlf(self):
        # The two obvious greps for this are both wrong, in opposite
        # directions: `^  - term$` misses CRLF files, and it also matches the
        # same word sitting in `tags`. Retrieval that quietly returns the
        # wrong set is worse than none - the agent reads rules it was not
        # given and misses the ones it was.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = (
                '---\ntype: convention\nrule_id: KB-EVIDENCE-001\n'
                'applies_to: [all-agents]\n'
                'tags:\n  - verification\n'
                'triggers:\n  - claim-writing\n'
                'enforcement: review\nseverity: error\nstatus: active\n---\n本文\n'
            )
            (root / 'tagged.md').write_bytes(note.encode('utf-8'))

            crlf = note.replace('KB-EVIDENCE-001', 'KB-VERIFY-001')
            crlf = crlf.replace('  - claim-writing', '  - verification')
            (root / 'crlf.md').write_bytes(crlf.replace('\n', '\r\n').encode('utf-8'))

            hits = rules_for_trigger(root, 'verification')
            self.assertEqual([r for r, _ in hits], ['KB-VERIFY-001'])
            self.assertEqual(
                [r for r, _ in rules_for_trigger(root, 'claim-writing')],
                ['KB-EVIDENCE-001'])
            self.assertEqual(rules_for_trigger(root, 'note-write'), [])

    def test_scope_is_no_longer_required(self):
        # scope carried 51 distinct values across 51 rules, 75% of them used
        # once: it duplicated triggers at worse quality and was dropped.
        for path in (ROOT / 'conventions').rglob('*.md'):
            text = path.read_text(encoding='utf-8-sig')
            if not text.startswith('---'):
                continue
            fm = yaml.safe_load(text.split('---', 2)[1]) or {}
            if fm.get('type') == 'convention':
                self.assertNotIn('scope', fm, path.name)

    def test_registry_is_not_validated_as_a_convention(self):
        # It sits among the Convention notes and has no rule_id of its own.
        errors = [str(e) for e in validate(ROOT / 'conventions')]
        self.assertFalse([e for e in errors if 'registry.md' in e], errors)

    def test_malformed_registry_rows_are_rejected(self):
        # Each mutation is a way the table can rot. A Markdown table has no
        # schema, so every one of these has to be caught by hand or the
        # registry can silently mean less than it says.
        cases = {
            'short row': lambda t: t.replace(
                '| 變更提交前核准 | shipped | core | — |', '| shipped | core | — |'),
            'duplicate id': lambda t: t.replace('| `KB-COLLAB-001` |', '| `KB-CHANGE-001` |', 1),
            'unknown status': lambda t: t.replace(
                '| 變更提交前核准 | shipped |', '| 變更提交前核准 | draft |'),
            'malformed id': lambda t: t.replace('| `KB-CHANGE-001` |', '| `KB-CHANGE-1` |'),
            'two links in one row': lambda t: t.replace(
                '| 變更提交前核准 | shipped |', '| [[變更提交前核准]] | shipped |'),
            'no rule table': lambda t: t.replace('| rule_id |', '| ruleid |'),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as tmp:
                    errors = validate(mutated_tree(tmp, mutate), strict=True)
                    self.assertTrue(errors, label)

    def test_registry_links_must_match_the_notes(self):
        cases = {
            'shipped rule left unlinked': lambda t: t.replace(
                '[[Approval before destructive or published changes]]',
                'Approval before destructive or published changes'),
            'link with no note behind it': lambda t: t.replace(
                '| Literature search completeness |', '| [[Literature search completeness]] |'),
            'link points at another note': lambda t: t.replace(
                '[[Approval before destructive or published changes]]', '[[Some other note]]'),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as tmp:
                    tree = mutated_tree(tmp, mutate)
                    # Link drift is a property of this tree, so it is opt-in:
                    # a subset of the packs would report every absent note.
                    self.assertEqual(validate(tree), [], label)
                    self.assertTrue(validate(tree, strict=True), label)

    def test_adapters_carry_the_agents_import(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'adapters'
            setup_v2.create_vault(cfg, target)
            for name in ('CLAUDE.md', 'GEMINI.md', 'AgentRules.md'):
                text = (target / name).read_text(encoding='utf-8')
                self.assertTrue(text.startswith('@AGENTS.md'), name)


class VaultLayoutTests(unittest.TestCase):
    def test_generated_vault_has_no_domain_prefix(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        cfg['modules']['paper_pipeline'] = True
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'unprefixed'
            setup_v2.create_vault(cfg, target)
            prefixed = [p.name for p in target.rglob('*') if p.name.startswith('OV-')]
            self.assertEqual(prefixed, [])
            self.assertNotIn('OV-', all_text(target))
            for name in cfg['domains']:
                self.assertTrue((target / name / 'Map').is_dir(), name)


class VaultHealthTests(unittest.TestCase):
    def test_frontmatter_aliases_resolve_as_link_targets(self):
        sys.path.insert(0, str(ROOT / 'framework'))
        import config
        import vault_health

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'vault_config.yaml').write_text('domains:\n  Demo:\n    keywords: []\n', encoding='utf-8')
            notes = root / 'Demo' / 'Note'
            notes.mkdir(parents=True)
            (notes / 'Canonical.md').write_text(
                '---\naliases:\n  - Old Name\n---\nbody\n', encoding='utf-8'
            )
            original = vault_health.VAULT_ROOT
            try:
                vault_health.VAULT_ROOT = str(root)
                index = vault_health.build_vault_index()
            finally:
                vault_health.VAULT_ROOT = original
            self.assertIn('Canonical', index)
            self.assertIn('Old Name', index)
            self.assertNotIn('Missing', index)


if __name__ == '__main__':
    unittest.main()
