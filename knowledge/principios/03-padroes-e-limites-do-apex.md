# Padrões × particularidades do Apex

O que muda ao trazer os padrões GoF (pensados para linguagens genéricas) para a plataforma Salesforce.

## Restrições da linguagem
| Característica do Apex | Consequência para os padrões |
|---|---|
| Sem generics em classes do usuário | Interfaces usam `Object`/`SObject` + cast, ou uma interface por tipo. `Iterator<T>`, `Comparator<T>` e coleções são exceções da plataforma. |
| Classes e métodos são finais por padrão | Para herança/Template Method/Mock por herança: `virtual`/`abstract` explícitos. |
| Sem lambdas/funções de primeira classe | Strategy/Command/Observer = classes pequenas implementando interfaces (ou inner classes). |
| Reflexão limitada (`Type.forName`, `newInstance` só com construtor sem argumentos) | Fábricas configuráveis: construtor vazio + inicialização por método (`init(config)`). |
| Herança simples | Prefira composição; use interfaces para múltiplos "papéis". |
| Sem visibilidade "friend" entre classes | Memento/encapsulamento por convenção; `@TestVisible` só para testes. |
| `static` vive por transação | Singleton = por transação; caches se renovam a cada transação/lote. |
| Serialização de Queueable | Commands enfileirados precisam de estado serializável. |

## Limites de governança guiam o design
- **Bulk em todas as interfaces**: `assign(List<Lead>)`, não `assign(Lead)`. Padrões que iteram (Chain, Visitor, Composite, Observer) recebem dados **pré-carregados**.
- **CPU (10 s / 60 s)**: muitas camadas de indireção por registro somam CPU; meça com `Limits.getCpuTime()` em cenários de 200 registros.
- **Heap (6 MB / 12 MB)**: Flyweight e Prototype raso ajudam; snapshots (Memento) e caches (Proxy) consomem.
- **Callouts após DML** proibidos: Decorators de log acumulam e gravam no fim; Commands assíncronos isolam callouts.
- **Profundidade de Queueable**: encadeamento de Commands com gancho sobrescrevível para testes.

## Configuração como ponto de extensão (OCP real)
```apex
public inherited sharing class TypeResolver {
    public static Object newInstance(String className, Type expectedType) {
        Type resolved = Type.forName(className);
        if (resolved == null) {
            throw new TypeResolverException('Classe não encontrada: ' + className);
        }
        if (!expectedType.isAssignableFrom(resolved)) {
            throw new TypeResolverException(className + ' não implementa ' + expectedType.getName());
        }
        return resolved.newInstance();
    }

    public class TypeResolverException extends Exception {}
}
```
Disponível em `templates/classes/TypeResolver.cls`. Usado por Factory Method, Strategy, Observer (assinantes) e Chain (etapas) configurados por Custom Metadata.

## Testabilidade dos padrões
- Interfaces → stubs triviais em teste (inner classes `@IsTest`).
- Stub API (`System.StubProvider` + `Test.createStub`) cria proxies dinâmicos para classes `virtual` (base do framework Mocker).
- Cada estratégia/handler/visitor tem teste próprio; o contexto é testado com stubs.
- Teste de "configuração válida": percorre o Custom Metadata e instancia todas as classes.
