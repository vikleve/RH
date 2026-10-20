# Portal DP & RH — Módulo 1: Cadastro de Colaboradores

Projeto interdisciplinar acadêmico desenvolvido em conjunto pelos cursos de **Recursos Humanos (RH)** e **Gestão da Tecnologia da Informação (GTI)**.
Foco exclusivo no **Módulo 1: Cadastro de Colaboradores**, estabelecendo a fundação cadastral, a integridade de dados e a auditoria histórica para as futuras etapas de Departamento Pessoal e Folha de Pagamento.

---

## 1. Resumo das Funcionalidades Implementadas

- **Cadastro Completo de Colaboradores (RF-01, CA-01):**
  - **Dados Pessoais:** Nome completo, CPF, RG (opcional), Data de nascimento.
  - **Dados de Contato:** E-mail corporativo/pessoal, Telefone/WhatsApp, Endereço completo estruturado (Logradouro, Número, Bairro, Cidade, UF, CEP).
  - **Dados Profissionais:** Matrícula única, Data de admissão, Cargo/função, Setor/departamento, Salário-base e Situação do vínculo.
  - **Dependentes:** Adição e remoção dinâmica de dependentes com nome, parentesco e CPF opcional com validação.
- **Validações Rigorosas de Negócio (RF-02, CA-02):**
  - Validação oficial de CPF com algoritmo de dígitos verificadores e rejeição de números repetidos.
  - Validação de formato de e-mail por regex.
  - Validação lógica de datas (data de nascimento no passado com idade mínima de 14 anos; data de admissão coerente).
  - Validação de valores monetários (salário-base numérico e estritamente positivo).
  - Apresentação de mensagens de erro claras e destacadas abaixo de cada campo.
- **Bloqueio de Duplicidade (RF-03, CA-03):**
  - Verificação de unicidade para CPF e Matrícula antes de persistir, tanto no cadastro quanto na edição.
- **Consulta e Pesquisa Rápida (RF-04, CA-04):**
  - Pesquisa instantânea por Nome, CPF (formatado ou apenas dígitos) ou Matrícula.
  - Filtros por situação (Todos, Ativos, Inativos) e por Setor.
- **Edição com Preservação de Identificador (RF-05, CA-05):**
  - Carregamento dos dados atuais no formulário, validação das alterações e atualização no banco sem criar duplicatas.
- **Trilha de Auditoria e Histórico de Alterações (RF-06, CA-06):**
  - Registro cronológico campo a campo contendo: data/hora exata, campo alterado, valor anterior, novo valor e responsável pela alteração.
- **Inativação Lógica e Reativação (RF-07, CA-07):**
  - Inativação lógica com preservação integral dos dados pessoais, dependentes e histórico.
  - Modal de confirmação com campo opcional de motivo de desligamento.
  - Diferenciação visual clara entre colaboradores ativos e inativos na listagem.
  - Possibilidade de reativação com registro no histórico.
- **Persistência Durável (RF-08, CA-08):**
  - Banco de dados relacional SQLite (`colaboradores.db`) com integridade referencial (`PRAGMA foreign_keys = ON`), constraints de unicidade e índices de busca.
  - Modo autônomo offline no frontend via `localStorage` quando executado diretamente pelo navegador.
- **Interface Administrativa Moderna e Responsiva (RF-09, CA-09):**
  - Interface desenvolvida em HTML5 semântico e Vanilla CSS com tipografia Inter, cards de métricas, modais acessíveis e suporte a dispositivos móveis.

---

## 2. Estrutura de Arquivos

```
cadastro-colaboradores/
├── backend/
│   ├── database.py             # Configuração e inicialização do SQLite com tabelas e índices
│   ├── validators.py           # Algoritmos de validação (CPF oficial, e-mail, datas, moeda)
│   ├── service.py              # Camada de regras de negócio, auditoria e inativação lógica
│   └── server.py               # Servidor HTTP REST (API JSON e arquivos estáticos sem dependências)
├── frontend/
│   ├── index.html              # Interface do usuário semântica e acessível
│   ├── styles.css              # Design system em Vanilla CSS, responsivo e corporativo
│   └── app.js                  # Lógica do cliente, máscaras, debounce, modais e integração API
├── tests/
│   ├── test_colaboradores.py   # Testes unitários de regras de negócio e persistência (CA-01 a CA-10)
│   ├── test_api.py             # Testes de integração da API HTTP REST
│   └── executar_todos_testes.py # Executor central de testes automatizados via código
├── ESPECIFICACAO_RH.md         # Documento de alinhamento e dúvidas para validação do RH
└── README.md                   # Documentação do módulo
```

---

## 3. Como Executar os Testes em Código (Sem Abrir Navegador)

Os testes foram construídos utilizando o módulo nativo `unittest` do Python e podem ser executados diretamente no terminal sem abrir nenhuma janela de navegador:

```powershell
# Executar a suíte completa de testes (17 testes automatizados)
uv run python tests/executar_todos_testes.py
```

Ou individualmente:

```powershell
# Testes de regras de negócio e critérios de aceitação (CA-01 a CA-10)
uv run python -m unittest tests/test_colaboradores.py

# Testes de integração da API HTTP
uv run python -m unittest tests/test_api.py
```

### Resultados dos Testes Automatizados:
- **17 testes executados com 100% de sucesso.**
- **0 falhas, 0 erros.**

---

## 4. Como Executar a Aplicação Web

Para iniciar o servidor local com API e banco de dados SQLite:

```powershell
uv run python backend/server.py
```

O servidor iniciará em `http://localhost:8000`. Basta abrir este endereço no navegador para utilizar a aplicação de forma completa e integrada.
Caso o arquivo `frontend/index.html` seja aberto diretamente em modo estático (`file://`), a aplicação ativa automaticamente o fallback para `localStorage`, permitindo demonstrações imediatas.

---

## 5. Matriz de Critérios de Aceitação

| Critério | Descrição | Status | Como foi validado |
|---|---|:---:|---|
| **CA-01** | Novo cadastro com dados válidos | APROVADO | Teste unitário `test_ca01_novo_cadastro_sucesso` e API `test_fluxo_completo_api` |
| **CA-02** | Validação de campos e formatos | APROVADO | Testes `test_ca02_*` (CPF oficial, e-mail, datas e salários) |
| **CA-03** | Bloqueio de duplicidade (CPF/Matrícula) | APROVADO | Testes `test_ca03_bloqueio_duplicidade_*` |
| **CA-04** | Consulta e pesquisa | APROVADO | Teste `test_ca04_pesquisa_por_nome_cpf_matricula` |
| **CA-05** | Edição preservando identificador | APROVADO | Teste `test_ca05_edicao_preservando_identificador` |
| **CA-06** | Histórico e auditoria de alterações | APROVADO | Teste `test_ca06_auditoria_historico_alteracoes` |
| **CA-07** | Inativação lógica sem perda | APROVADO | Testes `test_ca07_inativacao_logica` e `test_ca07_reativacao_logica` |
| **CA-08** | Persistência durável | APROVADO | Teste `test_ca08_persistencia_apos_reconexao` no SQLite |
| **CA-09** | Estrutura e responsividade | APROVADO | Teste `test_ca09_estrutura_e_filtros` e CSS responsivo |
| **CA-10** | Integridade e não-regressão | APROVADO | Teste `test_ca10_integridade_e_nao_regressao` |
