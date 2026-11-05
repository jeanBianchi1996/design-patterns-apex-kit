---
name: refactor-to-patterns
description: Refatora código Apex legado com segurança, identificando code smells e conduzindo, em passos pequenos e testados, para o design/padrão adequado (Strategy, State, Factory, Template Method, Chain, Decorator, Facade...). Use quando pedirem para refatorar, limpar, melhorar ou "deixar extensível" código existente.
---

# Refatoração rumo a padrões

## Regras
- **Comportamento preservado**: refatorar não muda o que o código faz. Bug encontrado → registre e pergunte antes de corrigir.
- **Rede de proteção primeiro**: testes de caracterização (mesmo integrados e lentos) antes da primeira mudança.
- **Passos pequenos**, cada um compilável e com testes verdes. Nada de "big bang".
- **Padrão só se a dor justificar**; às vezes extrair método e renomear basta.

## Procedimento
1. Rode `python3 <kit>/hooks/scripts/design_smells.py <arquivo>` e leia o código; liste os smells com evidência.
2. Consulte `knowledge/refatoracao/code-smells-para-padroes.md` (raiz do plugin) para o caminho smell → técnica → padrão.
3. Monte o **plano** numerado (cada passo: técnica de refatoração + arquivo + teste que garante).
4. Execute passo a passo: renomear → extrair método → extrair classe → introduzir interface → mover variação para estratégias/estados → injetar dependências → substituir condicional por polimorfismo.
5. Troque testes integrados por mockados nas classes extraídas (mais rápidos); mantenha 1 teste integrado de ponta a ponta.
6. Remova código morto e indireções que sobraram.
7. Entregue antes/depois (estrutura, métricas do `design_smells`, impacto em testes e limites).

## Exemplos de caminhos frequentes em Apex
| De | Para |
|---|---|
| `if (carrier == 'X') ... else if ...` em serviço | interface `FreightCalculator` + uma classe por transportadora + resolução por Custom Metadata (Strategy + Factory) |
| `switch on order.Status` em 4 classes | State com transições explícitas, usado pelo Validator |
| 5 Batches de integração com o mesmo fluxo | `AbstractSyncBatch` (Template Method) + subclasses pequenas |
| Serviço com log/retry/medição misturados no método de callout | `ErpClient` + Decorators empilháveis |
| Controllers LWC/REST/Invocable duplicando orquestração | Facade (Service) chamada pelos três |
| Aprovação por alçada em `if` aninhado | Chain of Responsibility (`ChainHandler`) |
| Handler de trigger que cresce a cada módulo interessado | Observer (`DomainEventPublisher` + assinantes configuráveis) |

Se o projeto usa o *salesforce-apex-patterns-kit*, mantenha os papéis dele (Repository, Filter, Validator, Enricher, TriggerHandler) como destino da refatoração estrutural.
