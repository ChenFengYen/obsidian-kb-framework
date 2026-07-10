import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import setup_v2
from framework.validate_conventions import validate


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
            self.assertFalse((target / 'OV-Papers').exists())
            self.assertFalse((target / '.claude' / 'settings.local.json').exists())
            self.assertEqual(validate(target / 'OV-KnowledgeBase' / 'Convention'), [])
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
            self.assertNotIn('OV-Bioinformatics', text)
            self.assertFalse((target / 'OV-Papers').exists())
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
            self.assertFalse((target / 'OV-Papers').exists())

    def test_paper_module_installs_its_runtime_dependencies(self):
        cfg = yaml.safe_load((ROOT / 'vault_config.yaml.example').read_text(encoding='utf-8'))
        cfg['modules']['paper_pipeline'] = True
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'papers'
            setup_v2.create_vault(cfg, target)
            scripts = target / 'OV-Papers' / 'scripts'
            self.assertTrue((scripts / 'config.py').is_file())
            self.assertTrue((scripts / 'status_tracker.py').is_file())
            self.assertTrue((target / 'OV-Papers' / 'PAPER_PROCESSING_GUIDE.md').is_file())
            result = subprocess.run(
                [sys.executable, str(scripts / 'insert_figures.py'), '--help'],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
