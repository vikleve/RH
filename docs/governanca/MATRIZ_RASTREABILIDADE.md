# Matriz de Rastreabilidade de Requisitos (RTM)

**Projeto:** Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos  
**Módulos Cobertos:** Módulo 1 (Colaboradores), Módulo 2 (Folha de Pagamento) e Camada de Segurança/Autenticação  
**Total de Testes Automatizados:** 63 testes com 100% de aprovação (0 falhas, 0 erros)  

---

## 1. Módulo de Autenticação e Segurança (RF-40 a RF-43 / RNF-01 a RNF-03)

| ID Requisito | Critério de Aceitação | Descrição Funcional | Componente Backend | Componente Frontend | Teste Automatizado | Status |
|---|---|---|---|---|---|:---:|
| **RF-40** | **CA-LOGIN-01** | Bloqueio de acesso inicial sem credenciais | `backend/server.py` | `frontend/app.js` | `test_ca_login_01_acesso_inicial_protegido` | **APROVADO** |
| **RF-40** | **CA-LOGIN-02** | Retorno HTTP 401 para rotas protegidas sem sessão | `backend/server.py` | `frontend/app.js` | `test_ca_login_02_bloqueio_acesso_direto` | **APROVADO** |
| **RF-40** | **CA-LOGIN-03** | Rejeição segura de credenciais inválidas (sem enumeração) | `backend/auth.py` | `frontend/app.js` | `test_ca_login_03_credenciais_invalidas` | **APROVADO** |
| **RF-40** | **CA-LOGIN-04** | Autenticação válida gerando token e sessão | `backend/auth.py` | `frontend/app.js` | `test_ca_login_04_autenticacao_valida` | **APROVADO** |
| **RF-43** | **CA-LOGIN-05** | Encerramento de sessão (Logout e revogação no banco) | `backend/auth.py` | `frontend/app.js` | `test_ca_login_05_encerramento_de_sessao` | **APROVADO** |
| **RNF-02** | **CA-LOGIN-06** | Proteção de dados sensíveis e contratos | `backend/server.py` | `frontend/app.js` | `test_ca_login_06_protecao_de_dados` | **APROVADO** |
| **RF-43** | **CA-LOGIN-07** | Persistência e expiração controlada de sessão | `backend/auth.py` | `frontend/app.js` | `test_ca_login_07_persistencia_e_expiracao_sessao` | **APROVADO** |
| **RNF-04** | **CA-LOGIN-08** | Não-regressão das operações sob autenticação | `backend/server.py` | `frontend/app.js` | `test_ca_login_08_regressao_modulo_existente` | **APROVADO** |
| **RNF-05** | **CA-LOGIN-09** | Layout corporativo e responsividade no login | `backend/server.py` | `frontend/styles.css` | `test_ca_login_09_estrutura_layout_e_responsividade` | **APROVADO** |
| **RNF-03** | **CA-LOGIN-10** | Compatibilidade de deploy Serverless / Vercel | `api/index.py` | `vercel.json` | `test_ca_login_10_compatibilidade_deploy_vercel` | **APROVADO** |
| **RNF-01** | **CA-LOGIN-PBKDF2** | Criptografia PBKDF2-HMAC-SHA256 com salt único | `backend/auth.py` | N/A | `test_criptografia_pbkdf2_com_salt` | **APROVADO** |

---

## 2. Módulo 1: Cadastro de Colaboradores e Dependentes (RF-01 a RF-09)

| ID Requisito | Critério de Aceitação | Descrição Funcional | Componente Backend | Componente Frontend | Teste Automatizado | Status |
|---|---|---|---|---|---|:---:|
| **RF-01** | **CA-01** | Cadastro completo de colaborador com dados válidos | `backend/service.py` | `frontend/app.js` | `test_ca01_novo_cadastro_sucesso` | **APROVADO** |
| **RF-02** | **CA-02-A** | Validação de campos obrigatórios no servidor | `backend/validators.py` | `frontend/app.js` | `test_ca02_validacao_campos_obrigatorios` | **APROVADO** |
| **RF-02** | **CA-02-B** | Validação matemática de CPF (dígitos verificadores) | `backend/validators.py` | `frontend/app.js` | `test_ca02_validacao_cpf_invalido` | **APROVADO** |
| **RF-02** | **CA-02-C** | Validação lógica de datas (nascimento e admissão) | `backend/validators.py` | `frontend/app.js` | `test_ca02_validacao_datas` | **APROVADO** |
| **RF-02** | **CA-02-D** | Validação sintática de formato de e-mail | `backend/validators.py` | `frontend/app.js` | `test_ca02_validacao_email_invalido` | **APROVADO** |
| **RF-02** | **CA-02-E** | Validação de valor salarial positivo e numérico | `backend/validators.py` | `frontend/app.js` | `test_ca02_validacao_salario_invalido` | **APROVADO** |
| **RF-03** | **CA-03-A** | Bloqueio de duplicidade de CPF no banco | `backend/database.py` | `frontend/app.js` | `test_ca03_bloqueio_duplicidade_cpf` | **APROVADO** |
| **RF-03** | **CA-03-B** | Bloqueio de duplicidade de Matrícula funcional | `backend/database.py` | `frontend/app.js` | `test_ca03_bloqueio_duplicidade_matricula` | **APROVADO** |
| **RF-04** | **CA-04** | Consulta e pesquisa por nome, CPF e matrícula | `backend/service.py` | `frontend/app.js` | `test_ca04_pesquisa_por_nome_cpf_matricula` | **APROVADO** |
| **RF-05** | **CA-05** | Edição cadastral preservando identificador primário | `backend/service.py` | `frontend/app.js` | `test_ca05_edicao_preservando_identificador` | **APROVADO** |
| **RF-06** | **CA-06** | Trilha de auditoria histórica de alterações | `backend/service.py` | `frontend/app.js` | `test_ca06_auditoria_historico_alteracoes` | **APROVADO** |
| **RF-07** | **CA-07-A** | Inativação lógica sem perda física de dados | `backend/service.py` | `frontend/app.js` | `test_ca07_inativacao_logica` | **APROVADO** |
| **RF-07** | **CA-07-B** | Reativação lógica com registro em auditoria | `backend/service.py` | `frontend/app.js` | `test_ca07_reativacao_logica` | **APROVADO** |
| **RF-08** | **CA-08** | Persistência durável e integridade referencial | `backend/database.py` | N/A | `test_ca08_persistencia_apos_reconexao` | **APROVADO** |
| **RF-09** | **CA-09** | Filtragem por setor e contagem de dependentes | `backend/service.py` | `frontend/app.js` | `test_ca09_estrutura_e_filtros` | **APROVADO** |
| **RF-03** | **CA-10** | Integridade de edição contra conflitos de unicidade | `backend/service.py` | `frontend/app.js` | `test_ca10_integridade_e_nao_regressao` | **APROVADO** |

---

## 3. Módulo 2: Folha de Pagamento & Encargos Trabalhistas (RF-10 a RF-25)

| ID Requisito | Critério de Aceitação | Descrição Funcional | Componente Backend | Componente Frontend | Teste Automatizado | Status |
|---|---|---|---|---|---|:---:|
| **RF-10** | **CA-FOLHA-01** | Cálculo de INSS com faixas progressivas (CLT 2026) | `backend/folha_calculos.py` | `frontend/app.js` | `test_inss_progressivo_multiplas_faixas` | **APROVADO** |
| **RF-10** | **CA-FOLHA-02** | Aplicação estrita do teto máximo de contribuição INSS | `backend/folha_calculos.py` | `frontend/app.js` | `test_inss_teto_maximo` | **APROVADO** |
| **RF-11** | **CA-FOLHA-03** | Cálculo de IRRF progressivo com deduções legais | `backend/folha_calculos.py` | `frontend/app.js` | `test_irrf_progressivo_com_deducoes` | **APROVADO** |
| **RF-11** | **CA-FOLHA-04** | Dedução legal de IRRF por dependente homologado | `backend/folha_calculos.py` | `frontend/app.js` | `test_irrf_deducao_por_dependentes` | **APROVADO** |
| **RF-11** | **CA-FOLHA-05** | Isenção tributária de IRRF na primeira faixa salarial | `backend/folha_calculos.py` | `frontend/app.js` | `test_irrf_isencao_primeira_faixa` | **APROVADO** |
| **RF-12** | **CA-FOLHA-06** | Cálculo de horas extras a 50% de acréscimo | `backend/folha_calculos.py` | `frontend/app.js` | `test_horas_extras_50_porcento` | **APROVADO** |
| **RF-12** | **CA-FOLHA-07** | Cálculo de horas extras a 100% (domingos e feriados) | `backend/folha_calculos.py` | `frontend/app.js` | `test_horas_extras_100_porcento` | **APROVADO** |
| **RF-13** | **CA-FOLHA-08** | Adicional noturno padrão (20%) | `backend/folha_calculos.py` | `frontend/app.js` | `test_adicional_noturno_padrao_20_porcento` | **APROVADO** |
| **RF-13** | **CA-FOLHA-09** | Redução ficta da hora noturna (52m30s / fator 1,142857) | `backend/folha_calculos.py` | `frontend/app.js` | `test_adicional_noturno_com_reducao_ficta` | **APROVADO** |
| **RF-14** | **CA-FOLHA-10** | DSR (Descanso Semanal Remunerado) sobre variáveis | `backend/folha_calculos.py` | `frontend/app.js` | `test_dsr_sobre_variaveis` | **APROVADO** |
| **RF-15** | **CA-FOLHA-11** | Desconto proporcional de faltas integrais injustificadas | `backend/folha_calculos.py` | `frontend/app.js` | `test_desconto_faltas` | **APROVADO** |
| **RF-15** | **CA-FOLHA-12** | Desconto proporcional de horas de atraso | `backend/folha_calculos.py` | `frontend/app.js` | `test_desconto_atrasos` | **APROVADO** |
| **RF-16** | **CA-FOLHA-13** | FGTS informativo (8% sem desconto do colaborador) | `backend/folha_calculos.py` | `frontend/app.js` | `test_valor_fgts_informativo` | **APROVADO** |
| **RF-17** | **CA-FOLHA-14** | Bloqueio de duplicidade de rubrica idêntica na folha | `backend/folha_calculos.py` | `frontend/app.js` | `test_bloqueio_duplicidade_de_rubrica` | **APROVADO** |
| **RF-18** | **CA-FOLHA-15** | Fechamento auditável de folha e bloqueio de alteração | `backend/folha_service.py` | `frontend/app.js` | `test_fechamento_e_reabertura_folha` | **APROVADO** |
| **RF-19** | **CA-FOLHA-16** | Bloqueio de folha duplicada no mesmo mês/ano | `backend/folha_service.py` | `frontend/app.js` | `test_bloqueio_folha_duplicada_mesma_competencia` | **APROVADO** |
| **RF-20** | **CA-FOLHA-17** | Fluxo REST completo da API de folha (CRUD e Estados) | `backend/server.py` | `frontend/app.js` | `test_fluxo_completo_api_folha` | **APROVADO** |
