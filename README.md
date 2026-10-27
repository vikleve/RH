# Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos

Projeto interdisciplinar acadêmico desenvolvido em conjunto pelos cursos de **Recursos Humanos (RH)** e **Gestão da Tecnologia da Informação (GTI)**.
Contempla o **Módulo 1: Cadastro de Colaboradores** e a **Camada de Segurança e Autenticação (RF-40, RF-41, RF-43, RNF-01, RNF-02, RNF-03)**, estabelecendo o controle de acesso restrito, proteção de endpoints, sessões criptográficas duráveis e auditoria histórica completa.

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
  - Bloqueio completo de acesso anônimo: requisições sem sessão válida a `/api/colaboradores` ou rotas protegidas retornam imediatamente **HTTP 401 Unauthorized**.
  - Dados sensíveis (pessoais, contratuais, salariais e de dependentes) não são enviados a visitantes não autenticados.
- **Gerenciamento Seguro de Sessões (CA-LOGIN-05, CA-LOGIN-07, RF-43):**
  - Sessões vinculadas a tokens criptográficos aleatórios de 32 bytes (64 caracteres hexadecimais).
  - Suporte a cookies de sessão com atributos de segurança: `HttpOnly`, `SameSite=Lax` e `Secure` em conexões HTTPS.
  - Suporte concomitante ao cabeçalho `Authorization: Bearer <token>`.
  - Persistência e expiração controlada das sessões na tabela `sessoes` do SQLite.
  - Encerramento de sessão funcional via botão **"Sair"**: invalidação imediata do token no banco de dados (`revogado = 1`), impedindo o reaproveitamento de sessões descartadas.
- **Preparação para Controle de Acesso por Perfil (RF-41):**
  - Estrutura de perfis de usuário (`administrador`, `analista_rh`, `operador_dp`).
  - Registro do operador responsável na trilha de auditoria campo a campo.

### 1.2. Módulo 1: Cadastro de Colaboradores (RF-01 a RF-09)
- **Cadastro Completo:** Dados pessoais, contato, profissionais e dependentes dinâmicos.
- **Validações Rigorosas:** CPF oficial com algoritmo de dígitos verificadores, e-mail por regex, datas lógicas e salário positivo.
- **Bloqueio de Duplicidade:** Unicidade de CPF e Matrícula.
- **Consulta e Pesquisa Rápida:** Filtros por situação (Ativo/Inativo) e Setor com pesquisa instantânea.
- **Edição Preservando Identificador:** Atualizações validadas com histórico de alterações.
- **Auditoria Histórica:** Registro cronológico contendo data/hora, campo alterado, valor antigo, novo valor e operador responsável.
- **Inativação e Reativação Lógica:** Preservação integral do histórico e dados no banco.
- **Persistência Durável:** SQLite relacional com integridade referencial (`PRAGMA foreign_keys = ON`).

---

## 2. Estrutura de Arquivos

```
cadastro-colaboradores/
├── api/
│   └── index.py                # Handler serverless para execução na Vercel
├── backend/
│   ├── auth.py                 # Serviço de autenticação, hashing PBKDF2 e sessões criptográficas
│   ├── database.py             # Configuração e tabelas do SQLite (colaboradores, dependentes, usuarios, sessoes)
│   ├── server.py               # Servidor HTTP REST (endpoints protegidos, cookies HttpOnly e static files)
│   ├── service.py              # Regras de negócio de colaboradores e auditoria
│   └── validators.py           # Algoritmos de validação (CPF oficial, e-mail, datas, moeda)
├── frontend/
│   ├── app.js                  # Lógica do cliente, AuthManager, integração protegida e máscaras
│   ├── index.html              # Tela de Login acessível + Painel do Sistema protegido
│   └── styles.css              # Design system corporativo, responsivo, spinner e cards de login
├── tests/
│   ├── executar_todos_testes.py # Executor central de testes automatizados headless
│   ├── test_api.py             # Testes de integração de API HTTP autenticada
│   ├── test_autenticacao.py    # Testes específicos dos critérios de segurança (CA-LOGIN-01 a 10)
│   └── test_colaboradores.py   # Testes unitários das regras de negócio do Módulo 1 (CA-01 a 10)
├── ESPECIFICACAO_RH.md         # Documento de alinhamento com a equipe de RH
├── vercel.json                 # Configuração de roteamento e deploy serverless na Vercel
└── README.md                   # Documentação completa do sistema
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

## 4. Como Executar os Testes em Código (Sem Abrir Navegador)

Todos os testes são executados em modo headless, sem necessidade de navegador aberto:

```powershell
# Executar a suíte completa consolidada (29 testes automatizados)
uv run python tests/executar_todos_testes.py
```

Ou executar módulos específicos:

```powershell
# Testes específicos de autenticação e segurança (CA-LOGIN-01 a CA-LOGIN-10)
uv run python -m unittest tests/test_autenticacao.py

# Testes de integração da API REST autenticada
uv run python -m unittest tests/test_api.py

# Testes das regras de negócio do Módulo 1 (CA-01 a CA-10)
uv run python -m unittest tests/test_colaboradores.py
```

### Resumo dos Resultados dos Testes:
- **29 testes executados com 100% de sucesso.**
- **0 falhas, 0 erros.**

---

## 5. Como Executar a Aplicação Localmente

Inicie o servidor HTTP com banco de dados SQLite:

```powershell
uv run python backend/server.py
```

O sistema estará acessível em `http://localhost:8000`. Ao acessar o endereço, a **Tela de Login** será exibida imediatamente, protegendo as informações e as funcionalidades internas do sistema.

---

## 6. Configuração e Deploy na Vercel

O projeto está configurado para deploy imediato na Vercel através dos arquivos `vercel.json` e `api/index.py`:

- **Roteamento de API:** Requisições para `/api/*` são roteadas para a Serverless Function Python em `api/index.py`.
- **Arquivos Estáticos:** Arquivos do frontend (`index.html`, `styles.css`, `app.js`) são servidos a partir do diretório `frontend/`.
- **Banco de Dados no Serverless:** Em ambiente Vercel, o caminho padrão do SQLite utiliza `/tmp/colaboradores.db` ou a variável de ambiente `DB_PATH`.

### Variáveis de Ambiente Recomendadas:
- `ADMIN_INITIAL_PASSWORD`: Senha de provisionamento do administrador inicial.
- `DB_PATH`: Caminho do banco SQLite durável ou integração com banco remoto (ex: Turso / Supabase / Neon).

---

## 7. Matriz de Critérios de Aceitação

### Critérios de Segurança e Autenticação (CA-LOGIN-01 a CA-LOGIN-10)

| Critério | Descrição | Status | Validação Automatizada |
|---|---|:---:|---|
| **CA-LOGIN-01** | Acesso inicial protegido sem vazar dados | APROVADO | `test_ca_login_01_acesso_inicial_protegido` |
| **CA-LOGIN-02** | Bloqueio de acesso direto a rotas protegidas (HTTP 401) | APROVADO | `test_ca_login_02_bloqueio_acesso_direto` |
| **CA-LOGIN-03** | Rejeição segura de credenciais inválidas | APROVADO | `test_ca_login_03_credenciais_invalidas` |
| **CA-LOGIN-04** | Autenticação válida com sessão e token | APROVADO | `test_ca_login_04_autenticacao_valida` |
| **CA-LOGIN-05** | Encerramento de sessão (Logout e invalidação de token) | APROVADO | `test_ca_login_05_encerramento_de_sessao` |
| **CA-LOGIN-06** | Proteção de dados sensíveis e contratuais | APROVADO | `test_ca_login_06_protecao_de_dados` |
| **CA-LOGIN-07** | Persistência de sessão e bloqueio de tokens expirados | APROVADO | `test_ca_login_07_persistencia_e_expiracao_sessao` |
| **CA-LOGIN-08** | Não-regressão das operações do Módulo 1 | APROVADO | `test_ca_login_08_regressao_modulo_existente` |
| **CA-LOGIN-09** | Responsividade e elementos visuais da tela de login | APROVADO | `test_ca_login_09_estrutura_layout_e_responsividade` |
| **CA-LOGIN-10** | Compatibilidade de deploy e configuração Vercel | APROVADO | `test_ca_login_10_compatibilidade_deploy_vercel` |

### Critérios Funcionais do Cadastro de Colaboradores (CA-01 a CA-10)

| Critério | Descrição | Status | Validação Automatizada |
|---|---|:---:|---|
| **CA-01** | Novo cadastro com dados válidos | APROVADO | `test_ca01_novo_cadastro_sucesso` |
| **CA-02** | Validação de campos e formatos | APROVADO | Testes `test_ca02_*` |
| **CA-03** | Bloqueio de duplicidade (CPF/Matrícula) | APROVADO | Testes `test_ca03_bloqueio_duplicidade_*` |
| **CA-04** | Consulta e pesquisa por nome/CPF/matrícula | APROVADO | `test_ca04_pesquisa_por_nome_cpf_matricula` |
| **CA-05** | Edição preservando identificador | APROVADO | `test_ca05_edicao_preservando_identificador` |
| **CA-06** | Histórico e auditoria de alterações | APROVADO | `test_ca06_auditoria_historico_alteracoes` |
| **CA-07** | Inativação lógica sem perda | APROVADO | Testes `test_ca07_inativacao_logica` e `reativacao` |
| **CA-08** | Persistência durável no SQLite | APROVADO | `test_ca08_persistencia_apos_reconexao` |
| **CA-09** | Estrutura e filtros | APROVADO | `test_ca09_estrutura_e_filtros` |
| **CA-10** | Integridade e não-regressão | APROVADO | `test_ca10_integridade_e_nao_regressao` |
