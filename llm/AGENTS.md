<!-- design-patterns-apex-kit:start -->
# Padrões de projeto e SOLID no Apex (design-patterns-apex-kit)

Ao desenhar ou alterar código Apex neste repositório, aplique os princípios abaixo **com critério**: padrão só quando resolve uma dor real.

## Princípios
- **SOLID**: uma razão para mudar por classe; nova variação = nova classe (não novo `else if`); subclasses substituíveis; interfaces pequenas; regras de negócio dependem de abstrações injetáveis.
- **Encapsule o que varia**, **programe para interfaces**, **prefira composição a herança** (herança só para "é um" e ganchos de framework).

## Do sintoma ao padrão
| Sintoma | Padrão |
|---|---|
| `if/switch` decide qual classe instanciar | Factory Method (+ Custom Metadata + `TypeResolver`) |
| Objetos de um mesmo fornecedor/família usados juntos | Abstract Factory |
| Montagem com muitos opcionais (HttpRequest, SOQL, dados de teste) | Builder |
| Copiar modelos/registros | Prototype (`SObject.clone`) |
| Mesmo dado/describe recalculado na transação | Singleton por transação / Flyweight |
| Contrato externo diferente do domínio | Adapter (Transformer) |
| Hierarquia em duas dimensões | Bridge |
| Árvore (kits, regras E/OU) | Composite |
| Log/retry/cache combináveis | Decorator |
| Cache/lazy/controle de acesso transparente | Proxy |
| Orquestração repetida em LWC/REST/Flow | Facade (Service) |
| Etapas sequenciais que podem parar | Chain of Responsibility (`ChainHandler`) |
| Ação a enfileirar/reexecutar/desfazer | Command (`CommandQueue`; Queueable) |
| Fonte não-SOQL em Batch / travessia complexa | Iterator (`Iterable`) |
| Serviços em teia coordenando um processo | Mediator |
| Desfazer em memória | Memento (`Savepoint` para o banco) |
| Vários módulos reagindo a um evento | Observer (`DomainEventPublisher`; Platform Events entre transações) |
| `switch on Status` repetido | State |
| Algoritmo variável escolhido por config | Strategy |
| Mesmo esqueleto com etapas diferentes | Template Method |
| Muitas operações sobre tipos estáveis | Visitor |

## Regras de implementação em Apex
1. Bulk: interfaces recebem coleções; dados pré-carregados; nada de SOQL/DML/callout por item.
2. Injeção por construtor/atributo `@TestVisible`; variações resolvidas por Custom Metadata com `TypeResolver.newInstance(nome, Interface.class)` e teste que instancia todas as classes configuradas.
3. `inherited sharing` nas classes do padrão; o ponto de entrada decide o sharing.
4. Estado compartilhado imutável; `static` = cache por transação.
5. Prefira o que a plataforma já oferece: Queueable (Command), Platform Events (Observer), Savepoint (Memento), `clone` (Prototype), `Iterable` (Iterator).
6. Não aplique padrão sem dor real; código simples num único lugar é aceitável.

## Ferramentas do kit
- Guia: `<kit>/knowledge/00-como-escolher-um-padrao.md` (+ um arquivo por padrão em `criacionais/`, `estruturais/`, `comportamentais/`)
- Detector de design smells: `python3 <kit>/hooks/scripts/design_smells.py force-app`
- Classes reutilizáveis: `<kit>/templates/classes/` (TypeResolver, Command, CommandQueue, ChainHandler, DomainEventSubscriber, DomainEventPublisher)
<!-- design-patterns-apex-kit:end -->
