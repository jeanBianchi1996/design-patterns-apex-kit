#!/usr/bin/env python3
"""
design_smells — detecta code smells em Apex e sugere o padrão/refatoração adequado.

Modos:
  CLI:   python3 design_smells.py force-app [--format text|json|github]
  Hook:  python3 design_smells.py --hook   (PostToolUse em Write|Edit; lê o JSON do Claude Code no stdin)

No modo hook os achados NÃO bloqueiam: voltam como additionalContext para a IA avaliar.
Com DESIGN_KIT_STRICT=1 viram bloqueantes (exit 2). DESIGN_KIT_DISABLE=1 desliga.
Supressão: // design-kit:ignore DSN004  (linha ou linha anterior)  |  // design-kit:ignore-file DSN001
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

# Windows: garante UTF-8 na saída (acentos nas mensagens dos hooks)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


LIMITS = {"method_lines": 40, "class_lines": 500, "methods_per_class": 25, "params": 4,
          "branches": 4, "switch_whens": 6, "instanceof": 3, "static_util_methods": 12, "repeated_literal": 3}

RULES = {
    "DSN001": "Método longo (> {method_lines} linhas). Extraia métodos com nomes de intenção; se houver etapas fixas com variações, considere Template Method.",
    "DSN002": "Classe grande (> {class_lines} linhas ou > {methods_per_class} métodos). Divida por responsabilidade (SRP); uma Facade fina pode orquestrar as partes.",
    "DSN003": "Muitos parâmetros (> {params}). Introduza objeto-parâmetro/DTO ou Builder.",
    "DSN004": "Cadeia de if/else comparando o mesmo valor ({branches}+ ramos). Substitua condicional por polimorfismo: Strategy, State ou Factory Method (+ Custom Metadata).",
    "DSN005": "switch com muitos ramos ({switch_whens}+). Se o mesmo switch existir em outras classes, use State/Strategy; se escolhe classe a instanciar, Factory Method.",
    "DSN006": "Cadeia de instanceof ({instanceof}+). Use polimorfismo; para várias operações sobre tipos estáveis, Visitor.",
    "DSN007": "Classe utilitária estática gigante ({static_util_methods}+ métodos static). God class: separe por responsabilidade e use instâncias injetáveis (DIP/testes).",
    "DSN008": "Dependência concreta criada dentro de método. Injete pelo construtor/atributo @TestVisible (DIP) para permitir Strategy/Mock.",
    "DSN009": "Literal repetido ({repeated_literal}+ vezes). Obsessão por primitivos: use constantes, enum ou State.",
    "DSN010": "Parâmetro booleano de controle. Prefira dois métodos com nomes claros ou uma Strategy.",
}

CONTROL = re.compile(r"^\s*(if|for|while|switch|catch|else|do|try|when|return|new)\b")
METHOD_DECL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:(?:public|private|protected|global|static|virtual|abstract|override|testMethod|webservice)\s+)*"
    r"([\w.<>,\[\]\s]+?)\s+(\w+)\s*\(([^)]*)\)\s*\{"
)
CONSTRUCTOR_DECL = re.compile(r"^\s*(?:(?:public|private|protected|global)\s+)?(\w+)\s*\(([^)]*)\)\s*\{")
CLASS_DECL = re.compile(r"\bclass\s+(\w+)", re.I)
CONCRETE_DEPENDENCY = re.compile(r"\bnew\s+(\w+(?:Service|Repository|Gateway|Client|Calculator|Strategy|Factory|Handler))\s*\(")
IF_EQUALS = re.compile(r"\bif\s*\(\s*([\w.]+(?:\(\))?)\s*==")
IGNORE_LINE = re.compile(r"design-kit:ignore\s+([A-Z0-9, ]+)")
IGNORE_FILE = re.compile(r"design-kit:ignore-file\s+([A-Z0-9, ]+)")


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    message: str


def strip_comments_keep_strings(source: str) -> str:
    out, i, n = [], 0, len(source)
    while i < n:
        if source.startswith("//", i):
            while i < n and source[i] != "\n":
                i += 1
        elif source.startswith("/*", i):
            i += 2
            while i < n and not source.startswith("*/", i):
                out.append("\n" if source[i] == "\n" else " ")
                i += 1
            i += 2
        elif source[i] == "'":
            j = i + 1
            while j < n and source[j] != "'":
                j += 2 if source[j] == "\\" else 1
            out.append(source[i:j + 1])
            i = j + 1
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


class SmellDetector:
    def __init__(self, path: Path, source: str):
        self.path = path
        self.raw_lines = source.split("\n")
        self.code = strip_comments_keep_strings(source)
        self.lines = self.code.split("\n")
        self.no_strings = [re.sub(r"'(?:\\.|[^'\\])*'", "''", line) for line in self.lines]
        self.is_test = bool(re.search(r"@\s*isTest\b", self.code, re.I))
        match = CLASS_DECL.search(self.code)
        self.class_name = match.group(1) if match else path.stem
        self.findings: list[Finding] = []
        self.file_ignores = {r.strip() for found in IGNORE_FILE.findall(source) for r in found.split(",")}

    def add(self, index: int, rule: str, detail: str = "") -> None:
        if rule in self.file_ignores:
            return
        for idx in (index, index - 1):
            if 0 <= idx < len(self.raw_lines):
                match = IGNORE_LINE.search(self.raw_lines[idx])
                if match and rule in [r.strip() for r in match.group(1).split(",")]:
                    return
        message = RULES[rule].format(**LIMITS)
        if detail:
            message += f" [{detail[:80]}]"
        self.findings.append(Finding(str(self.path), index + 1, rule, message))

    def methods(self):
        """Gera (indice_inicio, indice_fim, nome, parametros, eh_construtor)."""
        index = 0
        while index < len(self.no_strings):
            line = self.no_strings[index]
            if CONTROL.match(line) or "class " in line or "interface " in line:
                index += 1
                continue
            match = METHOD_DECL.match(line)
            constructor = CONSTRUCTOR_DECL.match(line)
            is_constructor = bool(constructor and constructor.group(1) in self.inner_class_names())
            if match or is_constructor:
                name = constructor.group(1) if is_constructor else match.group(2)
                params = constructor.group(2) if is_constructor else match.group(3)
                end = self.find_block_end(index)
                yield index, end, name, params, is_constructor
                index = end + 1
                continue
            index += 1

    def inner_class_names(self) -> set[str]:
        return set(CLASS_DECL.findall(self.code))

    def find_block_end(self, start: int) -> int:
        depth = 0
        for index in range(start, len(self.no_strings)):
            depth += self.no_strings[index].count("{") - self.no_strings[index].count("}")
            if depth <= 0 and index > start or (depth == 0 and "}" in self.no_strings[index]):
                return index
        return len(self.no_strings) - 1

    def run(self) -> list[Finding]:
        self.check_class_size()
        static_methods = 0
        for start, end, name, params, is_constructor in self.methods():
            body = self.no_strings[start:end + 1]
            if re.search(r"\bstatic\b", self.no_strings[start]):
                static_methods += 1
            if not self.is_test and end - start - 1 > LIMITS["method_lines"]:
                self.add(start, "DSN001", f"{name}: {end - start - 1} linhas")
            param_count = len([p for p in params.split(",") if p.strip()])
            if param_count > LIMITS["params"]:
                self.add(start, "DSN003", f"{name}: {param_count} parâmetros")
            if re.search(r"\bBoolean\s+\w+", params) and not self.is_test and param_count > 1:
                self.add(start, "DSN010", name)
            self.check_branching(start, body)
            if not is_constructor and not self.is_test:
                self.check_concrete_dependencies(start, body)
        if static_methods >= LIMITS["static_util_methods"] and re.search(r"(Util|Utils|Helper|Helpers|Manager)$", self.class_name):
            self.add(0, "DSN007", f"{self.class_name}: {static_methods} métodos static")
        if not self.is_test:
            self.check_repeated_literals()
        return sorted(self.findings, key=lambda f: (f.line, f.rule))

    def check_class_size(self) -> None:
        if self.is_test:
            return
        lines = len([l for l in self.no_strings if l.strip()])
        methods = len(list(self.methods()))
        if lines > LIMITS["class_lines"] or methods > LIMITS["methods_per_class"]:
            self.add(0, "DSN002", f"{self.class_name}: {lines} linhas, {methods} métodos")

    def check_branching(self, start: int, body: list[str]) -> None:
        subjects = Counter()
        for line in body:
            for subject in IF_EQUALS.findall(line):  # cobre "if" e "else if"
                subjects[subject] += 1
        for subject, count in subjects.items():
            if count >= LIMITS["branches"]:
                self.add(start, "DSN004", f"{subject} comparado {count}x")
        text = "\n".join(body)
        if text.count("switch on") and len(re.findall(r"^\s*when\b", text, re.M)) >= LIMITS["switch_whens"]:
            self.add(start, "DSN005")
        if len(re.findall(r"\binstanceof\b", text)) >= LIMITS["instanceof"]:
            self.add(start, "DSN006")

    def check_concrete_dependencies(self, start: int, body: list[str]) -> None:
        for offset, line in enumerate(body[1:], start=1):
            match = CONCRETE_DEPENDENCY.search(line)
            if match and match.group(1) != self.class_name:
                self.add(start + offset, "DSN008", match.group(1))
                return

    def check_repeated_literals(self) -> None:
        literals = Counter()
        first_seen: dict[str, int] = {}
        for index, line in enumerate(self.lines):
            if re.search(r"\b(static\s+final|final\s+static)\b", line):
                continue
            for literal in re.findall(r"'((?:\\.|[^'\\]){3,40})'", line):
                if re.fullmatch(r"[A-Za-z][\w ]*", literal):
                    literals[literal] += 1
                    first_seen.setdefault(literal, index)
        for literal, count in literals.items():
            if count >= LIMITS["repeated_literal"]:
                self.add(first_seen[literal], "DSN009", f"'{literal}' x{count}")


def detect(path: Path) -> list[Finding]:
    try:
        return SmellDetector(path, path.read_text(encoding="utf-8")).run()
    except (OSError, UnicodeDecodeError):
        return []


def collect(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.cls")))
        elif path.suffix == ".cls" and path.exists():
            files.append(path)
    return files


def format_text(findings: list[Finding]) -> str:
    return "\n".join(f"{f.file}:{f.line}: [{f.rule}] {f.message}" for f in findings)


def run_hook() -> int:
    if os.environ.get("DESIGN_KIT_DISABLE") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not file_path.endswith(".cls"):
        return 0
    findings = detect(Path(file_path))
    if not findings:
        return 0
    report = format_text(findings)
    if os.environ.get("DESIGN_KIT_STRICT") == "1":
        print("design-patterns-apex-kit: design smells encontrados (modo estrito):\n" + report, file=sys.stderr)
        return 2
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "Design smells detectados (avalie; aplique o padrão sugerido só se a dor for real — "
                                 "veja a skill design-pattern-selector):\n" + report,
        }
    }, ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    if "--hook" in argv:
        return run_hook()
    fmt = argv[argv.index("--format") + 1] if "--format" in argv else "text"
    targets = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--format")]
    findings = [f for path in collect(targets or ["."]) for f in detect(path)]
    if fmt == "json":
        print(json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False))
    elif fmt == "github":
        for f in findings:
            print(f"::warning file={f.file},line={f.line},title={f.rule}::{f.message}")
    else:
        if findings:
            print(format_text(findings))
        print(f"\n{len(findings)} design smell(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
