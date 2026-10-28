# Esteira de CI/CD e Quality Gates Automatizados

Este diretório contém os scripts das pipelines de Integração Contínua (CI) e Auditoria de Segurança implementadas no projeto:

## 1. Arquivos de Pipeline
- **`ci.yml`**: Pipeline principal de CI que é executada no GitHub Actions a cada `push` e `pull_request` nas branches `main` e `develop`.
  - Configura ambiente Python (matriz 3.11 e 3.12).
  - Executa análise de conformidade de código e formatação com `Ruff` (0 erros).
  - Executa análise estática de vulnerabilidades e segurança com `Bandit` (0 vulnerabilidades).
  - Executa a suíte completa de **64 testes automatizados** em modo headless com 100% de sucesso.
  - Gera relatório de cobertura de código (`Coverage >= 78%`).
- **`security.yml`**: Pipeline semanal e por demanda para auditoria contínua de dependências vulneráveis via `pip-audit` (sem `|| true`).

## 2. Ativação no GitHub Actions
Para habilitar a execução automática no painel **Actions** do repositório no GitHub, estes arquivos devem residir na pasta `.github/workflows/`.
Caso seu token do GitHub CLI precise da permissão `workflow`, execute no terminal:
```powershell
gh auth refresh -s workflow
git add .github/workflows/
git commit -m "ci: adicionar workflows do GitHub Actions"
git push origin gov/spec-gov-002-validacao-governanca
```
Ou adicione os fluxos diretamente pelo painel do GitHub na aba **Actions** > **New workflow**.
