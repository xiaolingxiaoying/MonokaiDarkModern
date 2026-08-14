from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEME = ROOT / "Monokai Dark Modern.sublime-color-scheme"


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scheme = json.loads(SCHEME.read_text(encoding="utf-8"))
        cls.rules = cls.scheme["rules"]

    def test_required_resources_exist(self):
        names = {"Monokai Dark Modern.sublime-theme", "Monokai Dark Modern.sublime-commands", "Main.sublime-menu", "monokai_dark_modern.py", "theme-build-report.json", "LICENSE", "README.md"}
        self.assertFalse([name for name in names if not (ROOT / name).is_file()])

    def test_interaction_palette_is_fixed(self):
        expected = {"background": "#242422", "selection": "#3A514A", "selection_border": "#3A514A", "line_highlight": "#2C2D29", "caret": "#F4F1DE", "brackets_foreground": "#A9D2C3", "find_highlight": "#C9A55A", "misspelling": "#FF6188"}
        self.assertEqual({key: self.scheme["globals"][key] for key in expected}, expected)

    def test_ui_theme_uses_warm_black_and_teal(self):
        theme = json.loads((ROOT / "Monokai Dark Modern.sublime-theme").read_text(encoding="utf-8"))
        text = json.dumps(theme)
        self.assertIn("#171815", text)
        self.assertIn("#5E9A8A", text)
        self.assertIn('"file_tab_style": "rounded"', text)
        rounded_tabset = next(rule for rule in theme["rules"] if rule.get("class") == "tabset_control" and rule.get("settings", {}).get("file_tab_style") == "rounded")
        self.assertEqual({key: rounded_tabset[key] for key in ("tab_overlap", "tab_height", "connector_height")}, {"tab_overlap": 10, "tab_height": 32, "connector_height": 2})
        unselected_tab = next(rule for rule in theme["rules"] if rule.get("class") == "tab_control" and "!selected" in rule.get("attributes", []))
        self.assertEqual(unselected_tab["layer1.tint"], "#1F201D")

    def test_extensions_and_semantics_are_present(self):
        scopes = " ".join(rule.get("scope", "") for rule in self.rules)
        for scope in ("entity.name.function", "entity.name.interface", "meta.mapping.key", "string.regexp", "support.function.general.latex", "meta.semantic-token.function", "meta.semantic-token.property.readonly"):
            self.assertIn(scope, scopes)

    def test_every_generated_rule_has_provenance(self):
        report = json.loads((ROOT / "theme-build-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["generated_rule_count"], len(self.rules))
        self.assertEqual(len(report["provenance"]), len(self.rules))
        self.assertTrue(all(item.get("source") for item in report["provenance"]))

    def test_styles_and_runtime_are_safe(self):
        allowed = {"bold", "italic", "glow", "underline", "stippled_underline", "squiggly_underline"}
        for rule in self.rules:
            self.assertFalse(set(rule.get("font_style", "").split()) - allowed)
        plugin = (ROOT / "monokai_dark_modern.py").read_text(encoding="utf-8")
        self.assertFalse([text for text in ("on_modified", "add_regions(", "find_all(") if text in plugin])

    def test_check_mode_does_not_write_outputs(self):
        before = (SCHEME.read_bytes(), (ROOT / "theme-build-report.json").read_bytes())
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "build_theme.py"), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, (SCHEME.read_bytes(), (ROOT / "theme-build-report.json").read_bytes()))


if __name__ == "__main__":
    unittest.main()
