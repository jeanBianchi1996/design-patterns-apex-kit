#!/usr/bin/env python3
"""
Pluga o design-patterns-apex-kit em um projeto Salesforce (SFDX) existente.

  python3 scripts/install_into_project.py /caminho/do/projeto [opções]

Sempre faz:
  - copia conhecimento e ferramentas para <projeto>/.design-kit/ (knowledge, detector de smells, templates)
  - mescla as regras em AGENTS.md (bloco entre marcadores, idempotente) e garante @AGENTS.md no CLAUDE.md
  - escreve .github/copilot-instructions.md (bloco) e .cursor/rules/design-patterns-apex.mdc

Opções:
  --with-classes   copia TypeResolver, Command, CommandQueue, ChainHandler, DomainEvent* (+ testes) para force-app
  --claude-hooks   registra os hooks em <projeto>/.claude/settings.json (para quem NÃO instalou o plugin)
  --ci             adiciona workflow GitHub Actions que comenta design smells nos PRs
  --api-version    versão de API dos -meta.xml (padrão 62.0)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
START, END = "<!-- design-patterns-apex-kit:start -->", "<!-- design-patterns-apex-kit:end -->"
VENDOR_DIR = ".design-kit"
VENDORED = ["hooks/scripts", "templates", "knowledge", "llm"]
CLASS_META = """<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>{api}</apiVersion>
    <status>Active</status>
</ApexClass>
"""
CI_WORKFLOW = """name: Design smells (Apex)

on:
  pull_request:
    paths:
      - "force-app/**/*.cls"

jobs:
  design-smells:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Design smells (design-patterns-apex-kit)
        run: python3 .design-kit/hooks/scripts/design_smells.py force-app --format github
"""


def merge_block(path: Path, block: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if pattern.search(current):
        updated = pattern.sub(lambda _: block.strip(), current)
    else:
        updated = (current.rstrip() + "\n\n" if current.strip() else "") + block.strip() + "\n"
    path.write_text(updated, encoding="utf-8")
    print(f"  regras mescladas: {path}")


def vendor(project: Path) -> None:
    target = project / VENDOR_DIR
    for item in VENDORED:
        shutil.copytree(KIT / item, target / item, dirs_exist_ok=True)
    (target / "VERSION").write_text(json.loads((KIT / ".claude-plugin/plugin.json").read_text())["version"] + "\n")
    print(f"  conhecimento e ferramentas copiados: {target}")


def ensure_claude_import(project: Path) -> None:
    claude_md = project / "CLAUDE.md"
    content = claude_md.read_text(encoding="utf-8") if claude_md.exists() else "# CLAUDE.md\n"
    if "@AGENTS.md" not in content:
        claude_md.write_text(content.rstrip() + "\n\n## Padrões do projeto\n@AGENTS.md\n", encoding="utf-8")
    print(f"  CLAUDE.md importa AGENTS.md: {claude_md}")


def write_cursor_rule(project: Path, rules: str) -> None:
    path = project / ".cursor" / "rules" / "design-patterns-apex.mdc"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "---\ndescription: Padrões de projeto e SOLID em Apex (design-patterns-apex-kit)\nglobs: \"**/*.cls\"\nalwaysApply: false\n---\n"
    path.write_text(header + rules, encoding="utf-8")
    print(f"  regra do Cursor: {path}")


def copy_classes(project: Path, api_version: str) -> None:
    target = project / "force-app" / "main" / "default" / "classes"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted((KIT / "templates" / "classes").glob("*.cls")):
        destination = target / source.name
        if destination.exists():
            print(f"  ignorado (já existe): {destination}")
            continue
        shutil.copy2(source, destination)
        Path(str(destination) + "-meta.xml").write_text(CLASS_META.format(api=api_version), encoding="utf-8")
        print(f"  criado: {destination}")


def register_claude_hooks(project: Path) -> None:
    settings_path = project / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
    hooks = settings.setdefault("hooks", {})
    smells = f'python3 "$CLAUDE_PROJECT_DIR/{VENDOR_DIR}/hooks/scripts/design_smells.py" --hook'
    context = f'python3 "$CLAUDE_PROJECT_DIR/{VENDOR_DIR}/hooks/scripts/session_context.py"'
    wanted = {
        "PostToolUse": {"matcher": "Write|Edit|MultiEdit", "hooks": [{"type": "command", "command": smells}]},
        "SessionStart": {"hooks": [{"type": "command", "command": context}]},
    }
    for event, entry in wanted.items():
        entries = hooks.setdefault(event, [])
        command = entry["hooks"][0]["command"]
        if not any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
            entries.append(entry)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  hooks registrados: {settings_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project")
    parser.add_argument("--with-classes", action="store_true")
    parser.add_argument("--claude-hooks", action="store_true")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--api-version", default="62.0")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.is_dir():
        parser.error(f"projeto não encontrado: {project}")

    print(f"Instalando design-patterns-apex-kit em {project}")
    vendor(project)
    rules = (KIT / "llm" / "AGENTS.md").read_text(encoding="utf-8").replace("<kit>", VENDOR_DIR)
    merge_block(project / "AGENTS.md", rules)
    ensure_claude_import(project)
    merge_block(project / ".github" / "copilot-instructions.md", rules)
    write_cursor_rule(project, rules)
    if args.with_classes:
        copy_classes(project, args.api_version)
    if args.claude_hooks:
        register_claude_hooks(project)
    if args.ci:
        workflow = project / ".github" / "workflows" / "design-smells.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text(CI_WORKFLOW, encoding="utf-8")
        print(f"  workflow de CI: {workflow}")
    print("Pronto. Guia: .design-kit/knowledge/00-como-escolher-um-padrao.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
