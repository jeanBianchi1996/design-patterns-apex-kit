/**
 * Observer (mesma transação): assinante de eventos de domínio. Sempre bulk.
 * Para reações pesadas ou que podem falhar isoladamente, o assinante deve apenas
 * enfileirar um Command (Queueable) ou publicar um Platform Event.
 */
public interface DomainEventSubscriber {
    void handle(String eventName, List<SObject> records);
}
