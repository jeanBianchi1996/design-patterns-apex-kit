---
description: Monta (e, se aprovado, executa) um plano de refatoração segura rumo aos padrões adequados
argument-hint: <arquivo ou classe>
---

Refatore com segurança: $ARGUMENTS

Use o agente `refactoring-specialist` com a skill `refactor-to-patterns`:
1. Smells encontrados (com evidência e saída do `design_smells.py`).
2. Plano numerado: técnica de refatoração + arquivos + teste que protege cada passo.
3. Peça confirmação antes de executar se o plano tocar mais de 3 classes; caso contrário, execute.
4. Ao final: antes/depois, testes, riscos remanescentes.
