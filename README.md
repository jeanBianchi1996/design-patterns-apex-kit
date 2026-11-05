# design-patterns-apex-kit

Kit plugável com os **22 padrões de projeto GoF**, **SOLID** e **refatoração** aplicados a **Apex/Salesforce**: base de conhecimento, skills, agentes, comandos, hook que detecta design smells, regras para LLMs e classes reutilizáveis.

Base conceitual: livro *Mergulho nos Padrões de Projeto* (Alexander Shvets, Refactoring.Guru), reescrito com palavras próprias e com **todos os exemplos em Apex** (o livro usa pseudocódigo), considerando limites de governança, bulkificação, Custom Metadata e o que a plataforma já oferece.

> Complementa o [`salesforce-apex-patterns-kit`](https://github.com/jeanBianchi1996/salesforce-apex-patterns-kit) (arquitetura em camadas: TriggerHandler, Repository, Filter, Enricher, integrações, testes). Os dois funcionam juntos no mesmo projeto.

## O que vem no kit

| Pasta | Conteúdo |
|---|---|
| `knowledge/00-como-escolher-um-padrao.md` | Guia sintoma → padrão, padrões que a plataforma já implementa, combinações comuns |
| `knowledge/principios/` | Bom projeto (encapsular o que varia, interfaces, composição), SOLID com exemplos Apex, padrões × limites do Apex |
| `knowledge/criacionais/` | Factory Method, Abstract Factory, Builder, Prototype, Singleton |
| `knowledge/estruturais/` | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| `knowledge/comportamentais/` | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor |
| `knowledge/refatoracao/` | Code smells → técnicas → padrões, smells específicos de Salesforce, sequência segura |
| `skills/` | `design-pattern-selector`, `apex-design-patterns`, `solid-review`, `refactor-to-patterns` |
| `agents/` | `design-patterns-architect`, `refactoring-specialist`, `solid-reviewer` |
| `commands/` | `/pattern-suggest`, `/pattern-apply`, `/solid-review`, `/refactor-plan` |
| `hooks/` | **SessionStart**: lembra os critérios em projetos Salesforce · **PostToolUse**: `design_smells` analisa cada `.cls` salvo e sugere o padrão (não bloqueia; `DESIGN_KIT_STRICT=1` bloqueia) |
| `templates/classes/` | `TypeResolver`, `Command`, `CommandQueue`, `ChainHandler`, `DomainEventSubscriber`, `DomainEventPublisher` + testes |
| `llm/AGENTS.md` | Regras universais para qualquer LLM (Claude Code, Codex, Cursor, Copilot…) |

Cada padrão traz: intenção, problema típico no Salesforce, solução, diagrama Mermaid, implementação Apex, teste, quando usar/evitar, prós e contras, relações e onde a plataforma já o oferece.

## Como usar em um projeto

### Opção A — Plugin do Claude Code
```bash
# dentro do Claude Code (repo privado: autentique-se no GitHub antes, ex.: gh auth login)
/plugin marketplace add jeanBianchi1996/design-patterns-apex-kit
/plugin install design-patterns-apex-kit@jean-design-patterns-kit
```

### Opção B — Vendorizar no projeto (time inteiro, qualquer LLM)
```bash
git clone git@github.com:jeanBianchi1996/design-patterns-apex-kit.git ~/kits/design-patterns-apex-kit
python3 ~/kits/design-patterns-apex-kit/scripts/install_into_project.py /caminho/do/projeto --with-classes --ci
# opcional, para Claude Code sem o plugin:
python3 ~/kits/design-patterns-apex-kit/scripts/install_into_project.py /caminho/do/projeto --claude-hooks
```
Cria `.design-kit/`, mescla as regras em `AGENTS.md` (convive com o bloco do kit Apex), garante `@AGENTS.md` no `CLAUDE.md`, escreve regras para Copilot e Cursor, copia as classes reutilizáveis e o workflow de CI. Idempotente.

## Detector de design smells
```bash
python3 hooks/scripts/design_smells.py force-app                 # texto
python3 hooks/scripts/design_smells.py force-app --format github # anotações no PR
```
| Regra | Smell | Sugestão |
|---|---|---|
| DSN001 | Método > 40 linhas | Extrair método / Template Method |
| DSN002 | Classe > 500 linhas ou > 25 métodos | Extrair classes (SRP) + Facade |
| DSN003 | > 4 parâmetros | Objeto-parâmetro / Builder |
| DSN004 | 4+ comparações do mesmo valor em if/else | Strategy / State / Factory Method |
| DSN005 | switch com 6+ ramos | State / Strategy / Factory Method |
| DSN006 | 3+ `instanceof` | Polimorfismo / Visitor |
| DSN007 | Util/Helper estático gigante | Separar responsabilidades, instâncias injetáveis |
| DSN008 | `new XService/Repository/...` dentro de método | Injeção de dependência (DIP) |
| DSN009 | Literal repetido 3+ vezes | Constantes / enum / State |
| DSN010 | Parâmetro booleano de controle | Dois métodos ou Strategy |

Supressão justificada: `// design-kit:ignore DSN004`.

## Windows
- **Node 22+** é obrigatório para o Salesforce CLI (ou use o instalador `.exe` do CLI, que já traz o próprio Node).
- O Claude Code no Windows usa o **Git for Windows** (Git Bash) para rodar os hooks — instale-o.
- Os hooks usam `python3` e, se ele não existir, `python`. Instale o Python 3 em python.org marcando **"Add python.exe to PATH"** e confira com `python --version` no Git Bash.
- No PowerShell, rode os scripts com `python` no lugar de `python3` e use caminhos como `$HOME\kits\...`.

## Observações
- Exemplos Apex escritos para API 62.0+ (usam `Assert`, `Comparator`, `Type.isAssignableFrom`). As classes de `templates/classes/` têm testes; valide numa scratch org antes do primeiro uso.
- Os PDFs e trechos do livro **não** fazem parte deste repositório (licença de uso pessoal do autor). Compre o livro em refactoring.guru para a leitura completa.
