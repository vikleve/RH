# ADR-003: Unificação Canônica do Código e Higienização do Repositório Git

## Status
Aprovado

## Data
2026-10-28

## Contexto
O histórico do repositório continha múltiplos diretórios concorrentes (`RH-main/`, `RH-main Camylla/`), arquivos compactados versionados (`RH-main.zip`), arquivos binários de banco SQLite local (`colaboradores.db`) e arquivos compilados de bytecode Python (`__pycache__/*.pyc`). 

A raiz do projeto possuía uma versão defasada contendo apenas o Módulo 1 (36 testes), enquanto as implementações completas do Módulo 2 (Folha de Pagamento) com 63 testes residiam isoladas dentro da subpasta `RH-main/`. Essa dispersão violava os padrões fundamentais de governança de software, causava ambiguidade de versão e risco de regressão.

## Decisão
1. **Auditoria e Comparação de Versões:** Foi realizada análise de integridade diferencial (`git diff`) confirmando que o conteúdo de `RH-main/` continha o superset mais recente e completo (incluindo o Módulo de Folha, migrações e testes adicionais).
2. **Promoção Canônica para a Raiz:** Todos os arquivos ativos de `RH-main/` foram promovidos e consolidados diretamente na raiz do projeto (`api/`, `backend/`, `frontend/`, `migrations/`, `tests/`, etc.).
3. **Expurgo de Duplicatas e Arquivos Proibidos:** Remoção de `RH-main.zip`, do diretório temporário `RH-main Camylla/`, da pasta redundante `RH-main/`, de todos os arquivos `.pyc` compilados e de bancos locais `.db` do controle de versão do Git.
4. **Blindagem do `.gitignore`:** Atualização rigorosa do arquivo `.gitignore` para bloquear permanentemente qualquer novo versionamento de caches, bancos de dados locais, arquivos compactados e credenciais.

## Consequências
- Fim da duplicidade e ambiguidade: a raiz é a única fonte da verdade (Single Source of Truth).
- Repositório limpo, profissional e em conformidade estrita com as exigências acadêmicas de Governança de TI.
- Execução de 64 testes automatizados diretamente na raiz com 100% de sucesso.
