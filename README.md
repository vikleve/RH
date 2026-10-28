# Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos

[![CI Pipeline](https://github.com/vikleve/RH/actions/workflows/ci.yml/badge.svg)](https://github.com/vikleve/RH/actions/workflows/ci.yml)
[![Security Audit](https://github.com/vikleve/RH/actions/workflows/security.yml/badge.svg)](https://github.com/vikleve/RH/actions/workflows/security.yml)
[![Governança de TI](https://img.shields.io/badge/Governan%C3%A7a%20de%20TI-Total%20(8%20Pilares)-blue.svg)](docs/governanca/MANUAL_DE_GOVERNANCA_TI.md)
[![Conformidade LGPD](https://img.shields.io/badge/LGPD-Conforme%20(Lei%2013.709)-green.svg)](docs/governanca/GOVERNANCA_DADOS_LGPD.md)
[![Testes Automatizados](https://img.shields.io/badge/Testes-63%20de%2063%20Aprovados-success.svg)](tests/executar_todos_testes.py)
[![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)

Projeto interdisciplinar acadêmico desenvolvido em conjunto pelos cursos de **Recursos Humanos (RH)** e **Gestão da Tecnologia da Informação (GTI)**.
Contempla o **Módulo 1: Cadastro de Colaboradores**, o **Módulo 2: Folha de Pagamento Completa** e a **Camada de Segurança e Autenticação (RF-40, RF-41, RF-43, RNF-01 a RNF-03)**, estabelecendo o controle de acesso restrito, proteção de endpoints, sessões criptográficas duráveis, cálculos trabalhistas parametrizados e auditáveis, e demonstrativos oficiais de contracheque.

---

## 🏛️ Governança Total do Projeto

Este repositório opera sob o modelo de **Governança Total de Software e TI**, atendendo às exigências acadêmicas e corporativas de engenharia de software, segurança da informação e legislação trabalhista/previdenciária:

| Documento de Governança | Descrição e Finalidade |
|---|---|
| 📘 **[Manual Integrado de Governança de TI](docs/governanca/MANUAL_DE_GOVERNANCA_TI.md)** | Visão mestre dos 8 Pilares de Governança (Git, Qualidade, CI/CD, Processos, ADRs, LGPD, RBAC, RTM). |
| 🛡️ **[Política de Dados & Conformidade LGPD](docs/governanca/GOVERNANCA_DADOS_LGPD.md)** | Mapeamento de dados sensíveis, bases legais (Art. 7º Lei 13.709/2018), auditoria imutável e inativação lógica. |
| 📊 **[Matriz de Rastreabilidade de Requisitos (RTM)](docs/governanca/MATRIZ_RASTREABILIDADE.md)** | Rastreamento ponta a ponta: RFs/RNFs ↔ Critérios de Aceitação ↔ Código ↔ 63 Testes Automatizados. |
| 🏗️ **[Architecture Decision Records (ADRs)](docs/adr/)** | Histórico e justificativas formais das decisões de arquitetura e tecnologia (`ADR-001` a `ADR-005`). |
| 🤝 **[Diretrizes de Contribuição (CONTRIBUTING)](CONTRIBUTING.md)** | Padrão de branching, Conventional Commits, fluxo de Pull Requests e Definition of Done (DoD). |
| 🔒 **[Política de Segurança (SECURITY)](SECURITY.md)** | Diretrizes de proteção criptográfica, gestão de credenciais e reporte responsável de vulnerabilidades. |
| 📜 **[Código de Conduta (CODE OF CONDUCT)](CODE_OF_CONDUCT.md)** | Compromisso ético e convivência acadêmica e profissional da equipe interdisciplinar. |
| 📄 **[Licença de Uso (LICENSE)](LICENSE)** | Licença permissiva MIT. |

---

## 1. Resumo das Funcionalidades Implementadas

### 1.1. Módulo de Autenticação e Segurança (RF-40, RF-41, RF-43)
- **Tela de Login Corporativa e Responsiva (CA-LOGIN-01, CA-LOGIN-09):**
  - Identificação por e-mail ou nome de usuário.
  - Campo de senha com controle de visualização (mostrar/ocultar senha com ícone interativo).
  - Indicador visual animado (spinner) durante o processamento da autenticação.
  - Validação de campos obrigatórios no cliente com mensagens de feedback visual.
  - Alerta seguro de credenciais inválidas que impede enumeração de contas (mensagem neutra e uniforme).
  - Orientações institucionais de segurança e encaminhamento para a administração em caso de esquecimento de credenciais (sem fluxo vulnerável de recuperação não homologado).
  - Identidade visual refinada e corporativa aderente à tipografia Inter e à paleta do Portal DP & RH.
- **Autenticação Real com Criptografia Forte (CA-LOGIN-03, CA-LOGIN-04, RNF-01):**
  - Senhas protegidas via algoritmo de derivação criptográfica **PBKDF2-HMAC-SHA256** com 100.000 iterações.
  - Salt criptográfico aleatório único de 16 bytes por usuário gerado via `secrets.token_hex`.
  - Comparação de hashes em tempo constante (`hmac.compare_digest`) para prevenir ataques de temporização (*timing attacks*).
  - Proibição de armazenamento de senhas em texto puro.
- **Proteção Integral de Rotas e Endpoints (CA-LOGIN-02, CA-LOGIN-06, RNF-02):**
  - Bloqueio completo de acesso anônimo: requisições sem sessão válida a `/api/colaboradores`, `/api/folha` ou rotas protegidas retornam imediatamente **HTTP 401 Unauthorized**.
  - Dados sensíveis (pessoais, contratuais, salariais e de dependentes) não são enviados a visitantes não autenticados.
- **Gerenciamento Seguro de Sessões (CA-LOGIN-05, CA-LOGIN-07, RF-43):**
  - Sessões vinculadas a tokens criptográficos aleatórios de 32 bytes (64 caracteres hexadecimais).
  - Suporte a cookies de sessão com atributos de segurança: `HttpOnly`, `SameSite=Lax` e `Secure` em conexões HTTPS.
  - Suporte concomitante ao cabeçalho `Authorization: Bearer <token>`.
  - Persistência e expiração controlada das sessões na tabela `sessoes` do SQLite/PostgreSQL.
  - Encerramento de sessão funcional via botão **"Sair"**: invalidação imediata do token no banco de dados (`revogado = 1`), impedindo o reaproveitamento de sessões descartadas.
- **Controle de Acesso por Perfil e Auditoria (RF-41):**
  - Perfis de usuário (`administrador`, `analista_rh`, `operador_dp`).
  - Registro de quem criou, alterou, recalculou, fechou ou reabriu cada folha de pagamento na trilha de auditoria.

### 1.2. Módulo 1: Cadastro de Colaboradores (RF-01 a RF-09)
- **Cadastro Completo:** Dados pessoais, contato, profissionais e dependentes dinâmicos.
- **Validações Rigorosas:** CPF oficial com algoritmo de dígitos verificadores, e-mail por regex, datas lógicas e salário positivo.
- **Bloqueio de Duplicidade:** Unicidade de CPF e Matrícula.
- **Consulta e Pesquisa Rápida:** Filtros por situação (Ativo/Inativo) e Setor com pesquisa instantânea.
- **Edição Preservando Identificador:** Atualizações validadas com histórico de alterações.
- **Auditoria Histórica:** Registro cronológico contendo data/hora, campo alterado, valor antigo, novo valor e operador responsável.
- **Inativação e Reativação Lógica:** Preservação integral do histórico e dados no banco.
- **Persistência Durável:** SQLite relacional com integridade referencial (`PRAGMA foreign_keys = ON`) e PostgreSQL (Supabase).

### 1.3. Módulo 2: Folha de Pagamento Completa
- **Seleção de Competência e Funcionário:**
  - Interface com seletor de mês/ano (competência, ex: `2026-10`), período de pagamento (início e fim) e data de pagamento.
  - Busca e preenchimento automático dos dados contratuais e salariais do colaborador no banco (salário contratual, cargo, setor, admissão, dependentes para dedução de IRRF).
  - **Bloqueio de Duplicidade:** O sistema impede a criação de folhas duplicadas para o mesmo colaborador na mesma competência.
- **Lançamento Dinâmico de Eventos e Rubricas:**
  - Horas extras com percentuais configuráveis (ex: 50% e 100%, ou percentuais customizados de acordos/CCT).
  - Adicional noturno urbano (20% padrão) com opção de hora ficta reduzida (52m30s / fator ~1.142857).
  - Desconto de faltas integrais em dias (com cálculo proporcional ao salário-base e dias do mês).
  - Desconto de atrasos ou saídas antecipadas em horas normais.
  - DSR sobre variáveis (horas extras e adicional noturno) parametrizado por dias úteis e repousos semanais.
  - Outros proventos e descontos avulsos configuráveis com descrição, referência e valor total.
- **Camada de Cálculos Desacoplada e Testável:**
  - Implementada em `backend/folha_calculos.py` com precisão decimal estrita (`round(..., 2)`).
  - Aplicação estrita da tabela progressiva de INSS por faixas salariais e do teto de contribuição previdenciária.
  - Cálculo de IRRF progressivo com dedução legal da parcela de INSS e dedução por dependentes legais cadastrados.
  - Apuração informativa de FGTS patronal (8%).
- **Gestão de Ciclo de Vida da Folha e Imutabilidade:**
  - Estados da folha: `Aberta`, `Calculada`, `Fechada` e `Cancelada`.
  - Fechamento formal auditável: bloqueia edição inadvertida e fixa valores contábeis.
  - Histórico completo na tabela `folha_historico`.
- **Demonstrativo Oficial de Pagamento (Holerite):**
  - Impressão e visualização de contracheque padronizado, contendo dados da empresa, colaborador, discriminação de proventos/descontos, bases de INSS/FGTS/IRRF e valor líquido.

---

## 2. Estrutura Canônica de Arquivos

```text
RH/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # Pipeline CI/CD: Linting, Bandit e 63 Testes Automatizados
│   │   └── security.yml               # Varredura periódica de vulnerabilidades em dependências
│   ├── ISSUE_TEMPLATE/                # Modelos de Issues (Bug, Feature, Governança)
│   └── pull_request_template.md       # Checklist obrigatório de aprovação de Pull Request
├── api/
│   ├── auth/                          # Endpoints serverless de autenticação (login, logout, me)
│   ├── colaboradores.py               # Handlers de colaboradores
│   └── index.py                       # Gateway Serverless para Vercel
├── backend/
│   ├── auth.py                        # Serviço de autenticação, hashing PBKDF2 e sessões
│   ├── database.py                    # Gerenciador Dual-Mode SQLite / PostgreSQL
│   ├── folha_calculos.py              # Motor matemático de cálculos trabalhistas (CLT 2026)
│   ├── folha_service.py               # Regras de negócio, ciclo de vida e auditoria da folha
│   ├── server.py                      # Servidor HTTP REST e roteamento de endpoints protegidos
│   ├── service.py                     # Regras de negócio e auditoria de colaboradores
│   └── validators.py                  # Validadores de CPF, e-mail, datas e valores
├── docs/
│   ├── adr/                           # Architecture Decision Records (ADR-001 a ADR-005)
│   └── governanca/                    # Manuais, Matriz de Rastreabilidade e LGPD
├── frontend/
│   ├── app.js                         # Interface interativa, AuthManager, Colaboradores e Folha
│   ├── index.html                     # Telas de Login, Gestão Cadastral e Folha de Pagamento
│   └── styles.css                     # Design system corporativo acessível e responsivo
├── migrations/
│   ├── 001_schema_inicial.sql         # Schema inicial relacional com integridade
│   └── 002_modulo_folha_pagamento.sql # Schema e tabelas da Folha com RLS
├── tests/
│   ├── executar_todos_testes.py       # Suíte central consolidada (63 testes)
│   ├── test_api.py                    # Testes de integração da API REST autenticada
│   ├── test_autenticacao.py           # Testes dos critérios de segurança (CA-LOGIN)
│   ├── test_colaboradores.py          # Testes unitários do Cadastro de Colaboradores
│   ├── test_folha_api.py              # Testes dos endpoints REST da Folha
│   ├── test_folha_calculos.py         # Testes de precisão dos cálculos da Folha (19 testes)
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

## 3. Credenciais Iniciais de Demonstração

Por motivos de segurança e conformidade, a conta inicial de demonstração é provisionada automaticamente no banco de dados na primeira inicialização, utilizando hash com salt criptográfico:

### Conta de Administrador:
- **E-mail / Usuário:** `admin.dp@empresa.com.br` ou `admin.dp`
- **Senha Inicial:** `Admin@RH2026!`
- **Perfil:** `administrador`

### Conta de Convidado / Visitante:
- **E-mail / Usuário:** `visitante@empresa.com.br` ou `visitante`
- **Senha Inicial:** `Visitante@RH2026!`
- **Perfil:** `analista_rh`

> [!NOTE]
> Para alterar as senhas iniciais no ambiente de produção, configure as variáveis de ambiente `ADMIN_INITIAL_PASSWORD` e `GUEST_INITIAL_PASSWORD`.

---

## 4. Como Executar os Testes Automatizados (63 Testes Headless)

Todos os testes são executados em modo headless, sem necessidade de navegador aberto:

```powershell
# Executar a suíte completa consolidada (63 testes automatizados)
python tests/executar_todos_testes.py
```

Ou utilizando `uv`:
```powershell
uv run python tests/executar_todos_testes.py
```

Também é possível executar módulos de teste específicos:
```powershell
# 1. Testes de cálculos matemáticos da Folha (19 testes)
python -m unittest tests/test_folha_calculos.py

# 2. Testes de ciclo de vida e serviço da Folha (5 testes)
python -m unittest tests/test_folha_service.py

# 3. Testes de endpoints REST da Folha (3 testes)
python -m unittest tests/test_folha_api.py

# 4. Testes de regras de negócio de Colaboradores (16 testes)
python -m unittest tests/test_colaboradores.py

# 5. Testes de segurança e autenticação (18 testes)
python -m unittest tests/test_autenticacao.py

# 6. Testes de integração HTTP da API (2 testes)
python -m unittest tests/test_api.py
```

### Resumo dos Resultados dos Testes:
- **63 testes executados com 100% de sucesso.**
- **0 falhas, 0 erros.**
- **Tempo médio de execução: ~11 segundos.**

---

## 5. Banco de Dados e Migrações SQL

O sistema foi concebido com arquitetura de persistência relacional **Dual-Mode** ([ADR-001](docs/adr/ADR-001-arquitetura-dual-mode-banco-de-dados.md)):
- **Ambiente Local / Testes:** SQLite durável com suporte a transações e chaves estrangeiras (`PRAGMA foreign_keys = ON`).
- **Ambiente de Produção / Nuvem:** PostgreSQL hospedado no Supabase com suporte a concorrência, integridade referencial estrita e políticas **Row Level Security (RLS)**.

### Migrações SQL Disponíveis (`/migrations`):
1. `migrations/001_schema_inicial.sql`: Cria as tabelas `colaboradores`, `dependentes`, `historico_alteracoes`, `usuarios` e `sessoes`.
2. `migrations/002_modulo_folha_pagamento.sql`:
   - Cria a tabela `folha_parametros` (parâmetros de cálculo e vigências com parâmetros padrão CLT 2026).
   - Cria a tabela `folhas_pagamento` com chave de unicidade `(colaborador_id, competencia)`.
   - Cria a tabela `folha_itens` para registro discriminado de proventos, descontos, informativos e memórias de cálculo.
   - Cria a tabela `folha_historico` para auditoria completa de criação, alteração, cálculo, homologação, fechamento e reabertura.
   - Habilita e configura políticas **RLS** (`ENABLE ROW LEVEL SECURITY`).

---

## 6. Como Executar a Aplicação Localmente

Inicie o servidor HTTP com banco de dados SQLite:

```powershell
python backend/server.py
```
Ou:
```powershell
uv run python backend/server.py
```

O sistema estará acessível em `http://localhost:8000`. Ao acessar o endereço, a **Tela de Login** será exibida imediatamente, protegendo as informações e as funcionalidades internas do sistema.

---

## 7. Configuração e Deploy na Vercel

O projeto está configurado para deploy imediato na Vercel através dos arquivos `vercel.json` e `api/index.py`:

- **Roteamento de API:** Requisições para `/api/*` são roteadas para a Serverless Function Python em `api/index.py`.
- **Arquivos Estáticos:** Arquivos do frontend (`index.html`, `styles.css`, `app.js`) são servidos a partir do diretório `frontend/`.
- **Banco de Dados no Serverless:** Em ambiente Vercel, o caminho padrão do SQLite utiliza `/tmp/colaboradores.db` ou a variável de ambiente `DB_PATH`.
