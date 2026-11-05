# Princípios de um bom projeto (aplicados a Apex)

> Fonte conceitual: *Mergulho nos Padrões de Projeto* (Alexander Shvets, Refactoring.Guru). Texto próprio; exemplos em Apex criados para este kit.

## O que é "bom projeto"
- **Reuso de código**: reduzir custo reaproveitando componentes. Em Salesforce, o maior reuso vem de camadas estáveis (Repository, Services, Transformers) e de contratos (interfaces) — não de classes utilitárias gigantes.
- **Extensibilidade**: a mudança é a única constante. Requisitos novos devem entrar **adicionando** classes, não reescrevendo as existentes (ver OCP).
- Três níveis de reuso: classes/bibliotecas (baixo), **padrões** (médio — reuso de ideias), frameworks (alto — "não nos chame, nós chamamos você", como o `TriggerHandler`).

## Encapsule o que varia
Identifique o que muda com frequência e isole do que é estável.
- **Nível de método**: extraia a regra variável (`calculateTax`) para um método próprio.
- **Nível de classe**: quando o método cresce com variações (`if país == ...`), mova para uma classe/estratégia própria.

```apex
// Antes: o cálculo de frete varia por transportadora e polui o serviço
public Decimal calculateTotal(Order order, String carrier) {
    Decimal shipping;
    if (carrier == 'CORREIOS') { shipping = order.TotalAmount * 0.05; }
    else if (carrier == 'JADLOG') { shipping = 15 + order.TotalAmount * 0.02; }
    return order.TotalAmount + shipping;
}

// Depois: o que varia vira uma estratégia; o serviço fica estável
public interface ShippingCalculator {
    Decimal calculate(Order order);
}

public Decimal calculateTotal(Order order, ShippingCalculator calculator) {
    return order.TotalAmount + calculator.calculate(order);
}
```

## Programe para uma interface, não para uma implementação
Dependa de abstrações. O cliente conhece o contrato; o concreto pode ser trocado (inclusive por um Mock).
1. Descubra o que um objeto precisa do outro.
2. Descreva esses métodos numa interface (ou classe abstrata/virtual).
3. Faça a dependência implementar o contrato.
4. Faça o cliente depender do contrato.

Em Apex isso viabiliza: estratégias configuráveis por Custom Metadata (`Type.forName(nome).newInstance()`), testes com Stub API (`Test.createStub`) e troca de fornecedores de integração.

## Prefira composição sobre herança
Herança é "é um"; composição é "tem um"/"usa um". Problemas da herança: a subclasse não pode reduzir a interface da mãe; precisa respeitar o comportamento dela (LSP); quebra o encapsulamento (conhece detalhes da mãe); acopla fortemente; e hierarquias paralelas explodem combinatoriamente (Caminhão × Carro × Elétrico × Gasolina × Autônomo × Manual...).

Com composição, cada dimensão vira um componente injetado:
```apex
public class NotificationService {
    private final MessageFormatter formatter;   // HTML, texto, Slack blocks...
    private final DeliveryChannel channel;      // e-mail, Slack, custom notification...

    public NotificationService(MessageFormatter formatter, DeliveryChannel channel) {
        this.formatter = formatter;
        this.channel = channel;
    }

    public void notify(SObject record) {
        channel.deliver(formatter.format(record));
    }
}
```
Use herança quando: a hierarquia é estável e realmente "é um" (`OrderRepository extends AbstractRepository`), ou para ganchos de framework (Template Method).
