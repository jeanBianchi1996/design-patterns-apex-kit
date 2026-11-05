---
name: solid-review
description: Avalia código Apex contra os princípios SOLID e de bom projeto (encapsule o que varia, programe para interface, composição sobre herança), apontando violações concretas com correção. Use em revisões de design, quando uma classe está difícil de estender/testar, ou quando pedirem análise SOLID.
---

# Revisão SOLID para Apex

## Checklist (aplique classe a classe)
**S — Responsabilidade única**
- A classe tem um nome sem "E"? Quantos motivos diferentes a fariam mudar? (banco, regra, integração, UI, formato)
- Métodos públicos falam do mesmo assunto?

**O — Aberto/fechado**
- Uma nova variação (tipo, canal, país, fornecedor) exige editar `if/switch` existentes? Onde?
- Existe ponto de extensão (interface + configuração)?

**L — Liskov**
- Subclasses lançam exceções que a mãe não lança, ignoram métodos (`throw new UnsupportedOperationException`) ou mudam pré/pós-condições?
- Mocks por herança se comportam como o real do ponto de vista do cliente?

**I — Segregação de interface**
- Implementações deixam métodos vazios/stub por não precisarem deles?

**D — Inversão de dependência**
- Regras de negócio instanciam diretamente Repository/HTTP/serviços concretos dentro de métodos?
- A abstração pertence ao módulo de alto nível? Há como injetar um stub no teste?

**Princípios de bom projeto**
- O que varia está encapsulado? Dependências são de contratos? Herança foi usada só para "é um"?

## Ferramenta de apoio
```bash
python3 <kit>/hooks/scripts/design_smells.py <caminho>
```
(DSN001 método longo, DSN002 classe grande, DSN003 muitos parâmetros, DSN004/005 condicionais que pedem polimorfismo, DSN006 instanceof, DSN007 utilitário estático gigante, DSN008 dependência concreta em método, DSN009 literais repetidos, DSN010 parâmetro booleano de controle.)

## Formato
Para cada violação: **princípio** · `arquivo:linha` · evidência · impacto (teste, extensão, risco) · correção proposta com código Apex · padrão relacionado (se houver). Termine com a ordem recomendada de refatoração (maior ganho com menor risco primeiro). Referência: `knowledge/principios/01-bom-projeto.md`, `knowledge/principios/02-solid.md`.
