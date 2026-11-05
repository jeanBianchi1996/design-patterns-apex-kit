---
description: Revisão de design SOLID e uso de padrões em código Apex
argument-hint: [caminho ou arquivos; padrão = alterações do git]
---

Revise o design de: $ARGUMENTS (se vazio, arquivos `.cls` alterados segundo `git diff --name-only`).

Use o agente `solid-reviewer` com a skill `solid-review` e o detector `design_smells.py`. Entregue: resumo, violações por severidade (arquivo:linha, evidência, impacto, correção em Apex), avaliação do uso de padrões e ordem recomendada de refatoração.
