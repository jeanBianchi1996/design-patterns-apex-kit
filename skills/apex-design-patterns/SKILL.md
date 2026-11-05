---
name: apex-design-patterns
description: Implementa qualquer um dos 22 padrões GoF em Apex de forma idiomática para Salesforce (Factory Method, Abstract Factory, Builder, Prototype, Singleton, Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy, Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor). Use quando o padrão já foi escolhido ou foi citado pelo nome.
---

# Implementando padrões GoF em Apex

## Antes de codar
Leia o arquivo do padrão em `knowledge/` (raiz do plugin, dois níveis acima desta skill):

| Criacionais | Estruturais | Comportamentais |
|---|---|---|
| `criacionais/factory-method.md` | `estruturais/adapter.md` | `comportamentais/chain-of-responsibility.md` |
| `criacionais/abstract-factory.md` | `estruturais/bridge.md` | `comportamentais/command.md` |
| `criacionais/builder.md` | `estruturais/composite.md` | `comportamentais/iterator.md` |
| `criacionais/prototype.md` | `estruturais/decorator.md` | `comportamentais/mediator.md` |
| `criacionais/singleton.md` | `estruturais/facade.md` | `comportamentais/memento.md` |
| | `estruturais/flyweight.md` | `comportamentais/observer.md` |
| | `estruturais/proxy.md` | `comportamentais/state.md` |
| | | `comportamentais/strategy.md` |
| | | `comportamentais/template-method.md` |
| | | `comportamentais/visitor.md` |

## Regras de implementação (todas obrigatórias)
1. **Contrato primeiro**: interface (ou classe `abstract`/`virtual`) pequena e focada (ISP).
2. **Bulk**: métodos que operam registros recebem `List`/`Set`/`Map`. Dados necessários chegam **pré-carregados**; nada de SOQL/DML/callout por item.
3. **Injeção**: dependências por construtor ou atributo `@TestVisible`; construtor sem argumentos resolve o padrão de produção (configuração).
4. **Configuração**: variações escolhidas por Custom Metadata + `TypeResolver.newInstance(className, Interface.class)`; inclua teste que instancia todas as classes configuradas.
5. **Sharing**: classes internas do padrão usam `inherited sharing`; o ponto de entrada decide.
6. **Imutabilidade** onde houver compartilhamento (Flyweight, estados sem dados, estratégias sem estado → podem ser cacheadas em `static final`).
7. **Assíncrono**: Commands/Observers que fazem callout ou trabalho pesado enfileiram Queueable; estado serializável.
8. **Nomes**: pelo domínio + papel (`FreightCalculator`/`...Strategy`, `...Factory`, `...Handler`, `...Decorator`), documentando o padrão no comentário da classe.
9. **Integração com o kit Apex**: se o projeto usa o *salesforce-apex-patterns-kit*, mantenha os papéis (Repository para dados, TriggerHandler para triggers); os padrões vivem dentro das camadas de Service/Enricher/Transformer.

## Reutilize antes de escrever
`templates/classes/`: `TypeResolver`, `Command`, `CommandQueue`, `ChainHandler`, `DomainEventSubscriber`, `DomainEventPublisher` (com testes). Copie para `force-app/main/default/classes` (o instalador faz isso com `--with-classes`).

## Testes mínimos por padrão
| Padrão | Teste |
|---|---|
| Factory / Strategy configurável | instancia cada classe configurada; erro para nome inválido |
| Builder | assert por propriedade construída + `build()` inválido |
| Decorator / Proxy | comportamento extra + delegação ao objeto real (stub contador) |
| Chain | cada elo responde; requisição percorre; fim sem handler gera erro explícito |
| Command | execute isolado; enfileiramento com gancho sobrescrito |
| Observer | todos assinantes recebem o lote; evento sem assinante não falha |
| State | transições válidas e inválidas |
| Template Method | subclasse concreta passa pelo fluxo completo; ganchos padrão |
| Composite / Visitor | árvore aninhada com resultado agregado correto |
