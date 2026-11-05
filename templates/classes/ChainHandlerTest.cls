@IsTest
private class ChainHandlerTest {

    private class UpToLimitHandler extends ChainHandler {
        private final Decimal maxValue;
        private final String approver;

        UpToLimitHandler(Decimal maxValue, String approver) {
            this.maxValue = maxValue;
            this.approver = approver;
        }

        protected override Boolean canHandle(Object request) { return (Decimal) request <= maxValue; }
        protected override Object process(Object request) { return approver; }
    }

    private static ChainHandler buildChain() {
        ChainHandler chain = new UpToLimitHandler(5, 'vendedor');
        chain.setNext(new UpToLimitHandler(15, 'gerente')).setNext(new UpToLimitHandler(30, 'diretor'));
        return chain;
    }

    @IsTest
    static void givenValueWithinFirstLimitWhenHandleThenFirstHandlerAnswers() {
        Assert.areEqual('vendedor', buildChain().handle(3.0));
    }

    @IsTest
    static void givenValueWithinLastLimitWhenHandleThenRequestTravelsTheChain() {
        Assert.areEqual('diretor', buildChain().handle(25.0));
    }

    @IsTest
    static void givenValueAboveAllLimitsWhenHandleThenThrowUnhandled() {
        try {
            buildChain().handle(50.0);
            Assert.fail('Deveria lançar UnhandledRequestException');
        } catch (ChainHandler.UnhandledRequestException e) {
            Assert.isTrue(e.getMessage().contains('50'));
        }
    }
}
