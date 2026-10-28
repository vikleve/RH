# Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos

[![CI Pipeline](https://github.com/vikleve/RH/actions/workflows/ci.yml/badge.svg)](https://github.com/vikleve/RH/actions/workflows/ci.yml)
[![Security Audit](https://github.com/vikleve/RH/actions/workflows/security.yml/badge.svg)](https://github.com/vikleve/RH/actions/workflows/security.yml)
[![Governança de TI](https://img.shields.io/badge/Governan%C3%A7a%20de%20TI-Alinhada%20(SPEC--GOV--002)-blue.svg)](docs/governanca/MANUAL_DE_GOVERNANCA_TI.md)
[![Conformidade LGPD](https://img.shields.io/badge/LGPD-Pol%C3%ADtica%20Documentada%20(Lei%2013.709)-green.svg)](docs/governanca/GOVERNANCA_DADOS_LGPD.md)
[![Testes Automatizados](https://img.shields.io/badge/Testes-64%20de%2064%20Aprovados%20(100%25)-success.svg)](tests/executar_todos_testes.py)
[![Cobertura de Código](https://img.shields.io/badge/Cobertura-78%25%20(Pass)-brightgreen.svg)](pyproject.toml)
[![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)

Projeto interdisciplinar acadêmico desenvolvido em conjunto pelos cursos de **Recursos Humanos (RH)** e **Gestão da Tecnologia da Informação (GTI)**.
Contempla o **Módulo 1: Cadastro de Colaboradores**, o **Módulo 2: Folha de Pagamento** e a **Camada de Segurança e Autenticação (RF-40, RF-41, RF-43, RNF-01 a RNF-03)**, estabelecendo controle de acesso restrito a operadores de DP/RH, proteção de rotas via HTTP 401, sessões criptográficas duráveis, cálculos trabalhistas parametrizados e auditáveis, e demonstrativos oficiais de contracheque.

---

## 🏛️ Governança do Projeto (SPEC-GOV-002)

Este repositório opera sob o modelo de **Governança de Software e TI**, atendendo às exigências acadêmicas e corporativas de engenharia de software, segurança da informação e legislação trabalhista/previdenciária:

| Documento de Governança | Descrição e Finalidade |
|---|---|
| 📘 **[Manual Integrado de Governança de TI](docs/governanca/MANUAL_DE_GOVERNANCA_TI.md)** | Visão mestre dos 8 Pilares de Governança (Git, Qualidade, CI/CD, Processos, ADRs, LGPD, RBAC, RTM). |
| 🛡️ **[Política de Dados & Diretrizes LGPD](docs/governanca/GOVERNANCA_DADOS_LGPD.md)** | Mapeamento de dados, bases legais (Art. 7º Lei 13.709/2018), auditoria rastreável e fluxo administrativo sem autoatendimento (RF-44). |
| 📊 **[Matriz de Rastreabilidade de Requisitos (RTM)](docs/governanca/MATRIZ_RASTREABILIDADE.md)** | Rastreamento integral: RF-01 a RF-56, RF-57 a RF-62, RNF-01 a RNF-10, RN-01 a RN-08, CA-01 a CA-09, T-01 a T-12 e DP-01 a DP-15 ↔ 64 Testes Automatizados. |
| 🏗️ **[Architecture Decision Records (ADRs)](docs/adr/)** | Histórico e justificativas formais das decisões de arquitetura e tecnologia (`ADR-001` a `ADR-005`). |
| 📋 **[Especificação de Governança (SPEC-GOV-002)](docs/governanca/SPEC-GOV-002-alinhamento-e-validacao-governanca.md)** | Especificação de alinhamento com a fonte oficial de requisitos (`Requisitos_Sistema_Folha.docx`) e validação de controles. |
| 🤝 **[Diretrizes de Contribuição (CONTRIBUTING)](CONTRIBUTING.md)** | Padrão de branching, Conventional Commits, fluxo de Pull Requests e Definition of Done (DoD). |
| 🔒 **[Política de Segurança (SECURITY)](SECURITY.md)** | Diretrizes de proteção criptográfica, gestão de credenciais e reporte responsável de vulnerabilidades. |
| 📜 **[Código de Conduta (CODE OF CONDUCT)](CODE_OF_CONDUCT.md)** | Compromisso ético e convivência acadêmica e profissional da equipe interdisciplinar. |
| 📄 **[Licença de Uso (LICENSE)](LICENSE)** | Licença permissiva MIT. |

---

## 1. Resumo das Funcionalidades e Controles

### 1.1. Módulo de Autenticação e Segurança (RF-40, RF-41, RF-43)
- **Tela de Login Corporativa e Responsiva (CA-LOGIN-01, CA-LOGIN-09):**
  - Identificação por e-mail ou nome de usuário institucional.
  - Campo de senha com controle de visibilidade interativo.
  - Indicador visual animado (spinner) durante processamento.
  - Rejeição segura de credenciais inválidas sem enumeração de contas (mensagem neutra e uniforme).
  - Orientações institucionais de segurança e contato com a administração em caso de esquecimento de acesso.
- **Autenticação com Criptografia Forte (CA-LOGIN-03, CA-LOGIN-04, RNF-01):**
  - Senhas protegidas via algoritmo de derivação criptográfica **PBKDF2-HMAC-SHA256** com 100.000 iterações.
  - Salt criptográfico aleatório único de 16 bytes gerado via `secrets.token_hex`.
  - Comparação de hashes em tempo constante (`hmac.compare_digest`) para mitigar ataques de temporização (*timing attacks*).
  - Bloqueio mandatório de inicialização sem senha administrativa forte em ambientes reais/compartilhados.
- **Proteção Integral de Rotas e Endpoints (CA-LOGIN-02, CA-LOGIN-06, RNF-02):**
  - Bloqueio completo de acesso anônimo: requisições sem sessão válida a `/api/colaboradores`, `/api/folha` ou rotas protegidas retornam **HTTP 401 Unauthorized**.
  - Dados sensíveis e contratuais não são trafegados para usuários não autenticados.
- **Gerenciamento de Sessões (CA-LOGIN-05, CA-LOGIN-07, RF-43):**
  - Sessões vinculadas a tokens criptográficos pseudoaleatórios de 32 bytes (64 caracteres hexadecimais).
  - Suporte a cookies de sessão com atributos `HttpOnly` e `SameSite=Lax`.
  - Encerramento de sessão funcional via botão **"Sair"**: invalidação imediata do token no banco de dados (`revogado = 1`).
- **Controle de Acesso Operacional (RF-41, RF-44, DP-03):**
  - Perfis de usuário estruturados (`administrador`, `analista_rh`).
  - O portal é de uso restrito dos operadores de DP/RH. Conforme **RF-44** e **DP-03**, não há autoatendimento direto para colaboradores na versão 1.0.

### 1.2. Módulo 1: Cadastro de Colaboradores (RF-01 a RF-09)
- **Cadastro Completo:** Dados pessoais, identificadores, contato, profissionais e dependentes dinâmicos.
- **Validações de Integridade:** Validação oficial de CPF com algoritmo de dígitos verificadores, e-mail por regex, datas lógicas e salário positivo.
- **Bloqueio de Duplicidade:** Unicidade de CPF e Matrícula funcional.
- **Consulta e Pesquisa Rápida:** Filtros por situação (Ativo/Inativo) e Setor com pesquisa textual.
- **Edição Preservando Identificador:** Atualizações validadas com histórico de alterações.
- **Auditoria Histórica:** Registro cronológico contendo data/hora, campo alterado, valor antigo, novo valor e operador responsável.
- **Inativação e Reativação Lógica:** Preservação integral do histórico no banco de dados sem exclusão física.

### 1.3. Módulo 2: Folha de Pagamento
- **Seleção de Competência e Funcionário:**
  - Interface com seletor de mês/ano (competência, ex: `2026-10`), período de apuração e data de pagamento.
  - Busca automática dos dados contratuais e dependentes para dedução de IRRF.
  - Bloqueio de duplicidade para o mesmo colaborador na mesma competência.
- **Lançamento de Eventos e Variáveis:**
  - Horas extras com percentuais configuráveis (50%, 100% ou percentuais acordados em CCT).
  - Adicional noturno urbano (20%) com cálculo técnico de redução ficta da hora noturna (fator ~1,142857).
  - Desconto de faltas integrais e horas de atraso.
  - DSR sobre variáveis parametrizado por dias úteis e repousos semanais.
- **Cálculos e Memória de Cálculo (ADR-004):**
  - Precisão decimal estrita (`round(..., 2)`).
  - Aplicação preliminar de faixas progressivas de INSS e teto previdenciário vigente.
  - Cálculo de IRRF progressivo com dedução de INSS e dependentes legais.
  - Apuração informativa de FGTS (8%).
  - *Nota:* Fórmulas e tabelas representam implementação técnica preliminar sujeita a homologação formal (DP-08, DP-14, DP-15).
- **Ciclo de Vida e Fechamento Auditável:**
  - Estados da folha: `Aberta`, `Calculada`, `Fechada` e `Cancelada`.
  - Fechamento formal auditável: bloqueia edição inadvertida; reabertura exige justificativa registrada em `folha_historico`.
- **Demonstrativo de Pagamento (Holerite):**
  - Visualização e impressão de contracheque padronizado com memória discriminada.

---

## 2. Estrutura Canônica de Arquivos

```text
RH/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # Pipeline CI/CD: Ruff, Bandit, Coverage e 64 Testes
│   │   └── security.yml               # Varredura periódica de vulnerabilidades em dependências
│   ├── ISSUE_TEMPLATE/                # Modelos de Issues (Bug, Feature, Governança)
│   └── pull_request_template.md       # Checklist obrigatório de aprovação de Pull Request
├── api/
│   ├── auth/                          # Endpoints serverless de autenticação (login, logout, me)
│   ├── colaboradores.py               # Handlers serverless de colaboradores
│   └── index.py                       # Gateway Serverless para Vercel
├── backend/
│   ├── auth.py                        # Serviço de autenticação, hashing PBKDF2 e sessões
│   ├── database.py                    # Gerenciador Dual-Mode SQLite / PostgreSQL
│   ├── folha_calculos.py              # Motor matemático de cálculos trabalhistas
│   ├── folha_service.py               # Regras de negócio, ciclo de vida e auditoria da folha
│   ├── server.py                      # Servidor HTTP REST e roteamento de endpoints protegidos
│   ├── service.py                     # Regras de negócio e auditoria de colaboradores
│   └── validators.py                  # Validadores de CPF, e-mail, datas e valores
├── docs/
│   ├── adr/                           # Architecture Decision Records (ADR-001 a ADR-005)
│   ├── ci-cd/                         # Arquivos de referência espelhados das esteiras CI/CD
│   └── governanca/                    # Manuais, Matriz de Rastreabilidade e Diretrizes LGPD
├── frontend/
│   ├── app.js                         # Interface interativa, AuthManager, Colaboradores e Folha
│   ├── index.html                     # Telas de Login, Gestão Cadastral e Folha de Pagamento
│   └── styles.css                     # Design system corporativo acessível e responsivo
├── migrations/
│   ├── 001_schema_inicial.sql         # Schema inicial relacional com integridade
│   └── 002_modulo_folha_pagamento.sql # Schema e tabelas da Folha com RLS
├── tests/
│   ├── executar_todos_testes.py       # Suíte central consolidada (64 testes)
│   ├── test_api.py                    # Testes de integração da API REST autenticada (5 testes)
│   ├── test_autenticacao.py           # Testes dos critérios de segurança (19 testes)
│   ├── test_colaboradores.py          # Testes unitários do Cadastro de Colaboradores (16 testes)
│   ├── test_folha_api.py              # Testes dos endpoints REST da Folha (3 testes)
│   ├── test_folha_calculos.py         # Testes de cálculos da Folha (16 testes)
│   └── test_folha_service.py          # Testes de integridade e ciclo de vida da Folha (5 testes)
├── .editorconfig                      # Padronização de indentação, encodings e line endings
├── .env.example                       # Modelo de variáveis de ambiente seguro
├── .gitignore                         # Blindagem contra inclusão de binários e segredos
├── .pre-commit-config.yaml            # Hooks de qualidade locais para desenvolvedores
├── CONTRIBUTING.md                    # Manual de contribuição e fluxo de Git
├── CODE_OF_CONDUCT.md                 # Código de conduta profissional e acadêmico
├── LICENSE                            # Licença MIT
├── pyproject.toml                     # Metadados do projeto, Ruff, Bandit e Coverage
├── README.md                          # Documentação central do projeto
├── requirements.txt                   # Dependências Python mínimas
├── SECURITY.md                        # Política de segurança e reporte de vulnerabilidades
└── vercel.json                        # Configuração de deploy serverless na Vercel
```

---

## 3. Gestão Segura de Credenciais e Inicialização

Em conformidade com as diretrizes de governança e segurança da informação (**GOV-002-02**), senhas padrão utilizáveis foram removidas do código e da documentação pública.

### Configuração de Ambientes Reais ou Compartilhados:
Antes de iniciar a aplicação em ambiente compartilhado ou produtivo, copie o arquivo `.env.example` para `.env` e defina uma senha forte para a conta de administração:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```ini
ADMIN_INITIAL_PASSWORD=DefinaSuaSenhaForteAqui@2026!
GUEST_INITIAL_PASSWORD=OpcionalSenhaVisitante2026!
```

> [!WARNING]
> **Bloqueio de Inicialização:** Se a variável `ADMIN_INITIAL_PASSWORD` não for configurada em ambiente real, o sistema interrompe a inicialização levantando um erro operacional de segurança para impedir a operação com credenciais padrão vazias ou fracas.

### Ambiente de Testes Automatizados:
A suíte de testes automatizados (`tests/executar_todos_testes.py`) roda em ambiente efêmero isolado utilizando credenciais sintéticas autogeradas, preservando a segurança sem depender de segredos em disco.

---

## 4. Como Executar os Quality Gates e a Suíte de Testes (64 Testes Headless)

Todos os testes são executados em modo headless, sem necessidade de navegador aberto:

```powershell
# Executar a suíte completa consolidada (64 testes automatizados)
python tests/executar_todos_testes.py
```

Ou utilizando `uv`:
```powershell
uv run python tests/executar_todos_testes.py
```

### Execução dos Quality Gates Individuais:
```powershell
# 1. Análise estática de código e linting (Ruff)
uv run ruff check .

# 2. Varredura estática de segurança (Bandit)
uv run bandit -r backend api -c pyproject.toml

# 3. Medição de cobertura de testes (Coverage >= 78%)
uv run coverage run --source=backend tests/executar_todos_testes.py
uv run coverage report -m

# 4. Auditoria de vulnerabilidades em dependências (pip-audit)
uv run pip-audit -r requirements.txt
```

### Resumo dos Resultados Reais Observados:
- **64 testes executados com 100% de sucesso (0 falhas, 0 erros).**
- **Cobertura de linhas no backend: 78% (limiar atendido).**
- **Ruff: 0 erros de formatação ou estilo.**
- **Bandit: 0 vulnerabilidades de segurança.**
- **pip-audit: 0 vulnerabilidades conhecidas.**

---

## 5. Banco de Dados e Persistência Dual-Mode

O sistema utiliza arquitetura de persistência relacional **Dual-Mode** ([ADR-001](docs/adr/ADR-001-arquitetura-dual-mode-banco-de-dados.md)):
- **Ambiente Local / Testes:** SQLite durável com suporte a transações e chaves estrangeiras (`PRAGMA foreign_keys = ON`).
- **Ambiente de Produção / Nuvem:** PostgreSQL hospedado no Supabase com suporte a concorrência, integridade referencial estrita e políticas **Row Level Security (RLS)**.

---

## 6. Como Executar a Aplicação Localmente

Inicie o servidor HTTP com banco de dados SQLite local:

```powershell
uv run python backend/server.py
```

O sistema estará acessível em `http://localhost:8000`. Ao acessar o endereço, a **Tela de Login** será exibida imediatamente, protegendo as informações e as funcionalidades internas do sistema.

---

## 7. Configuração Serverless na Vercel

O projeto possui configuração para deploy serverless na Vercel através dos arquivos `vercel.json` e `api/index.py`:
- **Roteamento de API:** Requisições para `/api/*` são roteadas para a Serverless Function Python em `api/index.py`.
- **Arquivos Estáticos:** Arquivos do frontend (`index.html`, `styles.css`, `app.js`) são servidos a partir do diretório `frontend/`.
- **Isolamento de Banco:** Em ambientes serverless efêmeros, utiliza-se banco PostgreSQL externo via `DATABASE_URL` configurado nas variáveis de ambiente da plataforma.
