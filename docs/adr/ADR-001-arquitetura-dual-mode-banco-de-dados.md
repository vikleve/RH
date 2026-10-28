# ADR-001: Arquitetura de Persistência Dual-Mode (SQLite & PostgreSQL)

## Status
Aprovado

## Data
2026-10-28

## Contexto
O projeto Portal DP & RH atende simultaneamente a dois cenários:
1. **Desenvolvimento e Testes Locais Ágeis:** Os desenvolvedores e estudantes precisam clonar o repositório e executar testes e o backend localmente sem obrigatoriedade de infraestrutura complexa ou servidores externos de banco de dados rodando na máquina.
2. **Ambiente Compartilhado / Nuvem / Vercel:** Ambientes serverless e implantações na nuvem exigem concorrência durável e persistência externa (já que o sistema de arquivos serverless é efêmero/read-only).

## Decisão
Adotar uma arquitetura de banco de dados relacional **Dual-Mode**:
- **Modo Padrão / Local:** SQLite com verificação estrita de integridade referencial (`PRAGMA foreign_keys = ON`) e transações ACID.
- **Modo Nuvem / Produção:** PostgreSQL hospedado (Supabase/Neon) ativado automaticamente quando a variável de ambiente `DATABASE_URL` estiver preenchida.
- **Migrações e Governança:** Todas as tabelas são versionadas através de scripts SQL declarativos em `/migrations` (`001_schema_inicial.sql` e `002_modulo_folha_pagamento.sql`), acompanhados por um script de migração segura de dados (`migrate_to_postgres.py`).

## Consequências
- **Positivas:**
  - Zero atrito para novos desenvolvedores e para a execução dos 63 testes automatizados headless.
  - Compatibilidade com deploys na nuvem sem perder integridade referencial nem segurança de concorrência.
  - Rastreabilidade de evolução de schema através de migrações SQL formais.
- **Mitigações:**
  - Os scripts de banco devem garantir equivalência de tipos de dados (ex: timestamps ISO 8601 e valores numéricos monetários representados com precisão de duas casas decimais).
