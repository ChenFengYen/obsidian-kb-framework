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
from framework.validate_conventions import render_table, validate


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
            shutil.copy2(ROOT / 'conventions' / 'registry.yaml', root / 'core' / 'registry.yaml')
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

    def test_partial_pack_install_still_validates(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        cfg['conventions']['packs'] = ['core']
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'partial'
            setup_v2.create_vault(cfg, target)
            conventions = target / 'KnowledgeBase' / 'Convention'
            self.assertTrue((conventions / 'registry.yaml').is_file())
            self.assertEqual(validate(conventions), [])
            data = yaml.safe_load((conventions / 'registry.yaml').read_text(encoding='utf-8'))
            shipped = {r['id'] for r in data['rules'] if r.get('status') == 'shipped'}
            self.assertIn('KB-EVIDENCE-001', shipped)      # core, installed
            self.assertNotIn('KB-LINK-001', shipped)       # obsidian, not installed
            self.assertIn('KB-LINK-001', {r['id'] for r in data['rules']})


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

    def test_registry_table_renders_every_rule(self):
        table = render_table(ROOT / 'conventions' / 'registry.yaml')
        data = yaml.safe_load((ROOT / 'conventions' / 'registry.yaml').read_text(encoding='utf-8'))
        for rule in data['rules']:
            self.assertIn(rule['id'], table)
        self.assertIn('PHENO-', table)

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
