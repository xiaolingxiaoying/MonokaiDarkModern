#!/usr/bin/env python3
"""Build Monokai Dark Modern from the bundled Monokai source and mappings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "Monokai.sublime-color-scheme"
OUTPUT = ROOT / "Monokai Dark Modern.sublime-color-scheme"
REPORT = ROOT / "theme-build-report.json"
LSP_ACTIVATION_BACKGROUND = "#00000101"
INTERACTION_GLOBALS = {
    "background": "#242422",
    "selection": "#3A514A",
    "selection_border": "#3A514A",
    "line_highlight": "#2C2D29",
    "caret": "#F4F1DE",
    "brackets_options": "underline",
    "brackets_foreground": "#A9D2C3",
    "bracket_contents_options": "underline",
    "bracket_contents_foreground": "#A9D2C3",
    "find_highlight": "#C9A55A",
    "find_highlight_foreground": "#171815",
    "misspelling": "#FF6188",
    "gutter_foreground": "#8A8C82",
    "gutter_foreground_highlight": "#F4F1DE",
    "guide": "#393A35",
    "active_guide": "#5E9A8A",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def rules_from_mapping(mapping: dict[str, Any], kind: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rules: list[dict[str, Any]] = []
    provenance: list[dict[str, str]] = []
    for item in mapping["rules"]:
        rule = {key: value for key, value in item.items() if key in {"name", "scope", "foreground", "background", "font_style"}}
        rules.append(rule)
        provenance.append({"kind": kind, "name": rule["name"], "scope": rule["scope"], "source": f"mappings/{kind}.json"})
    return rules, provenance


def semantic_rules(mapping: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rules = [{"name": "LSP semantic highlighting activation", "scope": "meta.semantic-token", "background": LSP_ACTIVATION_BACKGROUND}]
    provenance = [{"kind": "semantic", "name": rules[0]["name"], "scope": rules[0]["scope"], "source": "LSP activation exception"}]
    for group in mapping["groups"]:
        scope = ", ".join(f"meta.semantic-token.{token.lower()}" for token in group["tokens"])
        rules.append({"name": group["name"], "scope": scope, "foreground": group["foreground"]})
        provenance.append({"kind": "semantic", "name": group["name"], "scope": scope, "source": "mappings/semantic_tokens.json"})
    scope = ", ".join(f"meta.semantic-token.{selector}" for selector in mapping["readonly"])
    rules.append({"name": "Semantic readonly values", "scope": scope, "foreground": "var(purple)"})
    provenance.append({"kind": "semantic", "name": "Semantic readonly values", "scope": scope, "source": "mappings/semantic_tokens.json"})
    return rules, provenance


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    source = load_json(SOURCE)
    extensions = load_json(ROOT / "mappings" / "extensions.json")
    semantic = load_json(ROOT / "mappings" / "semantic_tokens.json")
    extension_rules, extension_provenance = rules_from_mapping(extensions, "extensions")
    semantic_output, semantic_provenance = semantic_rules(semantic)
    base_rules = source["rules"]
    scheme = {
        "name": "Monokai Dark Modern",
        "author": "Monokai by Sublime HQ Pty Ltd and Wimer Hazenberg; Dark Modern adaptation",
        "variables": source["variables"],
        "globals": {**source["globals"], **INTERACTION_GLOBALS},
        "rules": [*base_rules, *extension_rules, *semantic_output],
    }
    report = {
        "name": scheme["name"],
        "source": "source/Monokai.sublime-color-scheme",
        "generated_rule_count": len(scheme["rules"]),
        "provenance": [
            *({"kind": "monokai", "name": rule.get("name", ""), "scope": rule.get("scope", ""), "source": "source/Monokai.sublime-color-scheme"} for rule in base_rules),
            *extension_provenance,
            *semantic_provenance,
        ],
    }
    return scheme, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate inputs without writing output files")
    args = parser.parse_args(argv)
    try:
        scheme, report = build()
        if not args.check:
            OUTPUT.write_text(json.dumps(scheme, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
            REPORT.write_text(json.dumps(report, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Built {scheme['name']}: {report['generated_rule_count']} rules")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

