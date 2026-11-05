/**
 * Invoker assíncrono de Commands: executa um comando por job e encadeia os demais.
 * Permite enfileirar comandos heterogêneos (inclusive com callout) com uma única chamada.
 *
 *   System.enqueueJob(new CommandQueue(new List<Command>{ new SendOrderToErpCommand(ids), new NotifyCsCommand(ids) }));
 *
 * Em testes, sobrescreva enqueueNext (encadeamento não roda em contexto de teste).
 */
public inherited sharing virtual class CommandQueue implements Queueable, Database.AllowsCallouts {

    @TestVisible
    private final List<Command> commands;

    public CommandQueue(List<Command> commands) {
        this.commands = commands == null ? new List<Command>() : commands;
    }

    public void execute(QueueableContext context) {
        if (commands.isEmpty()) {
            return;
        }
        commands.remove(0).execute();
        if (!commands.isEmpty()) {
            enqueueNext(new CommandQueue(commands));
        }
    }

    @TestVisible
    protected virtual void enqueueNext(CommandQueue next) {
        System.enqueueJob(next);
    }
}
