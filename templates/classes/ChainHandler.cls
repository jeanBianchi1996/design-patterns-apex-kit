/**
 * Chain of Responsibility: base para cadeias de processamento (aprovação por alçada,
 * pipelines de validação, roteamento). Cada handler decide se trata ou repassa.
 *
 *   ChainHandler chain = new SellerApproval();
 *   chain.setNext(new ManagerApproval()).setNext(new DirectorApproval());
 *   Object approver = chain.handle(opportunity);
 *
 * Regra Apex: a requisição pode ser uma coleção (bulk) — nunca faça SOQL/DML dentro de canHandle/process;
 * receba dados pré-carregados no construtor do handler.
 */
public abstract inherited sharing class ChainHandler {

    private ChainHandler next;

    public ChainHandler setNext(ChainHandler next) {
        this.next = next;
        return next;
    }

    public Object handle(Object request) {
        if (canHandle(request)) {
            return process(request);
        }
        if (next == null) {
            return unhandled(request);
        }
        return next.handle(request);
    }

    protected abstract Boolean canHandle(Object request);

    protected abstract Object process(Object request);

    /** Fim da cadeia sem tratamento: por padrão é erro explícito (nada "cai" silenciosamente). */
    protected virtual Object unhandled(Object request) {
        throw new UnhandledRequestException('Nenhum handler tratou a requisição: ' + String.valueOf(request));
    }

    public class UnhandledRequestException extends Exception {}
}
