# CLAUDE.md — manutenção do próprio kit

Este repositório é um plugin do Claude Code + kit vendorizável.

- Estrutura de plugin: `.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `agents/*.md`, `commands/*.md`, `hooks/hooks.json` (scripts via `${CLAUDE_PLUGIN_ROOT}`).
- Conteúdo em português, com palavras próprias — nunca copie trechos do livro.
- Cada padrão em `knowledge/<categoria>/` segue a mesma estrutura: intenção, problema no Salesforce, solução, Mermaid, implementação Apex, teste, quando usar/evitar, prós e contras, relações, plataforma.
- Exemplos Apex sempre bulk, com injeção de dependência e `inherited sharing`.
- `bash scripts/selftest.sh` precisa passar (22 padrões, frontmatter das skills, classes sem smells, detector encontrando smells no exemplo ruim).
- Mudou critérios? Atualize juntos `knowledge/00-como-escolher-um-padrao.md`, `llm/AGENTS.md`, `hooks/scripts/session_context.py` e a skill `design-pattern-selector`.
- Versione em `plugin.json` (semver).
