/**
 * Observer em memória: desacopla quem detecta um evento (ex.: TriggerHandler) de quem reage.
 * Assinantes podem ser registrados por código ou por configuração (nome de classe vindo de Custom Metadata).
 *
 *   DomainEventPublisher publisher = new DomainEventPublisher()
 *       .subscribe('OrderApproved', new BillingSubscriber())
 *       .subscribe('OrderApproved', 'LogisticsSubscriber');
 *   publisher.publish('OrderApproved', approvedOrders);
 */
public inherited sharing class DomainEventPublisher {

    private final Map<String, List<DomainEventSubscriber>> subscribersByEvent = new Map<String, List<DomainEventSubscriber>>();

    public DomainEventPublisher subscribe(String eventName, DomainEventSubscriber subscriber) {
        if (!subscribersByEvent.containsKey(eventName)) {
            subscribersByEvent.put(eventName, new List<DomainEventSubscriber>());
        }
        subscribersByEvent.get(eventName).add(subscriber);
        return this;
    }

    public DomainEventPublisher subscribe(String eventName, String subscriberClassName) {
        return subscribe(
            eventName,
            (DomainEventSubscriber) TypeResolver.newInstance(subscriberClassName, DomainEventSubscriber.class)
        );
    }

    public void publish(String eventName, List<SObject> records) {
        if (records == null || records.isEmpty() || !subscribersByEvent.containsKey(eventName)) {
            return;
        }
        for (DomainEventSubscriber subscriber : subscribersByEvent.get(eventName)) {
            subscriber.handle(eventName, records);
        }
    }

    public Integer countSubscribers(String eventName) {
        return subscribersByEvent.containsKey(eventName) ? subscribersByEvent.get(eventName).size() : 0;
    }
}
