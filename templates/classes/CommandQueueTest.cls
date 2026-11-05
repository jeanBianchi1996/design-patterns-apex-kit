@IsTest
private class CommandQueueTest {

    private static List<String> executions = new List<String>();

    private class RecordingCommand implements Command {
        private final String name;
        RecordingCommand(String name) { this.name = name; }
        public void execute() { executions.add(name); }
    }

    private class InsertAccountCommand implements Command {
        private final String name;
        InsertAccountCommand(String name) { this.name = name; }
        public void execute() { insert new Account(Name = name); }
    }

    private class CommandQueueSpy extends CommandQueue {
        CommandQueue enqueued;
        CommandQueueSpy(List<Command> commands) { super(commands); }
        override protected void enqueueNext(CommandQueue next) { this.enqueued = next; }
    }

    @IsTest
    static void givenTwoCommandsWhenExecuteThenRunFirstAndEnqueueRest() {
        CommandQueueSpy queue = new CommandQueueSpy(new List<Command>{
            new RecordingCommand('primeiro'), new RecordingCommand('segundo')
        });

        queue.execute(null);

        Assert.areEqual(new List<String>{ 'primeiro' }, executions);
        Assert.isNotNull(queue.enqueued, 'O restante deve ser encadeado');
        Assert.areEqual(1, queue.enqueued.commands.size());
    }

    @IsTest
    static void givenSingleCommandWhenEnqueueThenExecuteAsync() {
        Test.startTest();
        System.enqueueJob(new CommandQueue(new List<Command>{ new InsertAccountCommand('Executado via fila') }));
        Test.stopTest();

        Assert.areEqual(1, [SELECT COUNT() FROM Account WHERE Name = 'Executado via fila']);
    }

    @IsTest
    static void givenEmptyQueueWhenExecuteThenDoNothing() {
        CommandQueueSpy queue = new CommandQueueSpy(null);

        queue.execute(null);

        Assert.isTrue(executions.isEmpty());
        Assert.isNull(queue.enqueued);
    }
}
