@IsTest
public class TypeResolverTest {

    public interface Greeting {
        String greet();
    }

    public class FormalGreeting implements Greeting {
        public String greet() { return 'Prezado(a)'; }
    }

    public class NotAGreeting {}

    @IsTest
    static void givenImplementingClassWhenNewInstanceThenReturnTypedInstance() {
        Greeting greeting = (Greeting) TypeResolver.newInstance('TypeResolverTest.FormalGreeting', Greeting.class);

        Assert.areEqual('Prezado(a)', greeting.greet());
    }

    @IsTest
    static void givenUnknownClassWhenNewInstanceThenThrowException() {
        assertThrows('ClasseQueNaoExiste', 'não encontrada');
    }

    @IsTest
    static void givenClassNotImplementingContractWhenNewInstanceThenThrowException() {
        assertThrows('TypeResolverTest.NotAGreeting', 'não implementa');
    }

    @IsTest
    static void givenBlankClassNameWhenNewInstanceThenThrowException() {
        assertThrows('', 'não informado');
    }

    private static void assertThrows(String className, String expectedMessage) {
        try {
            TypeResolver.newInstance(className, Greeting.class);
            Assert.fail('Deveria lançar TypeResolverException');
        } catch (TypeResolver.TypeResolverException e) {
            Assert.isTrue(e.getMessage().contains(expectedMessage), e.getMessage());
        }
    }
}
