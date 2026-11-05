# Refatoração: dos code smells aos padrões

> Complemento ao livro de padrões (catálogo de refatoração do Refactoring.Guru / Martin Fowler). Conteúdo próprio, focado em Apex.

Refatorar é mudar a estrutura **sem mudar o comportamento**. Sempre com rede de proteção: testes de caracterização antes, passos pequenos, testes verdes a cada passo.

## Smells mais comuns em Apex e o caminho de saída

| Smell | Como aparece em Apex | Refatoração | Padrão de destino |
|---|---|---|---|
| **Método longo** | `execute` de Batch com 200 linhas; trigger "faz tudo" | Extrair método → Extrair classe | Template Method / papéis do kit Apex |
| **Classe grande / god class** | `AccountHelper`, `Utils`, `OrderService` com 3.000 linhas | Extrair classe por responsabilidade | Facade fina + classes coesas (SRP) |
| **Switch statements** | `switch on Status`, `if (tipo == 'A')` repetidos | Substituir condicional por polimorfismo | State / Strategy / Factory Method |
| **Lista longa de parâmetros** | `createOrder(a, b, c, d, e, f, g)` | Introduzir objeto-parâmetro / preservar objeto inteiro | Builder / DTO |
| **Obsessão por primitivos** | status como `String` mágica, CPF como `String` sem validação | Substituir primitivo por objeto / constantes / enum | Value Object, State |
| **Código duplicado** | Mesma query em 5 classes; mesmo fluxo em 4 batches | Extrair método/classe; subir método para a superclasse | Repository; Template Method |
| **Mudança divergente** | Uma classe muda por motivos de áreas diferentes | Extrair classe | SRP |
| **Cirurgia com espingarda** | Uma regra nova exige mexer em 8 classes | Mover método/campo; internalizar classe | Strategy/Facade centralizando a variação |
| **Inveja de recursos** | Método que só usa dados de outra classe | Mover método | Repository/Transformer no lugar certo |
| **Grupos de dados** | `street, city, state, zip` sempre juntos | Extrair classe | DTO `Address` |
| **Hierarquias paralelas** | `SapOrderX` / `SapInvoiceX` para cada fornecedor | Mover método, colapsar hierarquia | Abstract Factory / Bridge |
| **Comentários explicando o código** | `// aqui filtra os contratos assinados` | Extrair método com nome de intenção | — |
| **Classe preguiçosa / generalidade especulativa** | Interfaces e fábricas "para o futuro" | Internalizar classe; colapsar hierarquia | Remover padrão desnecessário |
| **Cadeia de mensagens** | `a.getB().getC().getD().value` | Ocultar delegado | Facade |
| **Intimidade inapropriada** | Classe acessando atributos internos de outra (`@TestVisible` usado em produção) | Mover método/campo; encapsular | — |
| **Data class anêmica com regra espalhada** | Wrapper só com campos; regras nos controllers | Mover método para os dados | Domínio rico / Enricher |

## Smells específicos de Salesforce
| Smell | Correção |
|---|---|
| SOQL/DML em loop | Coletar Ids → uma query → `Map` indexado → uma DML (Repository + Filter) |
| `Test.isRunningTest()` em produção | Extrair gancho `protected virtual` + Mock (Template Method) |
| Lógica em trigger | TriggerHandler + papéis (kit Apex) |
| Strings mágicas de picklist/RecordType | Classe de constantes; `Schema...getRecordTypeInfosByDeveloperName()` cacheado (Singleton/Flyweight) |
| Callout síncrono depois de DML | Command assíncrono (Queueable) |
| Hard-code de Ids/URLs | Custom Metadata / Named Credential |
| Classe `static` impossível de mockar | Instância + injeção (Strategy/DIP) |

## Sequência segura de refatoração
1. **Caracterize**: testes que fixam o comportamento atual (mesmo que feio).
2. **Renomeie** para revelar intenção (barato, alto retorno).
3. **Extraia métodos** até cada método ter um nível de abstração.
4. **Extraia classes** por razão de mudança.
5. **Introduza o padrão** só onde a variação/complexidade justificar.
6. **Substitua testes integrados por mockados** nas classes extraídas (mais rápidos).
7. **Remova** código morto e indireções que sobraram.

## Técnicas de refatoração mais usadas (nomes do catálogo)
Compor métodos: Extrair Método, Internalizar Método, Extrair Variável, Substituir Temporária por Consulta, Substituir Método por Objeto-Método.
Mover recursos: Mover Método/Campo, Extrair Classe, Internalizar Classe, Ocultar Delegado.
Organizar dados: Encapsular Campo/Coleção, Substituir Número Mágico por Constante, Substituir Código de Tipo por Classe/Subclasses/State-Strategy.
Simplificar condicionais: Decompor Condicional, Consolidar Expressão Condicional, Substituir Condicional Aninhada por Cláusulas de Guarda, Substituir Condicional por Polimorfismo, Introduzir Objeto Nulo.
Simplificar chamadas: Renomear Método, Separar Consulta de Modificador, Parametrizar Método, Introduzir Objeto-Parâmetro, Substituir Construtor por Método-Fábrica.
Generalização: Subir Método/Campo, Descer Método, Extrair Superclasse/Interface, Formar Template Method, Substituir Herança por Delegação.
