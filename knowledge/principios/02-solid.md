# SOLID em Apex

Os cinco princípios (Robert C. Martin) tornam o design compreensível, flexível e sustentável. Não são leis: aplicá-los às cegas gera complexidade sem ganho. Use-os para **diagnosticar** dores reais.

## S — Responsabilidade única
Uma classe deve ter **uma razão para mudar**. Sinal de violação: a classe é difícil de nomear sem "E" ("valida E envia E salva"), muda por motivos de áreas diferentes, ou o teste exige montar meio mundo.

```apex
// ❌ Gera PDF, envia e-mail e grava log
public class InvoiceManager { /* ... */ }

// ✅ Cada razão de mudança em sua classe
public class InvoicePdfBuilder { public Blob build(Invoice__c invoice) { /* ... */ return null; } }
public class InvoiceMailer { public void send(Invoice__c invoice, Blob pdf) { /* ... */ } }
public class InvoiceRepository extends AbstractRepository { /* ... */ }
```
No Salesforce: Trigger → Handler → Filter/Validator/Enricher/Repository é SRP aplicado.

## O — Aberto/fechado
Aberto para extensão, fechado para modificação. Nova variação = **nova classe**, não novo `else if`.

```apex
public interface DiscountPolicy {
    Boolean appliesTo(Opportunity opportunity);
    Decimal discountFor(Opportunity opportunity);
}

public class DiscountService {
    private final List<DiscountPolicy> policies;

    public DiscountService(List<DiscountPolicy> policies) {
        this.policies = policies;
    }

    public Decimal discountFor(Opportunity opportunity) {
        Decimal total = 0;
        for (DiscountPolicy policy : policies) {
            if (policy.appliesTo(opportunity)) {
                total += policy.discountFor(opportunity);
            }
        }
        return total;
    }
}
// Nova política = nova classe registrada em Custom Metadata; DiscountService não muda.
```
Não force OCP em código que nunca varia — só quando a variação é real.

## L — Substituição de Liskov
A subclasse deve poder substituir a mãe **sem quebrar o cliente**:
- parâmetros de métodos sobrescritos não podem ser mais restritivos; retornos não podem ser mais genéricos;
- não lance exceções que a mãe não lançaria (o cliente não as trata);
- não fortaleça pré-condições nem enfraqueça pós-condições;
- preserve invariantes e não altere atributos privados da mãe por fora.

```apex
// ❌ ReadOnlyRepository extends AbstractRepository e lança exceção em save() → quebra quem espera persistir.
// ✅ Separe o contrato: ReadableRepository (find*) e WritableRepository (save/remove).
```
Mocks por herança só são seguros porque respeitam LSP: o Fake se comporta como o real do ponto de vista do cliente.

## I — Segregação de interface
Clientes não devem depender de métodos que não usam. Prefira interfaces pequenas.

```apex
// ❌ Uma interface gorda que todo provedor de integração precisa implementar por inteiro
public interface ErpGateway {
    void sendOrder(Order order);
    void sendInvoice(Invoice__c invoice);
    void syncStock(List<Product2> products);
}

// ✅ Capacidades separadas; cada provedor implementa só o que suporta
public interface OrderSender { void sendOrder(Order order); }
public interface InvoiceSender { void sendInvoice(Invoice__c invoice); }
public interface StockSynchronizer { void syncStock(List<Product2> products); }
```
Não fragmente demais: interfaces de um método para tudo também viram ruído.

## D — Inversão de dependência
Módulos de alto nível (regras de negócio) não dependem de baixo nível (banco, HTTP); ambos dependem de abstrações — e a abstração pertence ao alto nível.

```apex
public interface PaymentGateway {
    PaymentResult charge(Decimal amount, String token);
}

public inherited sharing class CheckoutService {
    @TestVisible PaymentGateway gateway = (PaymentGateway) Type.forName(
        PaymentSettings__mdt.getInstance('Default').GatewayClass__c
    ).newInstance();

    public PaymentResult checkout(Order order, String token) {
        return gateway.charge(order.TotalAmount, token);
    }
}
```
Em Apex não há container de DI nativo: use **construtor/atributo injetável** + `Type.forName` com Custom Metadata para o "composition root". Nos testes, injete um Stub.
