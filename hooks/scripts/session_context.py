#!/usr/bin/env python3
"""
SessionStart: em projetos Salesforce, lembra o Claude de aplicar padrões de projeto e SOLID com critério.
Silencioso fora de projetos Salesforce (sem sfdx-project.json / force-app).
"""
import os
import sys
from pathlib import Path

# Windows: garante UTF-8 na saída (acentos nas mensagens dos hooks)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


CONTEXT = """\
[design-patterns-apex-kit ativo] Ao desenhar ou alterar Apex, aplique SOLID e padrões GoF COM CRITÉRIO:
- Diagnostique pelo sintoma: if/switch escolhendo classe → Factory Method; algoritmo variável → Strategy;
  switch on Status repetido → State; etapas sequenciais que podem parar → Chain of Responsibility;
  vários módulos reagindo a evento → Observer (Platform Events entre transações); ação a enfileirar/reexecutar → Command (Queueable);
  log/retry/cache combináveis → Decorator; cache/controle de acesso → Proxy; contrato externo → Adapter;
  orquestração repetida → Facade (Service); fluxo fixo com etapas variáveis → Template Method; árvore E/OU → Composite.
- Bulk sempre: interfaces recebem listas; nada de SOQL/DML por registro dentro de estratégias/handlers/visitors.
- Variação por configuração: Custom Metadata + TypeResolver.newInstance(nome, Interface.class) (OCP real).
- Dependências injetáveis (DIP) e testáveis; não aplique padrão sem dor real (evite martelo dourado).
Guia: $KIT/knowledge/00-como-escolher-um-padrao.md. O hook design_smells comenta cada .cls salvo.
"""


def main() -> int:
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    salesforce = (root / "sfdx-project.json").exists() or (root / "force-app").is_dir()
    if os.environ.get("DESIGN_KIT_DISABLE") == "1" or not salesforce:
        return 0
    kit = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).resolve().parents[2]))
    print(CONTEXT.replace("$KIT", kit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
