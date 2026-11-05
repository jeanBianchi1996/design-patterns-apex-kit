---
name: design-pattern-selector
description: Diagnostica um problema de design em Apex/Salesforce e escolhe o padrão GoF adequado (ou decide que nenhum é necessário), com justificativa, trade-offs e desenho. Use quando houver if/switch crescendo, código difícil de estender, integração com múltiplos fornecedores, regras configuráveis, ou quando perguntarem "qual padrão usar", "como deixar isso extensível".
---

# Seleção de padrão de projeto

## Procedimento
1. **Descreva a dor em uma frase** (o que muda, com que frequência, quem sofre). Sem dor concreta → não aplique padrão; recomende a solução mais simples.
2. **Classifique a dor**:
   - *criar objetos* (qual classe, famílias compatíveis, montagem complexa, cópia, instância única) → criacionais;
   - *montar estruturas* (contratos incompatíveis, duas dimensões, árvore, comportamento empilhável, simplificar subsistema, memória, controle de acesso) → estruturais;
   - *distribuir comportamento* (etapas sequenciais, ação como objeto, travessia, coordenação, desfazer, reação a eventos, status, algoritmo variável, esqueleto fixo, operações sobre tipos estáveis) → comportamentais.
3. **Consulte a tabela de sintomas** em `knowledge/00-como-escolher-um-padrao.md` (raiz do plugin, dois níveis acima desta skill) e leia o arquivo do padrão candidato em `knowledge/<categoria>/<padrao>.md`.
4. **Verifique as restrições do Apex** (`knowledge/principios/03-padroes-e-limites-do-apex.md`): bulk, limites, `static` por transação, reflexão via `Type.forName`, ausência de generics/lambdas.
5. **Compare com 1–2 alternativas** e com "não usar padrão".

## Formato da resposta
```
### Diagnóstico
<dor em 1–2 frases + evidência no código>

### Recomendação: <Padrão> (<categoria>)
Por quê: ...
Alternativas consideradas: <Padrão B> (descartado porque ...), solução simples (suficiente se ...)

### Desenho
<diagrama Mermaid classDiagram>

### Implementação em Apex
<interfaces e classes principais; bulk; injeção; configuração por Custom Metadata quando fizer sentido>

### Testes
<como testar cada parte; stubs; teste de configuração>

### Trade-offs
✅ ... ⚠️ ...
```

## Heurísticas rápidas
- Escolha de **classe** por tipo → Factory Method. Escolha de **algoritmo** → Strategy. Comportamento por **status** com transições → State.
- Mesma interface + comportamento extra **combinável** → Decorator; extra **transparente** gerenciado pelo próprio objeto → Proxy.
- Contrato externo → Adapter (no kit Apex: Transformer).
- Sequência que pode **parar** → Chain; todos devem reagir → Observer; um coordenador conhece todos → Mediator.
- Fluxo fixo, passos variáveis, **herança** → Template Method; algoritmo inteiro variável, **composição** → Strategy.
- Use primeiro o que a plataforma já oferece (Queueable = Command, Platform Events = Observer, Savepoint = Memento, `clone` = Prototype, `Iterable` = Iterator).

Classes prontas para reutilizar (`templates/classes/`): `TypeResolver` (fábricas/estratégias configuráveis), `Command` + `CommandQueue`, `ChainHandler`, `DomainEventSubscriber` + `DomainEventPublisher`.
