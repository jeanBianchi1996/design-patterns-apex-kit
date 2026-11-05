# Como escolher um padrão (guia de decisão para Apex)

> Fonte conceitual: *Mergulho nos Padrões de Projeto* (Alexander Shvets, Refactoring.Guru) — 22 padrões GoF. Texto próprio; exemplos e adaptações para Apex/Salesforce criados para este kit.

Um padrão é uma **solução típica para um problema recorrente** — um conceito a adaptar, não código para copiar. Cada descrição tem: intenção, problema, solução, estrutura, aplicabilidade, implementação, prós/contras e relações. Os padrões se dividem em:
- **Criacionais** — como criar objetos com flexibilidade e reuso.
- **Estruturais** — como montar objetos e classes em estruturas maiores mantendo-as flexíveis.
- **Comportamentais** — como distribuir responsabilidades e comunicar objetos.

## Comece pelo sintoma

| Sintoma no código Apex | Padrão candidato | Arquivo |
|---|---|---|
| `if/switch` escolhendo **qual classe instanciar** por tipo/canal/país | Factory Method (+ Custom Metadata + `Type.forName`) | `criacionais/factory-method.md` |
| Vários objetos que **precisam combinar** (cliente HTTP + transformers do mesmo ERP) | Abstract Factory | `criacionais/abstract-factory.md` |
| Construtor/montagem com muitos parâmetros opcionais (`HttpRequest`, SOQL dinâmico, dados de teste) | Builder | `criacionais/builder.md` |
| Criar a partir de um modelo pré-configurado / duplicar registros com filhos | Prototype (`SObject.clone`) | `criacionais/prototype.md` |
| Mesmo describe/config/consulta repetidos na transação | Singleton (por transação) | `criacionais/singleton.md` |
| Integrar API/serviço com contrato diferente do seu domínio | Adapter (= Transformer) | `estruturais/adapter.md` |
| Hierarquia crescendo em **duas dimensões** (tipo × canal) | Bridge | `estruturais/bridge.md` |
| Estrutura em árvore (kits, regras E/OU, hierarquia de contas) | Composite | `estruturais/composite.md` |
| Acrescentar log/retry/cache/métricas combináveis a um serviço | Decorator | `estruturais/decorator.md` |
| Controllers/APIs/Flows repetindo a mesma orquestração | Facade (camada de Service) | `estruturais/facade.md` |
| Heap/CPU estourando por objetos repetindo dados iguais | Flyweight | `estruturais/flyweight.md` |
| Cache, lazy load, controle de acesso transparente | Proxy | `estruturais/proxy.md` |
| Aprovação/validação em etapas sequenciais que podem parar | Chain of Responsibility | `comportamentais/chain-of-responsibility.md` |
| Ação para enfileirar, agendar, registrar, reexecutar ou desfazer | Command (`Queueable` é um Command) | `comportamentais/command.md` |
| Percorrer fonte complexa (CSV, API paginada, árvore) / Batch sem SOQL | Iterator (`Iterable` no Batch) | `comportamentais/iterator.md` |
| Serviços chamando-se em teia ao concluir um processo | Mediator | `comportamentais/mediator.md` |
| Desfazer em memória / tentativa com volta | Memento (`Savepoint` para o banco) | `comportamentais/memento.md` |
| Vários módulos reagindo a um evento; handler crescendo a cada módulo | Observer (Platform Events entre transações) | `comportamentais/observer.md` |
| `switch on Status` repetido em várias classes | State | `comportamentais/state.md` |
| Algoritmo variável (comissão, frete, distribuição) escolhido por config | Strategy | `comportamentais/strategy.md` |
| Vários batches/jobs com o mesmo esqueleto e etapas diferentes | Template Method | `comportamentais/template-method.md` |
| Muitas operações sobre uma estrutura heterogênea estável | Visitor | `comportamentais/visitor.md` |

## Regras de bom senso
1. **Problema primeiro, padrão depois.** Se você não sente a dor que o padrão resolve, não o aplique ("martelo dourado").
2. **Prefira o mais simples que resolve.** `if` num único lugar é aceitável; o mesmo `if` em cinco lugares não é.
3. **Bulk sempre**: toda interface de padrão em Apex recebe e devolve **coleções** quando opera sobre registros. Nenhuma estratégia/handler/visitor faz SOQL/DML por registro.
4. **Configuração > código** para variações: Custom Metadata + `Type.forName` dá OCP real (nova variação sem deploy do núcleo). Cubra com um teste que instancia todas as classes configuradas.
5. **Testabilidade**: dependências injetáveis (construtor ou `@TestVisible`), interfaces para tudo que fala com banco/HTTP.
6. **Nomeie pelo papel**: `...Strategy`, `...Factory`, `...Handler`, `...Decorator` quando o padrão for parte da comunicação; caso contrário, nomeie pelo domínio (`ShippingCalculator`) e documente o padrão no comentário.

## Padrões que a plataforma já implementa (use antes de reinventar)
| Padrão | Na plataforma |
|---|---|
| Command | `Queueable`, `Schedulable`, `Database.Batchable`, Platform Events |
| Observer | Triggers, Platform Events, Change Data Capture, Flow disparado por registro |
| Iterator | `Iterator<T>`, `Iterable<T>`, Batch com `Iterable` |
| Memento | `Database.setSavepoint/rollback`, `Trigger.old` |
| Prototype | `SObject.clone()`, `List.deepClone()` |
| Proxy | Stub API (`Test.createStub`), Named Credentials (proxy remoto de autenticação) |
| Template Method | `Database.Batchable` (start/execute/finish), frameworks de trigger |
| Flyweight | Custom Metadata `getAll()/getInstance()`, describes cacheados, Platform Cache |
| Factory | `Type.forName().newInstance()`, `SObjectType.newSObject()` |

## Combinações que aparecem juntas em Salesforce
- **Trigger framework** = Template Method (handler base) + Chain/Observer (ações por evento) + Strategy (regras configuráveis).
- **Integração** = Facade (Service) + Adapter (Transformer) + Builder (request) + Decorator (log/retry) + Command (Queueable).
- **Motor de regras/preço** = Composite (regras E/OU) + Strategy (cálculo) + Flyweight (tabelas de preço) + Builder (monta a árvore a partir de metadata).
