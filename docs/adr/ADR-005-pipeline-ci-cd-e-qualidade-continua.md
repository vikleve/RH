# ADR-005: Pipeline de CI/CD e Quality Gates Automatizados

## Status
Aprovado

## Data
2026-10-28

## Contexto
Projetos interdisciplinares de software exigem validação contínua para evitar que commits inadvertidos quebrem regras de negócio já validadas, introduzam vulnerabilidades de segurança ou despadronizem a base de código.

## Decisão
Implementar uma esteira de Integração Contínua (CI) e Quality Gates automáticos via **GitHub Actions** (`.github/workflows/ci.yml` e `security.yml`):
1. **Quality Gate de Formatação e Sintaxe:** Execução do linter **Ruff** em cada Push e Pull Request.
2. **Quality Gate de Segurança Estática:** Análise estática de vulnerabilidades e antipatterns via **Bandit**.
3. **Quality Gate de Testes Automatizados:** Execução integral e obrigatória de todos os 64 testes automatizados (testes unitários, funcionais, de integração HTTP e de segurança) em matriz Python (3.11 e 3.12).
4. **Relatório de Cobertura de Código:** Monitoramento de cobertura de testes com verificação de não-regressão.
5. **Auditoria Periódica de Dependências:** Varredura semanal de vulnerabilidades conhecidas em bibliotecas externas.

## Consequências
- Garantia de que nenhuma alteração defeituosa entrará na branch estável `main`.
- Evidências automáticas de integridade para apresentação ao corpo docente.
- Transparência e previsibilidade no processo de entrega de software.
