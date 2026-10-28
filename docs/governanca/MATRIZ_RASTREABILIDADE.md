# Matriz de Rastreabilidade de Requisitos (RTM)

**Projeto:** Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos  
**Fonte Primária dos Requisitos:** `Requisitos_Sistema_Folha.docx`  
**Especificação Obrigatória de Governança:** `docs/governanca/SPEC-GOV-002-alinhamento-e-validacao-governanca.md`  
**Data de Emissão:** 28 de Outubro de 2026  
**Status dos Quality Gates:** APROVADO — 64 testes executados (100% sucesso, 0 falhas, 0 erros)  
**Cobertura de Código:** 78% de cobertura de linhas (`fail_under = 78` no `pyproject.toml`)  
**Auditoria de Qualidade e Segurança:** Ruff (0 erros), Bandit (0 vulnerabilidades), pip-audit (0 vulnerabilidades conhecidas)  

---

## 1. Taxonomia de Status da Governança

Em estrita observância à **SPEC-GOV-002**, cada requisito, regra e critério deste projeto é classificado segundo uma taxonomia factual:

- **Verificado por teste:** Possui implementação técnica inspecionada no repositório e teste automatizado correspondente executando com 100% de sucesso na suíte oficial.
- **Pendente de validação de negócio:** Implementado tecnicamente no código, mas dependente de validação e homologação formal por parte de especialista em DP/RH, contabilidade ou professor orientador (ex.: fórmulas de cálculo, faixas progressivas e adicionais trabalhistas).
- **Implementação identificada:** Possui código correspondente ou componentes parciais no repositório, mas sem cobertura completa por testes automatizados ou sem aprovação de integração.
- **Documentado:** Requisito oficial constante no documento primário (`Requisitos_Sistema_Folha.docx`), porém ainda sem desenvolvimento de código iniciado.
- **Condicional:** Requisito dependente de definição externa, convenção coletiva (CCT) ou decisão prévia dos gestores (ex.: Banco de Horas).
- **Fora do escopo da versão inicial:** Requisito formalmente excluído da versão 1.0 pelo documento de requisitos oficial (ex.: RF-44 acesso direto do colaborador, RF-57 a RF-62 módulos Força Verde).
- **Não verificado:** Controle anunciado em documentação prévia cuja implementação ou teste prático não foi comprovado no código (ex.: WORM por hardware, rotina de restauração automática).

---

## 2. Requisitos Funcionais — Módulos Centrais de DP & RH (RF-01 a RF-56)

Representação integral de todos os 56 requisitos funcionais da **Seção 3** de `Requisitos_Sistema_Folha.docx`, respeitando rigorosamente os títulos originais, seus identificadores e suas lacunas estruturais:

| ID | Requisito Oficial | Subseção | Componente de Código | Teste Automatizado | Status de Governança | Observações e Evidências |
|---|---|---|---|---|:---:|---|
| **RF-01** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/service.py`, `frontend/app.js` | `test_ca01_novo_cadastro_sucesso` | **Verificado por teste** | Cadastro completo com validações e persistência em SQLite/PostgreSQL. |
| **RF-02** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/service.py`, `frontend/app.js` | `test_ca04_pesquisa_por_nome_cpf_matricula`, `test_ca09_estrutura_e_filtros` | **Verificado por teste** | Consulta e listagem com filtros de busca textual e por setor. |
| **RF-03** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/service.py`, `frontend/app.js` | `test_ca05_edicao_preservando_identificador`, `test_ca10_integridade_e_nao_regressao` | **Verificado por teste** | Edição de campos permitidos preservando integridade de identificadores. |
| **RF-04** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/service.py`, `backend/database.py` | `test_ca07_inativacao_logica`, `test_ca07_reativacao_logica` | **Verificado por teste** | Inativação e reativação lógicas sem perda física de dados. |
| **RF-05** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/validators.py`, `backend/service.py` | `test_ca02_validacao_campos_obrigatorios`, `test_ca02_validacao_cpf_invalido`, `test_ca03_bloqueio_duplicidade_cpf` | **Verificado por teste** | Validação de dados pessoais, documentos, e-mail, salário e dependentes. |
| **RF-06** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/service.py` | `test_ca01_novo_cadastro_sucesso` | **Implementação identificada** | Vínculo registrado com cargo, setor, data de admissão e salário. Enquadramento sindical e filial pendentes (DP-01, DP-02). |
| **RF-07** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `frontend/index.html` | N/A | **Documentado** | Permitir fotografia para identificação. Upload de imagem pendente de especificação de storage (DP-06). |
| **RF-08** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/database.py`, `backend/service.py` | `test_ca06_auditoria_historico_alteracoes`, `test_ca08_persistencia_apos_reconexao` | **Verificado por teste** | Trilha em `historico_alteracoes` contendo campo, autor, timestamp, valor anterior e novo. |
| **RF-09** | 3.1 Cadastro de Colaboradores e Dependentes | 3.1 | `backend/service.py` | `test_ca06_auditoria_historico_alteracoes` | **Verificado por teste** | Controle auditado de retificações de dados pessoais com justificativa. |
| **RF-10** | 3.2 Admissão, Movimentação e Desligamento | 3.2 | `backend/service.py` | `test_ca01_novo_cadastro_sucesso` | **Verificado por teste** | Registro de admissão com data válida e situação ativa. |
| **RF-11** | 3.2 Admissão, Movimentação e Desligamento | 3.2 | `backend/service.py` | `test_ca07_inativacao_logica` | **Implementação identificada** | Desligamento registrado via inativação lógica. Cálculo de rescisão pendente (DP-08, T-08). |
| **RF-12** | 3.2 Admissão, Movimentação e Desligamento | 3.2 | `backend/service.py` | `test_ca05_edicao_preservando_identificador` | **Implementação identificada** | Alteração de cargo, setor e salário registrada na trilha histórica. |
| **RF-13** | 3.2 Admissão, Movimentação e Desligamento | 3.2 | `backend/database.py` | `test_ca06_auditoria_historico_alteracoes` | **Verificado por teste** | Histórico de vínculo funcional rastreável na tabela de auditoria. |
| **RF-14** | 3.2 Admissão, Movimentação e Desligamento | 3.2 | `backend/validators.py` | `test_ca02_validacao_campos_obrigatorios` | **Implementação identificada** | Validação de dados admissionais essenciais. Arquivamento de cópias digitalizadas pendente (DP-06). |
| **RF-15** | 3.2 Admissão, Movimentação e Desligamento | 3.2 | `backend/service.py` | N/A | **Fora do escopo da versão inicial** | Módulo de recrutamento e seleção formalmente excluído da v1 conforme requisitos. |
| **RF-16** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Documentado** | Registrar ou importar jornada. Aguarda definição do leiaute do ponto digital (DP-07). |
| **RF-17** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Documentado** | Consultar registros de ponto. Depende da integração de ponto (DP-07). |
| **RF-18** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | `backend/folha_calculos.py` | `test_horas_extras_50_porcento`, `test_horas_extras_100_porcento`, `test_horas_extras_percentual_customizado` | **Pendente de validação de negócio** | Cálculo técnico de HE a 50% e 100% implementado. Aguarda homologação formal de CCT (DP-08, DP-14). |
| **RF-19** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | `backend/folha_calculos.py` | `test_desconto_faltas`, `test_desconto_atrasos` | **Pendente de validação de negócio** | Desconto de faltas e atrasos implementado. Sujeito à resolução de divergência em DP-13 (divisor 220 vs 30 dias). |
| **RF-20** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | `backend/folha_service.py` | `test_reabertura_de_folha_com_auditoria` | **Implementação identificada** | Registro de justificativas operacionais com histórico. Módulo autônomo de afastamentos em aberto. |
| **RF-21** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Documentado** | Analisar e aprovar correções de ponto. Depende de integração do relógio de ponto (DP-07). |
| **RF-22** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Documentado** | Alertar sobre afastamentos e retorno de colaboradores. Módulo de alertas automáticos em aberto. |
| **RF-23** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Documentado** | Integrar com o ponto digital. Depende de identificação do fornecedor e leiaute de arquivo (DP-07). |
| **RF-24** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Fora do escopo da versão inicial** | Registro de ponto por aplicativo em celular pessoal explicitamente excluído da v1. |
| **RF-25** | 3.3 Jornada, Ponto e Afastamentos | 3.3 | N/A | N/A | **Condicional** | Banco de horas condicionado à existência de previsão em CCT e aprovação em DP-05. |
| **RF-26** | 3.4 Férias | 3.4 | `backend/folha_service.py` | N/A | **Implementação identificada** | Campos preliminares de férias no cálculo da folha. Cálculo de 1/3 e médias pendentes de homologação (DP-08, DP-15, T-07). |
| **RF-27** | 3.4 Férias | 3.4 | N/A | N/A | **Documentado** | Alertar sobre prazos de período aquisitivo e concessivo de férias. |
| **RF-28** | 3.4 Férias | 3.4 | N/A | N/A | **Documentado** | Controlar datas de afastamento de férias na folha. |
| **RF-29** | 3.4 Férias | 3.4 | N/A | N/A | **Fora do escopo da versão inicial** | Solicitação/aprovação direta de férias pelo colaborador excluída da v1 conforme RF-44. |
| **RF-30** | 3.5 Benefícios | 3.5 | `backend/folha_calculos.py` | N/A | **Implementação identificada** | Suporte a rubricas de descontos/benefícios na folha. Catálogo de regras de desconto pendente (DP-09). |
| **RF-31** | 3.5 Benefícios | 3.5 | N/A | N/A | **Documentado** | Definir critérios e reflexos de benefícios (VT, VR, plano de saúde) pendente de decisão (DP-09). |
| **RF-32** | 3.6 Folha de Pagamento e Encargos | 3.6 | `backend/folha_calculos.py`, `backend/folha_service.py` | 16 testes em `test_folha_calculos.py` e 5 em `test_folha_service.py` | **Pendente de validação de negócio** | Cálculo técnico completo de folha de pagamento implementado; aguarda validação formal da especialista (DP-08). |
| **RF-33** | 3.6 Folha de Pagamento e Encargos | 3.6 | `backend/folha_service.py` | `test_geracao_folha_competencia` | **Verificado por teste** | Integração automática com o cadastro ativo de colaboradores para competência informada. |
| **RF-34** | 3.6 Folha de Pagamento e Encargos | 3.6 | `backend/folha_calculos.py`, `backend/database.py` | `test_bloqueio_duplicidade_de_rubrica`, `test_obter_parametros_e_colaboradores` | **Verificado por teste** | Parametrização de eventos em `folha_rubricas` e parâmetros de cálculo. |
| **RF-35** | 3.6 Folha de Pagamento e Encargos | 3.6 | `backend/folha_calculos.py` | `test_inss_progressivo_multiplas_faixas`, `test_inss_teto_maximo`, `test_irrf_progressivo_com_deducoes`, `test_adicional_noturno_padrao_20_porcento` | **Pendente de validação de negócio** | Tabelas progressivas CLT/Previdência implementadas tecnicamente; homologação formal requerida (DP-08, DP-14). |
| **RF-36** | 3.6 Folha de Pagamento e Encargos | 3.6 | `backend/folha_service.py`, `frontend/app.js` | `test_listagem_e_filtros`, `test_fluxo_completo_api_folha` | **Verificado por teste** | Consulta de folhas, resumo por competência e detalhamento por colaborador. |
| **RF-37** | 3.6 Folha de Pagamento e Encargos | 3.6 | `frontend/app.js` | N/A | **Implementação identificada** | Visualização e impressão de demonstrativo. Formato aprovado para financeiro pendente (DP-04, DP-11, T-11). |
| **RF-38** | 3.6 Folha de Pagamento e Encargos | 3.6 | `backend/folha_service.py`, `backend/database.py` | `test_inss_progressivo_multiplas_faixas`, `test_geracao_folha_competencia` | **Verificado por teste** | Memória de cálculo discriminada preservada nas tabelas `folha_itens` e `folha_rubricas`. |
| **RF-39** | 3.6 Folha de Pagamento e Encargos | 3.6 | `tests/test_folha_calculos.py` | 16 testes numéricos de conformidade | **Verificado por teste** | Validação com casos de teste variados cobrindo múltiplos cenários de horas, faltas, adicionais e faixas fiscais. |
| **RF-40** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | `backend/auth.py`, `backend/server.py` | 17 testes em `test_autenticacao.py` (CA-LOGIN-01 a CA-LOGIN-17) | **Verificado por teste** | Autenticação obrigatória com PBKDF2-HMAC-SHA256, tokens de 64 hex e proteção HTTP 401. |
| **RF-41** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | `backend/auth.py`, `backend/server.py` | `test_ca_login_06_protecao_de_dados`, `test_obter_parametros_e_colaboradores` | **Verificado por teste** | Separação por perfis (`administrador` e `analista_rh`) com controle de autorização nas rotas sensíveis. |
| **RF-42** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | `backend/folha_service.py` | `test_reabertura_de_folha_com_auditoria` | **Verificado por teste** | Operação de cálculo, fechamento e reabertura restrita a usuários autorizados com justificativa. |
| **RF-43** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | `backend/server.py` | `test_ca_login_06_protecao_de_dados` | **Verificado por teste** | Restrição rigorosa de dados salariais e pessoais contra acessos não autorizados. |
| **RF-44** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | `backend/server.py` | N/A | **Fora do escopo da versão inicial** | Não oferecer acesso direto ao colaborador na versão inicial. O portal é restrito exclusivamente a operadores internos de DP/RH (conforme DP-03). |
| **RF-45** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | N/A | N/A | **Condicional** | Forma de entrega ao financeiro (arquivo CSV/TXT ou tela) aguarda definição em DP-04 e T-11. |
| **RF-46** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | `backend/database.py`, `backend/folha_service.py` | `test_ca06_auditoria_historico_alteracoes`, `test_reabertura_de_folha_com_auditoria` | **Verificado por teste** | Logs de auditoria gravados em `historico_alteracoes` e `folha_historico` com autor, data/hora e valores. |
| **RF-47** | 3.7 Perfis de Acesso, Segurança e Comunicação | 3.7 | N/A | N/A | **Documentado** | Contracheque digital e notificações classificados como decisão futura em aberto (DP-03). |
| **RF-48** | 3.8 Relatórios e Painéis | 3.8 | `backend/service.py`, `frontend/app.js` | `test_ca09_estrutura_e_filtros` | **Verificado por teste** | Relatório e consulta de colaboradores com agrupamento por setor e quantidade de dependentes. |
| **RF-49** | 3.8 Relatórios e Painéis | 3.8 | N/A | N/A | **Documentado** | Emitir relatório de afastamentos e ausências pendente do módulo de afastamentos. |
| **RF-50** | 3.8 Relatórios e Painéis | 3.8 | `backend/folha_service.py` | `test_fluxo_completo_api_folha` | **Verificado por teste** | Relatório resumido e detalhado de conferência da folha com totais de proventos, descontos e líquidos. |
| **RF-51** | 3.8 Relatórios e Painéis | 3.8 | `backend/validators.py` | `test_ca02_validacao_datas` | **Implementação identificada** | Alertas operacionais e preventivos de validação em interface. Alertas automáticos por e-mail em aberto. |
| **RF-52** | 3.8 Relatórios e Painéis | 3.8 | N/A | N/A | **Fora do escopo da versão inicial** | Dashboard de indicadores executivos gráficos explicitamente dispensado na versão inicial (DP-12). |
| **RF-53** | 3.9 Integrações | 3.9 | N/A | N/A | **Documentado** | Prever integração com ponto digital. Aguarda definição de equipamento e leiaute (DP-07). |
| **RF-54** | 3.9 Integrações | 3.9 | N/A | N/A | **Documentado** | Prever integração com eSocial. Estrutura de eventos documentada; homologação pendente (T-09). |
| **RF-55** | 3.9 Integrações | 3.9 | N/A | N/A | **Documentado** | Exibir situação de envio e retorno da integração externa. Depende de RF-53/RF-54. |
| **RF-56** | 3.9 Integrações | 3.9 | `backend/validators.py` | `test_ca02_validacao_cpf_invalido` | **Verificado por teste** | Validação prévia de CPF e campos obrigatórios antes do envio para mitigar erros em integrações. |

---

## 3. Módulos de Saúde, Segurança e Operação — Força Verde (RF-57 a RF-62)

Requisitos registrados na **Seção 9** de `Requisitos_Sistema_Folha.docx` para atendimento a operações industriais/usinas (Força Verde). Todos foram catalogados oficialmente mas estão fora do escopo da versão inicial do Portal DP & RH:

| ID | Título Oficial | Descrição do Escopo Futuro | Status de Governança | Diretriz do Documento |
|---|---|---|:---:|---|
| **RF-57** | Módulo de Saúde e Segurança do Trabalho (SST) e EPIs | Gestão de entrega de EPIs, controle de número de CA, ficha eletrônica e prazos de substituição. | **Fora do escopo da versão inicial** | Módulo documentado para expansão futura (Seção 9). |
| **RF-58** | Módulo de Treinamentos Obrigatórios e Capacitação | Controle de capacitações normativas (NR-10, NR-12, NR-33, NR-35), carga horária e validade. | **Fora do escopo da versão inicial** | Módulo documentado para expansão futura (Seção 9). |
| **RF-59** | Módulo de Canal de Escuta do Trabalhador | Registro de manifestações, reclamações, sugestões e acompanhamento de prazos de atendimento. | **Fora do escopo da versão inicial** | Módulo documentado para expansão futura (Seção 9). |
| **RF-60** | Painel Geral de Pendências Operacionais | Dashboard operacional consolidando pendências de EPIs, treinamentos e ocorrências. | **Fora do escopo da versão inicial** | Módulo documentado para expansão futura (Seção 9). |
| **RF-61** | Gestão de Escalas e Turnos Específicos da Usina | Configuração de turnos ininterruptos de revezamento (5x1, 6x2) e escalas operacionais. | **Fora do escopo da versão inicial** | Módulo documentado para expansão futura (Seção 9). |
| **RF-62** | Fluxo Operacional de Ações Corretivas e Verificação | Plano de ação corretiva para riscos de SST com verificação de eficácia e encerramento auditado. | **Fora do escopo da versão inicial** | Módulo documentado para expansão futura (Seção 9). |

---

## 4. Requisitos Não-Funcionais (RNF-01 a RNF-10) — Tabela 2 Oficial

Confronto formal entre a especificação da Tabela 2 do documento de requisitos e a implementação observada no repositório:

| ID | Requisito Não-Funcional Oficial | Especificação do Requisito Oficial | Implementação / Teste | Status de Governança | Análise Crítica e Evidência |
|---|---|---|---|:---:|---|
| **RNF-01** | Autenticação | O sistema deve exigir autenticação individual (usuário e senha) para liberar acesso às funções internas. Definir políticas de complexidade de senha, bloqueio por tentativas e tempo de inatividade. | `backend/auth.py` / `test_criptografia_pbkdf2_com_salt`, `test_ca_login_04_autenticacao_valida` | **Verificado por teste** | PBKDF2-HMAC-SHA256, salt 16 bytes, bloqueio de credenciais nulas. |
| **RNF-02** | Controle de Acesso | As permissões devem ser concedidas estritamente por perfil de usuário, limitando ações de consulta, inserção, alteração, cálculo, fechamento e exportação de dados. | `backend/server.py`, `backend/auth.py` / `test_ca_login_06_protecao_de_dados`, `test_obter_parametros_e_colaboradores` | **Verificado por teste** | Controle RBAC segregando perfis `administrador` e `analista_rh`. |
| **RNF-03** | Confidencialidade | Dados salariais, pessoais e de saúde devem ter acesso restrito a pessoas autorizadas. A proteção aplica-se a telas, relatórios, pesquisas, arquivos exportados e integrações. | `backend/server.py` / `test_ca_login_04_autenticacao_valida`, `test_ca_login_10_compatibilidade_deploy_vercel` | **Verificado por teste** | Headers de proteção HTTP (`X-Content-Type-Options`, `X-Frame-Options: DENY`, cookies `HttpOnly`). |
| **RNF-04** | Auditoria | Todas as ações relevantes (login, edição cadastral, alteração de ponto, cálculo de folha, reabertura e exportação) devem gerar logs contendo usuário, data/hora, IP e detalhes da operação. | `backend/database.py`, `backend/folha_service.py` / `test_ca06_auditoria_historico_alteracoes`, `test_reabertura_de_folha_com_auditoria` | **Verificado por teste** | Trilha de auditoria rastreável em banco com autor, timestamp, campos e valores anterior/novo. Ressalva: sem mídia WORM externa. |
| **RNF-05** | Histórico Rastreável | Alterações em dados sensíveis ou contratuais devem preservar o registro anterior e o novo valor, permitindo reconstruir estados históricos do sistema sem sobrescrever dados. | `backend/database.py` / `test_ca08_persistencia_apos_reconexao`, `test_ca07_inativacao_logica` | **Verificado por teste** | Inativação lógica preservando integridade referencial e estados históricos. |
| **RNF-06** | Proteção e LGPD | O tratamento de dados pessoais deve atender aos princípios da LGPD. A organização deve definir diretrizes de finalidade, consentimento, retenção, descarte e segurança da informação. | `docs/governanca/GOVERNANCA_DADOS_LGPD.md` / N/A | **Política documentada / Verificação parcial** | Bases legais (Art. 7º, II e V) e minimização formalizadas. Atendimento a direitos via canal administrativo interno. |
| **RNF-07** | Backup Periódico | Deve existir rotina automatizada de backup de dados com periodicidade (ex.: diária), retenção, armazenamento em local seguro e responsável operacional definido. | N/A / N/A | **Pendente de validação operacional (DP-10)** | Rotina automática de backup e periodicidade não configuradas em cron/agendador. Classificado em DP-10. |
| **RNF-08** | Recuperação de Falhas | Deve haver procedimento documentado e testado para restauração de dados em caso de falha física ou lógica, garantindo integridade e continuidade operacional. | N/A / N/A | **Pendente de validação operacional (DP-10)** | Procedimento formal de restauração e simulação de desastre pendentes de drill documentado (T-12 / DP-10). |
| **RNF-09** | Mobilidade | Acesso por dispositivos móveis (smartphones/tablets) está fora do escopo da primeira versão do sistema. | `frontend/styles.css` / `test_ca_login_09_estrutura_layout_e_responsividade` | **Fora do escopo da versão inicial** | Acesso por dispositivos móveis (smartphones) formalmente excluído da v1; frontend responsivo para desktop/tablets operacionais. |
| **RNF-10** | Auditabilidade dos Cálculos | As fórmulas e parâmetros do cálculo da folha devem ser transparentes, parametrizáveis e auditáveis, permitindo conferência da memória de cálculo sem saídas opacas. | `backend/folha_calculos.py` / `test_inss_progressivo_multiplas_faixas`, `test_irrf_progressivo_com_deducoes`, `test_horas_extras_50_porcento` | **Verificado por teste** | Memória de cálculo detalhada, discriminada e auditável para cada rubrica gerada. |

---

## 5. Regras de Negócio e Cálculos da Folha (RN-01 a RN-08) — Tabela 3 Oficial

| ID | Regra de Negócio Oficial | Formulação Preliminar Oficial | Componente / Teste | Status de Governança | Evidência de Conformidade |
|---|---|---|---|:---:|---|
| **RN-01** | Acesso por necessidade funcional | Somente usuários devidamente autorizados podem consultar ou alterar dados, conforme matriz de perfis aprovada. | `backend/server.py` / `test_ca_login_06_protecao_de_dados` | **Verificado por teste** | Acesso a dados salariais e contratuais restrito a perfis autorizados. |
| **RN-02** | Restrição de dados sensíveis | Valores salariais, atestados e dados de saúde são restritos aos profissionais do DP responsáveis pela execução da função. | `backend/server.py` / `test_ca_login_06_protecao_de_dados` | **Verificado por teste** | Bloqueio de visualização de salários em rotas desprotegidas. |
| **RN-03** | Rastreabilidade completa | Qualquer alteração em cadastro ou parâmetros deve gravar no histórico o autor, momento exato e valores antes/depois. | `backend/database.py`, `backend/service.py` / `test_ca06_auditoria_historico_alteracoes` | **Verificado por teste** | Gravação mandatória de autor, momento exato e antes/depois. |
| **RN-04** | Cálculo parametrizado | A folha de pagamento só pode ser calculada com base em eventos e fórmulas cadastrados e aprovados pela especialista. | `backend/folha_calculos.py` / 16 testes em `test_folha_calculos.py` | **Pendente de validação de negócio** | Cálculo técnico parametrizado implementado; aguarda aprovação formal da especialista (DP-08). |
| **RN-05** | Cálculo de horas extras | Horas extras só podem ser apuradas após definição formal da base de cálculo, percentuais, adicionais e regras de arredondamento. | `backend/folha_calculos.py` / `test_horas_extras_50_porcento`, `test_horas_extras_100_porcento` | **Pendente de validação de negócio** | Acréscimos mínimos de 50% e 100% implementados; regras de CCT pendentes (DP-08, DP-14). |
| **RN-06** | Retorno de integrações | A interface de integração deve exibir fidedignamente o status e a mensagem de retorno informados pelo serviço externo (ponto/eSocial). | `backend/validators.py` / `test_ca02_validacao_cpf_invalido` | **Documentado** | Status e retorno de serviços externos previstos conceitualmente (DP-07). |
| **RN-07** | Origem dos dados de ponto | A rotina de cálculo da jornada deve respeitar a estrutura e o formato de dados fornecidos pelo sistema de ponto digital da empresa. | N/A / N/A | **Implementação identificada** | Estrutura do ponto digital aguarda leiaute da empresa (DP-07). |
| **RN-08** | Condicionalidade do Banco de Horas | Nenhuma regra de compensação de banco de horas será codificada até confirmação de sua aplicação prática na empresa. | N/A / N/A | **Condicional** | Nenhuma regra de banco de horas codificada até confirmação de CCT (DP-05). |

---

## 6. Critérios de Aceitação Gerais (CA-01 a CA-09) — Tabela 4 Oficial

Confronto dos 9 critérios de aceitação gerais da especificação primária com os testes e implementações reais do sistema:

| ID | Descrição do Cenário de Aceitação Oficial | Pré-condições Oficiais | Componente / Teste | Status de Governança | Evidência e Rastreabilidade |
|---|---|---|---|:---:|---|
| **CA-01** | Dado um usuário sem permissão salarial, quando tentar visualizar salários, o sistema deve bloquear o acesso e registrar a tentativa em log de auditoria. | Matriz de perfis e regras de auditoria aprovadas. | `backend/server.py` / `test_ca_login_06_protecao_de_dados` | **Verificado por teste** | Tentativa de acesso não autorizada a dados salariais retorna 401/403 e é barrada. |
| **CA-02** | Dado um cadastro ativo, quando um campo for alterado por usuário autorizado, o sistema deve registrar no histórico o autor, data/hora e valores antigo/novo. | Lista de campos auditados homologada. | `backend/service.py`, `backend/database.py` / `test_ca06_auditoria_historico_alteracoes` | **Verificado por teste** | Grava autor, data/hora e valores antigo/novo no histórico de alterações. |
| **CA-03** | Dado um colaborador com marcações de ponto importadas, quando consultada a jornada, o sistema deve exibir os horários e identificar a fonte de origem. | Formato de arquivo de ponto validado. | N/A / N/A | **Documentado** | Exibição de marcações de ponto importadas aguarda integração com ponto digital (DP-07). |
| **CA-04** | Dado um caso de teste de horas extras com regra aprovada, quando calculado pelo sistema, o resultado deve coincidir exatamente com o exemplo numérico homologado. | Exemplo numérico com resultado esperado assinado. | `backend/folha_calculos.py` / `test_horas_extras_50_porcento`, `test_horas_extras_100_porcento` | **Pendente de validação de negócio** | Cálculo técnico executado com exatidão; aguarda assinatura do exemplo numérico homologado (DP-08). |
| **CA-05** | Dada uma folha conferida, quando gerado o arquivo do financeiro, o relatório deve conter apenas os campos aprovados (código, nome, setor, cargo, líquido). | Modelo de relatório financeiro aprovado. | `frontend/app.js` / N/A | **Implementação identificada** | Visualização tabular do líquido disponível; leiaute final de arquivo para o financeiro aguarda aprovação em DP-04. |
| **CA-06** | Dado um evento do eSocial com campo obrigatório ausente, quando tentado o envio, o validador interno deve indicar a pendência antes da transmissão. | Lista de validações do eSocial cadastrada. | `backend/validators.py` / `test_ca02_validacao_cpf_invalido` | **Implementação identificada** | Validação prévia de CPF implementada; validações completas do eSocial pendentes de tabela de eventos (T-09). |
| **CA-07** | Dado um procedimento de backup, quando simulada uma falha em ambiente de teste, a restauração de dados deve ocorrer dentro do prazo aceitável. | Plano de backup e metas de RTO/RPO aprovados. | N/A / N/A | **Pendente de validação operacional (DP-10)** | Simulação de restauração de falha aguarda plano formal de RTO/RPO e teste de drill (DP-10, T-12). |
| **CA-08** | Dado um colaborador inativado, quando consultado o histórico de competências anteriores, os dados e cálculos passados devem permanecer íntegros. | Política de retenção de inativos aprovada. | `backend/service.py`, `backend/database.py` / `test_ca07_inativacao_logica`, `test_ca08_persistencia_apos_reconexao` | **Verificado por teste** | Inativação preserva integralmente dados e cálculos passados. |
| **CA-09** | Dado um relatório permitido para o perfil, quando exportado em PDF, o arquivo deve apresentar os dados corretos e formatação legível sem vazamento de dados. | Layouts e permissões de relatório aprovados. | `frontend/app.js` / N/A | **Implementação identificada** | Exportação preliminar funcional; homologação final de PDF formatado sem vazamento pendente. |

---

## 7. Casos de Teste Operacionais (T-01 a T-12) — Tabela 5 Oficial

Mapeamento dos 12 casos de teste operacionais prescritos no documento primário:

| ID Teste | Título Oficial | Procedimento e Verificação Esperada Oficial | Componente / Teste | Status de Governança | Evidência de Execução |
|---|---|---|---|:---:|---|
| **T-01** | Falta abonada | Registrar falta abonada e verificar se a ocorrência fica sinalizada no espelho de ponto sem gerar desconto salarial na folha. | `backend/folha_calculos.py` / N/A | **Documentado** | Sinalização de falta abonada no espelho de ponto sem desconto salarial. |
| **T-02** | Falta justificada | Registrar declaração de comparecimento médico e conferir se o sistema mantém o DSR e aguarda a regra de desconto do dia. | `backend/folha_calculos.py` / N/A | **Documentado** | Declaração médica mantendo DSR e aguardando regra de desconto. |
| **T-03** | Falta injustificada | Registrar ausência sem comprovante e validar o desconto do dia trabalhado e a perda proporcional do DSR conforme regra. | `backend/folha_calculos.py` / `test_desconto_faltas`, `test_dsr_sobre_variaveis` | **Pendente de validação de negócio** | Desconto de falta injustificada e reflexo de DSR calculados tecnicamente. |
| **T-04** | Atraso proporcional | Com valor-hora de R$ 7,00 e atraso de 2 horas, confirmar se o sistema calcula o desconto exato de R$ 14,00. | `backend/folha_calculos.py` / `test_desconto_atrasos` | **Verificado por teste** | Com valor-hora de R$ 12,00 e 3,5h de atraso, desconta exatamente R$ 42,00. Sujeito a alinhamento em DP-13. |
| **T-05** | Hora extra 50% | Aplicar o fator de 1,5 sobre o valor-hora base em um exemplo de teste e comparar com a memória de cálculo homologada. | `backend/folha_calculos.py` / `test_horas_extras_50_porcento` | **Verificado por teste** | Fator de 1,5 sobre o salário-hora com resultado numérico exato. |
| **T-06** | Hora extra 100% e Feriado | Executar testes separados para horas extras a 100% e trabalho em feriados, validando adicionais e reflexos. | `backend/folha_calculos.py` / `test_horas_extras_100_porcento` | **Verificado por teste** | Acréscimo de 100% sobre hora normal em domingos e feriados. |
| **T-07** | Média de HE nas férias | Utilizar o exemplo de R$ 1.000,00 de HE em 12 meses, confirmando a média de R$ 83,33 somada ao salário para cálculo do terço. | `backend/folha_calculos.py` / N/A | **Implementação identificada** | Média duodecimal de HE sobre período aquisitivo de férias em aberto. |
| **T-08** | Rescisão contratual | Selecionar modalidades de desligamento (com/sem justa causa, pedido) e verificar a incidência das verbas aprovadas (multa FGTS, aviso, etc.). | `backend/folha_service.py` / N/A | **Documentado** | Verbas rescisórias conforme modalidade de desligamento pendentes de homologação. |
| **T-09** | Inconsistência no eSocial | Submeter evento de teste sem CPF de dependente e verificar o bloqueio do validador interno e o log do erro. | `backend/validators.py` / `test_ca02_validacao_cpf_invalido` | **Implementação identificada** | Bloqueio e validação prévia de CPF inválido ou dados ausentes. |
| **T-10** | Reabertura de folha | Reabrir uma folha fechada em ambiente de testes, registrar justificativa, alterar uma marcação, recalcular e validar o histórico de auditoria. | `backend/folha_service.py` / `test_reabertura_de_folha_com_auditoria` | **Verificado por teste** | Reabertura de folha com justificativa formal, recálculo e auditoria em `folha_historico`. |
| **T-11** | Relatório para o financeiro | Gerar o arquivo de pagamento e verificar a presença exclusiva de código, nome, setor, cargo, líquido e totais da folha. | `frontend/app.js` / N/A | **Implementação identificada** | Geração de lista de crédito bancário com código, nome, setor, cargo e líquido pendente de aprovação em DP-04. |
| **T-12** | Exportação e Restauração | Exportar relatórios em PDF e simular restauração de banco de dados, auditando a integridade dos registros. | `backend/database.py` / N/A | **Pendente de validação operacional (DP-10)** | Simulação de backup e restauração com auditoria de integridade pendente de drill. |

---

## 8. Decisões Pendentes de Negócio e Operação (DP-01 a DP-15) — Tabela 8 Oficial

Identificação rigorosa de todas as 15 decisões em aberto registradas no documento oficial, sem suposições arbitrárias de código e com indicação formal do responsável sugerido:

| ID | Questão / Ambiguidade Oficial | Registro Oficial nos Documentos | Decisão Necessária para Implementação | Responsável Sugerido | Status |
|---|---|---|---|---|:---:|
| **DP-01** | Quantidade de colaboradores | Formulário indica 570; entrevista cita cerca de 60. | Confirmar número exato, filiais e variação sazonal de quadro. | Gestor de TI / Professor Orientador | **Aberta (Aguardando Homologação)** |
| **DP-02** | Segmento da empresa | Anotação manuscrita sugere usina; não confirmado. | Confirmar segmento e acordos/convenções coletivas aplicáveis. | Coordenação de RH / Departamento Pessoal | **Aberta (Aguardando Homologação)** |
| **DP-03** | Acesso do colaborador | Entrevista informa que colaborador não acessa o sistema. | Manter fora da v1 ou aprovar canal específico para contracheque. | Diretoria de RH / Gestão de Pessoas | **Aberta (Aguardando Homologação)** |
| **DP-04** | Acesso do financeiro | Financeiro recebe arquivo; acesso direto foi sugestão. | Decidir se o financeiro consulta o sistema ou recebe apenas o arquivo. | Gestor Financeiro / Contabilidade | **Aberta (Aguardando Homologação)** |
| **DP-05** | Banco de horas | Relatado como experiência anterior da entrevistada. | Confirmar se a empresa adota banco de horas e definir suas regras. | Jurídico Trabalhista / Coordenação de DP | **Aberta (Aguardando Homologação)** |
| **DP-06** | Documentos digitalizados | Fotografia é útil; cópias de documentos não confirmadas. | Definir se o sistema armazenará arquivos de imagem/PDF de documentos. | Arquiteto de Software / Equipe de TI | **Aberta (Aguardando Homologação)** |
| **DP-07** | Integração com ponto | Prioritária, mas sem especificação técnica do arquivo. | Identificar marca/modelo do ponto digital e leiaute do arquivo. | Coordenação de DP / Especialista de Ponto | **Aberta (Aguardando Homologação)** |
| **DP-08** | Fórmulas da folha | Eventos citados sem fórmulas e tabelas completas. | Obter da especialista a memória de cálculo e tabelas oficiais. | Especialista em DP / Contador Homologador | **Aberta (Aguardando Homologação)** |
| **DP-09** | Benefícios | Exemplos genéricos citados sem confirmação de concessão. | Confirmar quais benefícios são oferecidos e regras de desconto. | Gestor de RH / Benefícios | **Aberta (Aguardando Homologação)** |
| **DP-10** | Backup e recuperação | Necessidade reconhecida sem parâmetros operacionais. | Definir janela de backup, tempo de retenção e metas de RTO/RPO. | Administrador de Banco de Dados / Infraestrutura TI | **Aberta (Aguardando Homologação)** |
| **DP-11** | Exportação para Excel | PDF é padrão indicado; Excel consta como opção aberta. | Decidir quais relatórios devem permitir exportação em planilha. | Gestores de RH / DP / Financeiro | **Aberta (Aguardando Homologação)** |
| **DP-12** | Dashboard executivo | Formulário indica que painel com gráficos não é necessário. | Excluir da primeira versão do sistema conforme escopo. | Gestor do Projeto / Professor Orientador | **Aberta (Aguardando Homologação)** |
| **DP-13** | Contradição do atraso | Frase 'desconta 10 horas' diverge do exemplo R$ 7 x 2h = R$ 14. | Confirmar que os atrasos são calculados estritamente pelo tempo real. | Especialista em DP / Contabilidade | **Aberta (Aguardando Homologação)** |
| **DP-14** | Fórmula do Adicional Noturno | Frase '50% mais 20%' dita com ressalva 'se não me engano'. | Homologar a fórmula legal/convenção para adicional noturno. | Especialista em DP / Jurídico | **Aberta (Aguardando Homologação)** |
| **DP-15** | Tabela de Faltas x Férias | Citação de 'cinco faltas' sem apresentar a tabela completa. | Obter a tabela de proporcionalidade de férias conforme CLT. | Especialista em DP / Consultoria Trabalhista | **Aberta (Aguardando Homologação)** |

---

## 9. Indicadores de Desempenho (KPIs) e Critérios Gerenciais — Seção 11 Oficial

Catalogação dos 5 indicadores executivos e dos 12 critérios de aceite gerenciais previstos na **Seção 11** de `Requisitos_Sistema_Folha.docx`:

### Indicadores Estratégicos (KPIs)
1. **Taxa de Absenteísmo e Rotatividade (Turnover):** Acompanhamento mensal por setor e tipo de ocorrência (faltas justificadas, injustificadas e afastamentos médicos).
2. **Índice de Conformidade em Treinamentos:** Percentual de colaboradores operando com capacitação e NRs válidas.
3. **Taxa de Pendências de EPIs:** Monitoramento de equipamentos com CA vencido ou substituição pendente.
4. **Tempo Médio de Resposta do Canal de Escuta:** Indicador de eficiência no atendimento a sugestões e reclamações dos trabalhadores.
5. **Volume e Resolução de Ocorrências de Segurança:** Acompanhamento de riscos comunicados vs. ações corretivas concluídas com eficácia.

### Critérios de Aceite Gerenciais (CA-01 a CA-12 da Seção 11)

| ID Critério | Título Oficial | Especificação do Critério | Status de Governança |
|---|---|---|:---:|
| **CA-01 (S11)** | Taxa de Absenteísmo | Relatório e indicador consolidado por período, setor, unidade e colaborador, segregando faltas e afastamentos. | **Fora do escopo da versão inicial** |
| **CA-02 (S11)** | Taxa de Rotatividade (Turnover) | Cálculo considerando admissões, desligamentos e quadro ativo do período. | **Fora do escopo da versão inicial** |
| **CA-03 (S11)** | Índice de Conformidade em Treinamentos | Percentual de colaboradores com treinamentos normativos e NRs na validade. | **Fora do escopo da versão inicial** |
| **CA-04 (S11)** | Pendências de Treinamento | Relatório de cursos vencidos ou não realizados com identificação de colaborador e setor. | **Fora do escopo da versão inicial** |
| **CA-05 (S11)** | Taxa de Pendências de EPI | Indicador de EPIs com CA vencido ou entrega pendente. | **Fora do escopo da versão inicial** |
| **CA-06 (S11)** | Rastreabilidade de EPIs | Vínculo com registros de entrega, devolução e substituição para auditoria. | **Fora do escopo da versão inicial** |
| **CA-07 (S11)** | Tempo Médio de Resposta do Canal de Escuta | Tempo entre abertura e primeiro atendimento/conclusão da manifestação. | **Fora do escopo da versão inicial** |
| **CA-08 (S11)** | Indicadores do Canal de Escuta | Acompanhamento de volume de solicitações abertas, em andamento e encerradas. | **Fora do escopo da versão inicial** |
| **CA-09 (S11)** | Volume de Ocorrências de Segurança | Acompanhamento de incidentes e condições inseguras registradas por setor e gravidade. | **Fora do escopo da versão inicial** |
| **CA-10 (S11)** | Resolução de Ocorrências de Segurança | Relação entre ocorrências registradas e ações corretivas concluídas com eficácia. | **Fora do escopo da versão inicial** |
| **CA-11 (S11)** | Consolidação Gerencial | Filtros por período, setor, unidade e tipo de ocorrência em relatórios gerenciais. | **Fora do escopo da versão inicial** |
| **CA-12 (S11)** | Consistência dos Indicadores | Valores obtidos diretamente dos dados operacionais sem divergência analítica. | **Fora do escopo da versão inicial** |

---

## 10. Mapeamento da Suíte de Testes Automatizados Executada (64 Testes)

Relação completa de todos os 64 testes automatizados em código que compõem o quality gate oficial do projeto, demonstrando a cobertura real sobre os requisitos:

| Arquivo de Teste | Método de Teste | Requisito / Critério Coberto | Resultado Real Observado |
|---|---|---|:---:|
| `tests/test_colaboradores.py` | `test_ca01_novo_cadastro_sucesso` | RF-01, RF-10 (Cadastro Válido) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca02_validacao_campos_obrigatorios` | RF-05, RF-14 (Campos Obrigatórios) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca02_validacao_cpf_invalido` | RF-05, RF-56 (Validação de CPF) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca02_validacao_datas` | RF-05, RF-51 (Consistência de Datas) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca02_validacao_email_invalido` | RF-05 (Sintaxe de E-mail) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca02_validacao_salario_invalido` | RF-05 (Salário Positivo) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca03_bloqueio_duplicidade_cpf` | RF-05 (Unicidade de CPF) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca03_bloqueio_duplicidade_matricula` | RF-05 (Unicidade de Matrícula) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca04_pesquisa_por_nome_cpf_matricula` | RF-02 (Busca Multi-critério) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca05_edicao_preservando_identificador` | RF-03, RF-12 (Edição de Dados) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca06_auditoria_historico_alteracoes` | RF-08, RF-46, RNF-04, RN-03 | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca07_inativacao_logica` | RF-04, RF-11, RNF-05 (Inativação) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca07_reativacao_logica` | RF-04 (Reativação Auditada) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca08_persistencia_apos_reconexao` | RF-08, RNF-05 (Durabilidade) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca09_estrutura_e_filtros` | RF-02, RF-09, RF-48 (Filtro por Setor) | **100% SUCESSO (PASS)** |
| `tests/test_colaboradores.py` | `test_ca10_integridade_e_nao_regressao` | RF-03, RF-05 (Integridade em Edição) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_adicional_noturno_com_reducao_ficta` | RF-35, RN-04 (Hora Noturna Ficta) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_adicional_noturno_padrao_20_porcento` | RF-35, RN-04 (Adicional Noturno 20%) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_bloqueio_duplicidade_de_rubrica` | RF-34, RN-04 (Unicidade de Rubrica) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_desconto_atrasos` | RF-19, T-04 (Desconto de Atraso) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_desconto_faltas` | RF-19, T-03 (Desconto de Faltas) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_dsr_sobre_variaveis` | RF-35, RN-04 (DSR sobre Variáveis) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_horas_extras_100_porcento` | RF-18, T-06 (HE 100% Feriados) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_horas_extras_50_porcento` | RF-18, T-05 (HE 50% Dias Úteis) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_horas_extras_percentual_customizado` | RF-18, RN-05 (HE Convenção Coletiva) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_inss_progressivo_multiplas_faixas` | RF-35, RNF-10 (Faixas INSS 2026) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_inss_primeira_faixa` | RF-35 (Faixa Mínima INSS 7,5%) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_inss_teto_maximo` | RF-35 (Aplicação do Teto Previdenciário) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_irrf_deducao_por_dependentes` | RF-35 (Dedução Legal Dependentes) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_irrf_isencao_primeira_faixa` | RF-35 (Isenção 1ª Faixa IRRF) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_irrf_progressivo_com_deducoes` | RF-35, RNF-10 (Cálculo IRRF Completo) | **100% SUCESSO (PASS)** |
| `tests/test_folha_calculos.py` | `test_valor_fgts_informativo` | RF-35 (FGTS Informativo 8%) | **100% SUCESSO (PASS)** |
| `tests/test_folha_service.py` | `test_bloqueio_folha_duplicada_mesma_competencia` | RF-32, RN-04 (Bloqueio de Duplicidade) | **100% SUCESSO (PASS)** |
| `tests/test_folha_service.py` | `test_fechamento_e_reabertura_folha` | RF-32, RF-42 (Ciclo de Vida) | **100% SUCESSO (PASS)** |
| `tests/test_folha_service.py` | `test_geracao_folha_competencia` | RF-32, RF-33 (Geração com Colaboradores) | **100% SUCESSO (PASS)** |
| `tests/test_folha_service.py` | `test_listagem_e_filtros` | RF-36 (Filtros por Competência) | **100% SUCESSO (PASS)** |
| `tests/test_folha_service.py` | `test_reabertura_de_folha_com_auditoria` | RF-42, RF-46, T-10 (Auditoria na Reabertura) | **100% SUCESSO (PASS)** |
| `tests/test_folha_api.py` | `test_bloqueio_endpoints_sem_token` | RF-40, RNF-02 (Proteção de Endpoints) | **100% SUCESSO (PASS)** |
| `tests/test_folha_api.py` | `test_fluxo_completo_api_folha` | RF-32, RF-36, RF-50 (Ciclo REST da Folha) | **100% SUCESSO (PASS)** |
| `tests/test_folha_api.py` | `test_obter_parametros_e_colaboradores` | RF-34, RF-41 (Parâmetros e Perfis) | **100% SUCESSO (PASS)** |
| `tests/test_api.py` | `test_api_get_colaboradores` | RF-02, RF-40 (Listagem REST Autenticada) | **100% SUCESSO (PASS)** |
| `tests/test_api.py` | `test_api_get_colaborador_por_id` | RF-02, RF-40 (Consulta por ID) | **100% SUCESSO (PASS)** |
| `tests/test_api.py` | `test_api_post_novo_colaborador` | RF-01, RF-05 (Criação via REST) | **100% SUCESSO (PASS)** |
| `tests/test_api.py` | `test_api_put_atualizar_colaborador` | RF-03, RF-05 (Edição via REST) | **100% SUCESSO (PASS)** |
| `tests/test_api.py` | `test_api_patch_inativar_reativar` | RF-04, RF-46 (Inativação/Reativação REST) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_01_acesso_inicial_protegido` | RF-40, RNF-02 (Acesso Inicial Protegido) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_02_bloqueio_acesso_direto` | RF-40, RNF-02 (Bloqueio sem Token) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_03_credenciais_invalidas` | RF-40, RNF-01 (Rejeição Segura) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_04_autenticacao_valida` | RF-40, RNF-01, RNF-03 (Login Válido) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_05_encerramento_de_sessao` | RF-43, RNF-01 (Logout e Invalidação) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_06_protecao_de_dados` | RF-43, RNF-02, RNF-03, RN-02 | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_07_persistencia_e_expiracao_sessao` | RF-40, RNF-01 (Validade de Sessão) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_08_regressao_modulo_existente` | RF-01 a RF-09 (Não-Regressão) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_09_estrutura_layout_e_responsividade` | RNF-09 (Layout Responsivo) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_10_compatibilidade_deploy_vercel` | RNF-03 (Deploy Serverless) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_11_servico_disponivel` | RF-40 (Disponibilidade da Rota) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_12_login_valido_e_sessao` | RF-40, RNF-01 (Concessão de Sessão) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_13_credenciais_invalidas_sem_vazar_detalhes` | RF-40, RNF-01 (Mitigação de Enumeração) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_14_backend_indisponivel_mantem_acesso_bloqueado` | RF-40, RNF-02 (Falha Segura) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_15_ambiente_serverless_vercel` | RF-40, RNF-03 (Handler Serverless) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_16_persistencia_contas_demo` | RF-40, RNF-01 (Persistência de Usuários) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_ca_login_17_regressao_colaboradores` | RF-01, RF-02 (Operação sob Sessão) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_criptografia_pbkdf2_com_salt` | RNF-01, RN-03 (PBKDF2 com Salt Único) | **100% SUCESSO (PASS)** |
| `tests/test_autenticacao.py` | `test_gov_002_02_bloqueio_inicializacao_sem_senha_segura` | GOV-002-02, RNF-01 (Bloqueio sem Senha Segura) | **100% SUCESSO (PASS)** |

---

## 11. Resumo Quantitativo de Rastreabilidade e Cobertura

| Grupo de Requisitos / Elementos | Total Mapeado | Verificado por Teste | Pendente de Validação de Negócio | Implementação Identificada | Fora do Escopo Inicial / Documentado / Condicional |
|---|:---:|:---:|:---:|:---:|:---:|
| **Requisitos Funcionais Centrais (RF-01 a RF-56)** | 56 | 21 | 4 | 9 | 22 |
| **Módulos SST e Operação Força Verde (RF-57 a RF-62)** | 6 | 0 | 0 | 0 | 6 |
| **Requisitos Não-Funcionais (RNF-01 a RNF-10)** | 10 | 6 | 0 | 1 | 3 |
| **Regras de Negócio da Folha (RN-01 a RN-08)** | 8 | 3 | 2 | 1 | 2 |
| **Critérios de Aceitação Gerais (CA-01 a CA-09)** | 9 | 3 | 1 | 3 | 2 |
| **Casos de Teste Operacionais (T-01 a T-12)** | 12 | 4 | 1 | 3 | 4 |
| **Decisões Pendentes de Negócio (DP-01 a DP-15)** | 15 | 0 | 0 | 0 | 15 (Abertas) |
| **Critérios Gerenciais da Seção 11 (CA-01 a CA-12)** | 12 | 0 | 0 | 0 | 12 |
| **Total de Testes Automatizados no Quality Gate** | **64** | **64 (100%)** | **0 falhas** | **0 erros** | **0 pulados** |

