---
description: Aplica um padrão GoF específico a um código Apex existente ou novo, com testes
argument-hint: <Padrão> <arquivo ou descrição>
---

Aplique o padrão: $ARGUMENTS

1. Leia `knowledge/<categoria>/<padrão>.md` do kit e a skill `apex-design-patterns`.
2. Se houver código existente, use a skill `refactor-to-patterns` (testes de caracterização → passos pequenos).
3. Reaproveite `templates/classes/` quando servir (TypeResolver, CommandQueue, ChainHandler, DomainEventPublisher) — copie para `force-app/main/default/classes` com `-meta.xml` se ainda não existirem.
4. Implemente bulk, injetável e (quando houver variação) configurável por Custom Metadata.
5. Escreva os testes mínimos do padrão (tabela da skill).
6. Rode `design_smells.py` nos arquivos alterados e resuma: classes criadas/alteradas, como estender (ex.: "nova transportadora = nova classe + registro de metadata"), testes.
