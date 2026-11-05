/**
 * Command: uma ação encapsulada como objeto (parâmetros no construtor).
 * Implementações devem ter estado serializável para poderem ser enfileiradas (CommandQueue).
 */
public interface Command {
    void execute();
}
