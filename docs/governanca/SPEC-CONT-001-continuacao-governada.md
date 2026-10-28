# SPEC-CONT-001 — Continuidade Governada do Sistema de Folha de Pagamento

**Projeto:** Portal DP & RH — Sistema de Departamento Pessoal e Recursos Humanos  
**Repositório:** https://github.com/vikleve/RH  
**Versão da spec:** 1.0 — proposta para validação  
**Estado:** Proposta; não significa aprovação formal nem implementação concluída  
**Base técnica observada:** repositório na branch `main`, estrutura Python + HTML/CSS/JavaScript, SQLite para desenvolvimento/testes e suporte em código para PostgreSQL.  
**Regra principal:** preservar o trabalho existente; não reescrever nem migrar tecnologias sem decisão documentada.

---

## 1. Objetivo

Estabelecer um processo seguro, verificável e gradual para dar continuidade ao sistema existente, desenvolvendo **uma especificação por vez**. Cada especificação deve ser analisada, planejada no Trello, implementada em pequenas mudanças no GitHub, testada e validada antes de ser considerada concluída.

Esta primeira especificação cobre o diagnóstico do estado atual, a organização da governança e a preparação da próxima entrega. Não autoriza alterar regras trabalhistas nem declarar o sistema pronto para uso real.

## 2. Contexto existente a preservar

Na árvore e na documentação atual do repositório são identificados:

- Cadastro de colaboradores e dependentes, validações, pesquisa, edição e inativação lógica.
- Autenticação, sessões, perfis de usuário e endpoints protegidos.
- Histórico de alterações/auditoria.
- Frontend em HTML, CSS e JavaScript.
- Backend em Python.
- Testes automatizados em `tests/`.
- Código do módulo de folha, incluindo cálculos, serviços, API e testes em partes da árvore do repositório.
- Uso de SQLite para desenvolvimento/testes e suporte condicional a PostgreSQL; há script de migração e arquivos SQL de migração.
- Arquivos e configuração para Vercel. A presença desses arquivos não significa que o deploy esteja ativo, que o banco seja durável no ambiente publicado ou que o uso real esteja aprovado.

**Atenção de estrutura:** o repositório contém diretórios `RH-main/` além dos diretórios da raiz e também um arquivo ZIP. Antes de mover/apagar/mesclar conteúdo, comparar as versões e identificar qual conjunto de arquivos é a fonte atual. Não apagar diretórios, bancos ou código nesta etapa.

**Atenção de segurança:** o README expõe credenciais de demonstração documentadas. Não usar essas credenciais em ambiente real. Verificar se credenciais ou dados reais foram versionados; remover dados sensíveis do histórico exige avaliação específica e não deve ser feito sem plano. Usar apenas dados fictícios/anônimos em testes. Credenciais iniciais devem vir de configuração segura e ser trocadas antes de qualquer ambiente compartilhado.

## 3. Escopo desta primeira entrega

### Incluído
1. Inspecionar a estrutura atual do repositório e identificar duplicações/versões divergentes.
2. Executar a suíte de testes disponível em ambiente local limpo e registrar o resultado real.
3. Conferir como o README, os testes e os arquivos do módulo de folha descrevem o estado atual.
4. Registrar funcionalidades como **documentadas**, **confirmadas por teste**, **não verificadas** ou **pendentes**.
5. Estabelecer rastreabilidade entre requisito, cartão Trello, issue/PR GitHub, código, teste e evidência.
6. Criar/atualizar documentação de governança sem alterar comportamento funcional do sistema.
7. Preparar a próxima especificação e sua lista de pendências.

### Fora de escopo
- Reescrever o backend ou frontend.
- Migrar definitivamente SQLite para PostgreSQL.
- Alterar fórmulas de folha, INSS, IRRF, FGTS, horas extras, adicional noturno, férias, rescisão ou banco de horas.
- Conectar o sistema a dados reais de colaboradores, relógio de ponto, eSocial, bancos ou sistemas externos.
- Publicar o sistema ou declará-lo adequado para uso produtivo.
- Remover arquivos, bancos ou histórico do Git sem análise e autorização.

## 4. Requisitos desta spec

### RF-CONT-01 — Inventário técnico
A equipe deve listar as principais pastas, módulos, pontos de entrada, arquivos de configuração, suíte de testes e scripts de migração. Deve identificar arquivos duplicados ou versões paralelas sem apagá-los.

**Aceitação:** inventário salvo em documentação do repositório, com indicação dos caminhos considerados ativos, dúvidas e evidências usadas.

### RF-CONT-02 — Verificação reproduzível de testes
Executar os testes existentes em ambiente local controlado, documentando comando, versão de Python/dependências, data, total executado e falhas/erros. Não copiar o status do README como resultado novo.

**Aceitação:** relatório com resultado observado. Se não for possível executar, registrar o bloqueio e os passos exatos para reproduzir; não declarar aprovação.

### RF-CONT-03 — Matriz de estado das funcionalidades
Preparar uma matriz com: ID do requisito ou critério, funcionalidade, arquivo(s) relacionado(s), teste relacionado, evidência, estado e pendência.

Estados permitidos:
- **Documentado:** aparece na especificação/documentação.
- **Confirmado por teste:** teste pertinente foi executado com sucesso no ambiente descrito.
- **Implementado, não verificado:** há código identificado, mas a verificação ainda não foi realizada.
- **Falhou:** a verificação foi executada e falhou.
- **Pendente de decisão:** falta regra ou aprovação do responsável competente.
- **Fora do escopo atual:** não será desenvolvido nesta etapa.

**Aceitação:** nenhum recurso é chamado de “concluído” sem evidência verificável apropriada.

### RF-CONT-04 — Continuidade sem regressão
Mudanças posteriores devem preservar as funcionalidades existentes ou documentar explicitamente a alteração aprovada. Executar testes de regressão relevantes antes de aceitar mudanças.

**Aceitação:** alteração acompanhada de testes pertinentes e resultado registrado; defeitos existentes não devem ser ocultados por mudanças na documentação.

### RF-CONT-05 — Governança Trello/GitHub
Cada tarefa de desenvolvimento deve ter um cartão Trello com ID, objetivo, responsável, critérios de aceitação, dependências, riscos e link à issue/PR GitHub. Requisitos e testes devem conservar seus identificadores ao longo do processo.

**Aceitação:** para a primeira entrega, o cartão principal liga-se à documentação/PR ou issue correspondente; não há tarefa funcional sem rastreabilidade.

### RF-CONT-06 — Segurança de dados e credenciais
Usar dados fictícios/anônimos. Não registrar segredos, senhas reais, CPF real, dados de saúde ou informações salariais reais em issues, cartões, capturas de tela ou logs do projeto.

**Aceitação:** checklist de revisão de segredos/dados executado. Qualquer suspeita de exposição é registrada e tratada antes da publicação de novas mudanças.

### RF-CONT-07 — Pendências e decisões
Registrar dúvidas como itens separados, indicando descrição, impacto, responsável sugerido, aprovador competente, evidência/documento necessário e estado. A equipe não deve inventar regras de negócio para desbloquear a implementação.

**Aceitação:** pendências de regras trabalhistas, arquitetura, banco de dados, backup e publicação permanecem abertas até aprovação explícita ou decisão documentada.

## 5. Critérios de aceitação global

A spec só pode ser encerrada quando:

- [ ] Inventário técnico foi revisado pela equipe.
- [ ] Testes foram executados e o resultado observado foi registrado, ou o bloqueio está descrito com precisão.
- [ ] Matriz de estado de funcionalidades foi criada.
- [ ] Possíveis divergências entre raiz, diretório `RH-main/` e arquivo ZIP foram documentadas sem exclusão automática.
- [ ] Revisão inicial de segredos e dados potencialmente sensíveis foi registrada.
- [ ] Pendências e decisões estão visíveis e têm responsáveis sugeridos.
- [ ] Cartão do Trello e artefatos GitHub estão relacionados.
- [ ] Um colega revisou a entrega; decisões de negócio são encaminhadas ao responsável de RH/professor, quando aplicável.

A aprovação desta spec não representa aprovação para uso produtivo.

## 6. Fluxo de trabalho spec por spec

1. **Analisar:** entender o requisito e localizar o que já existe.
2. **Clarificar:** registrar dúvidas; pedir decisão ao responsável competente.
3. **Aprovar para desenvolvimento:** confirmar escopo e critérios de aceitação.
4. **Planejar:** decompor em tarefas no Trello com responsáveis e dependências.
5. **Implementar:** branch curta e alterações pequenas; não trabalhar diretamente em `main` como prática padrão, se o fluxo de branches estiver disponível para a equipe.
6. **Revisar:** comparar a mudança com o requisito e verificar riscos.
7. **Testar:** unitários, integração, segurança e regressão conforme aplicável.
8. **Validar:** registrar evidência e aprovação.
9. **Concluir:** fechar o cartão só após satisfazer os critérios.
10. **Aprender:** documentar defeitos e ajustar o processo para a spec seguinte.

## 7. Trello — modelo de cartão

**Título:** `SPEC-CONT-001 — Diagnóstico e preparação governada do projeto`

**Descrição do cartão:**
- Objetivo: inventariar o sistema atual, verificar testes e preparar a próxima entrega sem refazer funcionalidades.
- Fonte da verdade: repositório GitHub e documentos versionados; Trello é usado para acompanhamento.
- Critérios de aceitação: RF-CONT-01 a RF-CONT-07 e seção 5 desta spec.
- Responsável de execução: a definir pela equipe.
- Revisor: sugerido — outro integrante da equipe.
- Aprovador acadêmico: professor orientador, conforme combinado com a equipe.
- Aprovador das regras de negócio: representante competente de RH/DP; se indisponível, manter a decisão pendente.
- Links: preencher depois de criar o cartão, issue e/ou PR.
- Evidências: inventário, relatório de testes, matriz de estado, registro de pendências e revisão de segurança.

**Listas sugeridas:** Backlog / A especificar → Em análise → Pronta para desenvolver → Em desenvolvimento → Em testes/Revisão → Aprovada/Concluída. Usar “Bloqueada/Pendências” quando uma dependência impedir avanço. Não marcar itens bloqueados como concluídos.

## 8. GitHub — fluxo sugerido

- Manter `main` como referência estável.
- Criar branch de trabalho com nome como `docs/spec-cont-001-governanca`.
- Abrir issue com este ID e critérios de aceitação.
- Fazer mudanças pequenas e revisáveis.
- Abrir pull request ligando a issue; incluir testes executados, resultado e limitações.
- Não usar o GitHub como armazenamento de documentos com dados reais de funcionários.
- Não fazer merge se o teste pertinente estiver falhando ou se houver decisão de negócio não aprovada necessária ao escopo.
- Se os colaboradores preferirem commits diretos por limitação de fluxo, registrar a exceção e pelo menos exigir revisão das mudanças antes de declarar a entrega aceita.

## 9. Riscos e controles

| Risco | Controle nesta etapa |
|---|---|
| Refazer código que já existe | Inventário antes de implementar; comparar arquivos e versões. |
| Tratar README como prova de funcionamento | Executar testes e registrar evidência atual. |
| Regras de cálculo incorretas | Não alterar fórmulas sem aprovação documentada de RH/DP. |
| Perda de histórico/dados | Não excluir bancos/arquivos; usar cópia de trabalho e controle de versão. |
| Exposição de credenciais/dados | Revisar repositório e artefatos; usar dados fictícios; tratar exposição antes de publicação. |
| Confusão sobre a fonte válida do código | Documentar diferenças entre raiz, `RH-main/` e ZIP; não mesclar automaticamente. |
| Migração prematura do banco | Tratar PostgreSQL e estratégia de persistência como decisão arquitetural separada. |
| Mudanças sem rastreabilidade | Vincular Trello, issue/PR, requisito, teste e evidência. |

## 10. Pendências — não presumir decisão

| ID | Pendência | Responsável sugerido | Critério para decidir |
|---|---|---|---|
| DP-ARCH-01 | Definir a arquitetura-alvo e justificar a manutenção da stack atual versus eventual migração. | Liderança técnica + professor | Decisão registrada com custo, risco, aprendizado e compatibilidade considerados. |
| DP-DB-01 | Definir banco para cada ambiente e requisitos de persistência/produção. | Liderança técnica | Teste de conexão, migração, integridade e recuperação; decisão aprovada. |
| DP-RULE-01 | Validar fórmulas e parâmetros da folha. | Profissional responsável de RH/DP/contabilidade | Casos de cálculo aprovados e documentados; tabela/parâmetros com vigência e fonte. |
| DP-RULE-02 | Resolver regras de horas extras, adicional noturno, banco de horas, férias e rescisão. | RH/DP e responsável competente | Exemplos de cálculo, exceções e critérios de aprovação definidos. |
| DP-DATA-01 | Confirmar volume e natureza dos dados de teste. | Equipe + responsável de dados | Nenhum dado real desnecessário é usado; política de teste documentada. |
| DP-SEC-01 | Avaliar credenciais de demonstração descritas na documentação e possível exposição no histórico. | Responsável técnico | Plano de tratamento aprovado e credenciais seguras no ambiente usado. |
| DP-BKP-01 | Definir frequência, retenção, destino, RPO/RTO e teste de restauração. | Responsável técnico + professor/gestor | Valores e procedimentos aprovados; restauração demonstrada antes de uso real. |
| DP-DEP-01 | Definir se e onde haverá deploy de demonstração/uso real. | Equipe + professor | Ambiente, armazenamento persistente, custos, proteção de acesso e limites documentados. |
| DP-RH-01 | Responder às dúvidas existentes em `ESPECIFICACAO_RH.md`. | Responsável competente de RH | Decisões registradas e refletidas na especificação sem apagar o histórico. |

Os responsáveis acima são sugestões; não significam que já aceitaram a responsabilidade.

## 11. Próxima especificação funcional sugerida

Após a SPEC-CONT-001, selecionar **uma única especificação** para desenvolvimento. A escolha deve levar em conta:
- requisitos já aprovados;
- dependências técnicas;
- risco e tamanho;
- critérios de aceitação testáveis;
- ausência de decisão de negócio bloqueante.

Se o objetivo imediato for avançar na folha, primeiro validar o conjunto de regras e casos de cálculo existente. Só depois escolher uma função delimitada da folha e criar uma spec própria. Não implementar a folha inteira em uma única tarefa.

## 12. Histórico e aprovação

| Versão | Descrição | Estado |
|---|---|---|
| 1.0 | Primeira proposta para continuidade governada, baseada na estrutura observada do repositório e nas orientações da equipe. | Aguardando revisão/aprovação |

**Aprovação da equipe:** a preencher  
**Revisão acadêmica:** a preencher  
**Decisões de negócio relacionadas:** a preencher

---

**Nota de integridade:** este documento é uma especificação de trabalho proposta. Não afirma que os testes atuais passaram, que todas as funcionalidades estão seguras, que a auditoria é suficiente, que backups foram implementados, ou que o sistema está pronto para uso real. Essas afirmações dependem de verificação e evidência.
