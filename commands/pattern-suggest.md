---
description: Diagnostica um problema de design e recomenda o padrão GoF adequado para Apex (ou nenhum)
argument-hint: <descrição do problema ou caminho do arquivo>
---

Analise: $ARGUMENTS

Use o agente `design-patterns-architect` com a skill `design-pattern-selector`. Se for um arquivo, leia-o e rode `python3 <kit>/hooks/scripts/design_smells.py` nele. Responda no formato da skill: Diagnóstico, Recomendação (com alternativas descartadas), Desenho Mermaid, Implementação Apex, Testes, Trade-offs. Se nenhum padrão se justificar, diga claramente e proponha a solução simples.
