/**
 * Instancia classes por nome com verificação de contrato.
 * Base de Factory Method, Strategy, Observer e Chain configurados por Custom Metadata (OCP real:
 * nova variação = nova classe + registro de metadata, sem alterar o núcleo).
 *
 *   ShippingCalculator calculator = (ShippingCalculator) TypeResolver.newInstance(
 *       ShippingSettings__mdt.getInstance('Default').CalculatorClass__c, ShippingCalculator.class);
 */
public inherited sharing class TypeResolver {

    public static Object newInstance(String className, Type expectedType) {
        if (String.isBlank(className)) {
            throw new TypeResolverException('Nome de classe não informado para ' + expectedType.getName());
        }
        Type resolvedType = Type.forName(className);
        if (resolvedType == null) {
            throw new TypeResolverException('Classe não encontrada: ' + className);
        }
        if (!expectedType.isAssignableFrom(resolvedType)) {
            throw new TypeResolverException(className + ' não implementa/estende ' + expectedType.getName());
        }
        return resolvedType.newInstance();
    }

    public class TypeResolverException extends Exception {}
}
