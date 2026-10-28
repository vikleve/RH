# SPEC-GOV-002 — Validação da Governança e Fidelidade à Especificação Oficial

**Projeto:** Portal DP & RH — Sistema de Departamento Pessoal e Recursos Humanos  
**Repositório:** https://github.com/vikleve/RH  
**Versão:** 1.0 — proposta para execução  
**Estado:** Aguardando revisão da equipe e validação acadêmica  
**Documento de requisitos de referência:** `Requisitos_Sistema_Folha.docx` (documento oficial fornecido pela equipe)  
**Especificação anterior relacionada:** `docs/governanca/SPEC-CONT-001-continuacao-governada.md`  
**Tipo:** Governança, rastreabilidade, segurança de configuração e qualidade contínua  
**Princípio:** manter a implementação existente e tornar as afirmações do repositório verificáveis; não inventar nem aprovar regras de negócio.

---

## 1. Objetivo

Validar e corrigir a documentação e os controles de governança adicionados recentemente ao repositório para que sejam consistentes com o documento oficial de requisitos, com o código realmente existente e com evidências reproduzíveis.

A governança já recebeu uma estrutura importante: limpeza da árvore do repositório, manual com oito pilares, política de dados, matriz de rastreabilidade, cinco ADRs, templates de contribuição e documentação de CI/CD. Esta spec não pretende refazer esse trabalho. Ela fecha as lacunas e inconsistências identificadas antes de iniciar uma nova funcionalidade de negócio.

## 2. Hierarquia das fontes e fidelidade

Aplicar a seguinte hierarquia:

1. **Fonte primária de requisitos:** `Requisitos_Sistema_Folha.docx`.
2. **Decisões de negócio aprovadas:** apenas decisões com responsável competente, data, conteúdo da aprovação e evidência registrada.
3. **Decisões de arquitetura aprovadas:** ADRs, limitados às decisões técnicas que de fato foram aprovadas.
4. **Código e testes:** evidência do comportamento existente; não alteram, por si só, a regra de negócio.
5. **README, manual de governança, política LGPD e RTM:** documentos de implementação e acompanhamento que devem refletir as fontes acima.

Se uma implementação, ADR ou documento contradizer a fonte primária, não reescrever a regra de forma silenciosa. Registrar a divergência, manter o ID original e encaminhar a decisão ao responsável indicado. Não converter uma proposta em regra aprovada apenas porque já existe código para ela.

A cópia original do documento de requisitos deve permanecer intacta. Qualquer matriz ou resumo derivado deve identificar claramente que é derivado e manter os IDs e o sentido dos requisitos.

## 3. Constatações iniciais que orientam esta spec

As constatações abaixo foram identificadas ao revisar os arquivos e commits recentes. Elas devem ser confirmadas durante a execução, mas não devem ser ignoradas:

1. **Unificação do repositório:** o commit `92c154937f2517789f9ebed9f6959eeb72255d9b` consolidou a raiz e removeu as pastas duplicadas e artefatos que apareciam antes em `RH-main/`, `RH-main Camylla/`, ZIPs, bancos locais e bytecode. A SPEC-CONT-001 foi escrita antes dessa mudança; não repetir a limpeza já feita. Documentar o resultado como histórico e verificar apenas se a raiz continua canônica.
2. **CI/CD ainda não ativada na localização correta:** os arquivos `ci.yml` e `security.yml` aparecem em `docs/ci-cd/`, enquanto o GitHub Actions exige os workflows em `.github/workflows/`. A pasta `.github/workflows/` não foi encontrada na árvore atual. As execuções recentes visíveis no GitHub são de Pages build/deployment; não constituem evidência de execução da suíte de testes, Ruff, Bandit ou pip-audit.
3. **Credenciais conhecidas no repositório:** o README publica senhas de demonstração, `.env.example` repete valores de senha e contém um valor fixo de exemplo para chave de sessão, e a implementação de provisionamento deve ser conferida em busca de valores padrão conhecidos. Esses valores não devem ser usados em ambientes compartilhados ou reais.
4. **Matriz de rastreabilidade incompleta em relação à fonte:** a RTM atual mapeia parte dos requisitos e declarações de testes, mas não cobre todos os grupos presentes no documento oficial, incluindo RNF-06 a RNF-10 e RF-57 a RF-62. A cobertura completa e a situação de cada requisito precisam ser demonstradas, não presumidas.
5. **Alegações de conformidade e aprovação:** o manual, a política LGPD, os badges e a RTM contêm afirmações como “plenamente conforme”, “aprovado” e “100% de aprovação”. Essas expressões só podem permanecer quando houver a evidência correspondente e o tipo de aprovação estiver claro.
6. **Conflito sobre acesso do colaborador:** a política LGPD afirma que o colaborador pode consultar dados e comprovantes pelo sistema. O requisito RF-44 da fonte primária exclui o acesso direto do colaborador na versão inicial. A documentação deve ser harmonizada com RF-44; não implementar portal de autoatendimento por inferência.
7. **Regras de folha em validação:** o ADR-004 apresenta parâmetros e regras de cálculo como decisão aprovada, mas a fonte primária exige que fórmulas e parâmetros sejam aprovados pela especialista e mantém diversas decisões DP-01 a DP-15 pendentes. Não alterar os cálculos nesta spec; corrigir o status documental ou anexar evidência de aprovação válida.
8. **Auditoria, backup e recuperação:** as afirmações de auditoria “imutável” e de conformidade devem ser confrontadas com código e testes. RNF-07 e RNF-08 exigem backup periódico automatizado e procedimento de restauração documentado e testado; não afirmar que estão atendidos sem evidência.

Estas constatações não autorizam concluir que o sistema está inseguro em todos os aspectos ou que nenhum teste local tenha passado. Elas indicam que o estado de aprovação não está demonstrado por evidência de CI/CD no GitHub na revisão realizada.

## 4. Escopo

### Incluído
- Ativar e validar os quality gates do GitHub Actions.
- Retirar credenciais padrão conhecidas dos exemplos/documentação e impedir provisionamento com senhas padrão conhecidas.
- Atualizar a RTM para representar integralmente os requisitos e decisões do documento oficial.
- Corrigir afirmações de aprovação, conformidade e funcionamento que não estejam apoiadas por evidência.
- Harmonizar o escopo documentado, especialmente o RF-44 de ausência de acesso direto do colaborador na versão inicial.
- Revisar o status do ADR-004 sem modificar fórmulas de negócio.
- Corrigir links internos inválidos na documentação.
- Registrar o estado verificado de RNF-07/RNF-08 e manter os parâmetros operacionais necessários como pendências quando ainda não aprovados.

### Fora de escopo
- Alterar fórmulas de INSS, IRRF, FGTS, salário proporcional, horas extras, adicional noturno, DSR, faltas, férias, rescisão ou banco de horas.
- Resolver as decisões de negócio DP-01 a DP-15 sem aprovação da pessoa competente.
- Desenvolver portal de autoatendimento, versão mobile, recrutamento e seleção, integração genérica com serviços externos ou outros itens excluídos/não confirmados pela fonte.
- Mudar a arquitetura de aplicação, migrar o banco de dados ou reescrever os módulos.
- Declarar conformidade legal final ou prontidão para uso produtivo.
- Reescrever o histórico do Git. Qualquer saneamento de histórico será uma ação separada, com avaliação e aprovação explícitas.

## 5. Requisitos desta spec

### GOV-002-01 — Quality gates executáveis
Os workflows oficiais devem residir em `.github/workflows/ci.yml` e `.github/workflows/security.yml`. Os arquivos de `docs/ci-cd/` devem ser referências/documentação ou ser mantidos de forma que não existam duas definições operacionais divergentes.

A pipeline principal deve:
- executar nos eventos definidos de push e pull request;
- configurar as versões Python suportadas pelo projeto e instaladas/testadas pela equipe;
- instalar dependências de forma reproduzível;
- executar Ruff, Bandit e a suíte consolidada real em `tests/executar_todos_testes.py`;
- executar a verificação de cobertura configurada em `pyproject.toml`, mantendo o limiar de cobertura documentado consistente com o comando real;
- exibir um resultado claro de sucesso ou falha no GitHub Actions.

A pipeline de segurança deve executar a auditoria de dependências e tornar erros da ferramenta/resultados relevantes visíveis. Não usar `|| true` nem mecanismo equivalente para ocultar indiscriminadamente falhas. Se uma política de exceções for necessária, ela deve ser explícita, justificada, ter responsável e prazo de revisão.

**Aceitação:** um push/PR de teste aciona os workflows reais e a página Actions mostra as execuções de lint, análise estática, testes, cobertura e auditoria. Nenhuma documentação afirma que uma pipeline está ativa antes disso. Falhas preexistentes são registradas e corrigidas ou deixam a spec bloqueada; não reduzir testes nem mudar regras de negócio apenas para obter uma marca verde.

### GOV-002-02 — Credenciais e configuração segura
- Remover senhas de demonstração conhecidas do README e de arquivos de configuração de exemplo.
- Manter `.env.example` como modelo sem valores de senha/chave utilizáveis. Variáveis secretas devem estar vazias ou conter somente instruções não funcionais.
- Revisar `backend/auth.py` e outros pontos de inicialização para identificar senhas padrão hardcoded. Não provisionar contas com credenciais padrão publicadas.
- Exigir configuração explícita e segura para credenciais iniciais em ambientes compartilhados; quando obrigatória e ausente, o sistema deve falhar com mensagem operacional clara em vez de usar uma senha conhecida.
- Adaptar os testes para usar credenciais sintéticas e isoladas por fixture/configuração de teste.
- Atualizar as instruções locais de configuração no README sem publicar segredos.
- Verificar se a chave `SESSION_SECRET_KEY` é realmente consumida pela aplicação; documentar seu propósito e exigir valor seguro onde aplicável, sem alegar que protege sessões se não houver uso efetivo.
- Se algum ambiente tiver utilizado as credenciais públicas de demonstração, registrar a necessidade de trocá-las. Não executar rotação em ambiente externo sem autorização.

**Aceitação:** busca no estado atual do repositório não encontra senhas/chaves padrão utilizáveis nos arquivos de execução, nos exemplos ou no README; testes comprovam que a inicialização segura não depende de credenciais públicas predefinidas e que a autenticação existente continua funcionando com configuração explícita.

### GOV-002-03 — RTM fiel ao documento oficial
Atualizar `docs/governanca/MATRIZ_RASTREABILIDADE.md` para incluir todos os requisitos e grupos constantes em `Requisitos_Sistema_Folha.docx`, preservando identificadores, nomes, condicionantes e sentido original:
- requisitos funcionais RF-01 a RF-56 exatamente conforme aparecem no documento, incluindo lacunas de numeração;
- requisitos adicionais RF-57 a RF-62;
- requisitos não funcionais RNF-01 a RNF-10;
- regras de negócio RN-01 a RN-08;
- cenários de aceitação CA-01 a CA-09 e casos de teste T-01 a T-12;
- decisões pendentes DP-01 a DP-15;
- KPIs/indicadores descritos na fonte, com seu estado e critério de aceitação quando aplicável.

Não criar requisitos para preencher lacunas na numeração. Requisitos condicionais ou fora da versão inicial devem continuar rastreáveis e ser marcados como condicionais/fora do escopo, não apagados.

Cada linha da RTM deve indicar, quando aplicável:
- ID da fonte e resumo fiel;
- módulo/arquivo(s) relacionados;
- teste automatizado ou caso de teste manual;
- evidência e data/commit de verificação;
- estado atual;
- dependência ou DP relacionada;
- responsável sugerido e aprovador competente, quando pendente.

Usar estados distintos, no mínimo: **documentado**, **implementação identificada**, **verificado por teste**, **pendente de validação de negócio**, **condicional**, **fora do escopo da versão inicial** e **falhou/não verificado**. Não usar “APROVADO” como sinônimo genérico de “há código”.

**Aceitação:** todos os IDs presentes na fonte estão representados na matriz ou em um registro associado, sem alteração silenciosa do significado. Cada status “verificado por teste” aponta para um teste executável e resultado efetivamente obtido.

### GOV-002-04 — Conformidade documental e escopo
- Corrigir o texto do manual e da política de dados que declara conformidade plena, homologação ou aprovação sem evidência formal.
- Substituir badges/declarações categóricas de conformidade LGPD por títulos neutros de documentação enquanto a revisão competente e a verificação de controles estiverem pendentes.
- Harmonizar a seção de direitos dos titulares com RF-44: a versão inicial não fornece login/portal direto ao colaborador. Não afirmar que funcionalidades de autoatendimento estão implementadas. A forma de atender solicitações por processo administrativo não deve ser convertida em um novo módulo sem requisito aprovado.
- Afirmar que uma política foi documentada, que um controle está implementado, que ele passou em teste e que foi aprovado por responsável competente como estados diferentes.
- Não definir novos períodos de retenção, bases legais, obrigações legais ou interpretações como fatos aprovados sem fonte e revisão apropriadas. Quando a fonte exigir definição organizacional, registrar o responsável e a decisão pendente.
- Corrigir links `file:///` em documentos Markdown para links relativos ao repositório, verificando que os destinos existam.
- Atualizar a contagem de testes e badges a partir da suíte real. Não usar números estáticos como prova de aprovação atual.

**Aceitação:** os documentos não se contradizem sobre escopo nem afirmam conformidade legal/operacional sem evidência. Os links internos são navegáveis no GitHub.

### GOV-002-05 — Status correto das decisões de arquitetura
- Revisar os cinco ADRs contra o código, a fonte de requisitos e as aprovações realmente registradas.
- Em particular, no ADR-004, se não houver validação documentada de RH/DP/contabilidade, atualizar o status para **proposto/pendente de validação de negócio** e marcar parâmetros trabalhistas/fiscais como preliminares. Não alterar os valores ou funções de cálculo no âmbito desta spec.
- Manter a decisão técnica de arquitetura separada da aprovação da regra de negócio. Um ADR não substitui a aprovação da especialista mencionada na fonte primária.
- Qualquer referência à tabela tributária, vigência, arredondamento, divisor, percentual ou regra coletiva precisa apontar para fonte/versão e evidência de validação; se não houver, registrar a pendência DP pertinente.
- Na SPEC-CONT-001, atualizar a observação sobre diretórios duplicados como retrato histórico anterior ao commit de unificação, ou identificá-la como superada por esta nova spec. Não executar novamente a limpeza já concluída.

**Aceitação:** o status de cada ADR e da SPEC-CONT-001 representa fielmente o que está aprovado, concluído, pendente ou superado. Nenhuma fórmula é alterada aqui.

### GOV-002-06 — Alegações de auditoria, backup e recuperação
- Confrontar os documentos de governança com o código e os testes para os RNF-04 e RNF-05: logs devem permitir identificar usuário, data/hora, IP e detalhes da operação, e alterações relevantes devem preservar valores anteriores e novos conforme exigido pela fonte.
- Não descrever o log como “imutável” se a imutabilidade não foi demonstrada por controle técnico/teste; usar “trilha de auditoria” até comprovação.
- Mapear RNF-07 e RNF-08 na RTM como não verificados/pendentes até que exista evidência de backup automatizado periódico e de restauração testada. Não apresentar scripts ou políticas documentais como evidência de execução.
- Preservar como pendências as definições de frequência, retenção, destino seguro, responsável, RPO/RTO ou outros parâmetros que ainda precisem de aprovação.

**Aceitação:** afirmações de auditoria e recuperação têm ligação a evidências concretas; RNF-07/RNF-08 não são marcados como atendidos sem demonstração funcional e teste de restauração.

### GOV-002-07 — Continuidade e não regressão
- Manter a estrutura canônica atual da raiz, sem restaurar diretórios duplicados.
- Não alterar o comportamento funcional do cadastro, autenticação, API ou módulo de folha além do mínimo necessário para remover credenciais padrão e possibilitar configuração segura.
- Executar todos os testes de regressão existentes. Se uma correção exigir alterar uma expectativa de teste, documentar a razão e demonstrar aderência à fonte primária; não remover um teste válido para contornar uma falha.
- Manter o fluxo de contribuição descrito em `CONTRIBUTING.md`: branch temática, issue/spec relacionada, pull request e revisão por outra pessoa. Não fazer commit direto na `main` como parte desta tarefa.

**Aceitação:** suíte e quality gates estão verdes na PR final. Se isso não for obtido, a PR não deve ser declarada concluída; a falha deve ser registrada com evidência.

## 6. Definition of Done — critérios globais de aceitação

- [ ] Workflows reais estão em `.github/workflows/` e são executados pelo GitHub Actions.
- [ ] O resultado da execução inclui lint, análise estática, suíte de testes, cobertura e auditoria de dependências.
- [ ] Credenciais padrão publicadas foram removidas dos arquivos atuais e o provisionamento seguro foi verificado por teste.
- [ ] RTM abrange todos os IDs e grupos da fonte primária, inclusive RF-57 a RF-62, RNF-01 a RNF-10, RN-01 a RN-08, CA-01 a CA-09, T-01 a T-12 e DP-01 a DP-15.
- [ ] Os status de teste e aprovação diferenciam código encontrado, teste executado e validação formal.
- [ ] Os documentos não afirmam acesso direto do colaborador na versão inicial; RF-44 é preservado.
- [ ] O ADR-004 não declara aprovadas regras de negócio sem evidência da especialista competente.
- [ ] Afirmações de conformidade LGPD, auditoria imutável, backup e recuperação estão respaldadas por evidência ou explicitamente marcadas como pendentes.
- [ ] Links relativos e badges/documentação de CI estão corretos.
- [ ] As decisões pendentes continuam abertas quando não existir aprovação.
- [ ] Uma pessoa diferente do implementador revisou a PR e o professor/responsável competente foi envolvido quando a decisão for acadêmica ou de negócio.
- [ ] Nenhuma alteração não autorizada foi feita em fórmulas trabalhistas, regras de negócio, dados reais ou histórico Git.

Se um item depender de decisão externa, registrar o bloqueio e não declarar a spec concluída por mera substituição do status.

## 7. Trello e GitHub — rastreabilidade obrigatória

Criar um cartão Trello dedicado a esta spec com o título:

**SPEC-GOV-002 — Validar governança, rastreabilidade e quality gates**

O cartão deve conter:
- link para esta spec;
- objetivo e escopo;
- checklist GOV-002-01 a GOV-002-07;
- responsável de execução e revisor, a serem definidos pela equipe;
- dependências e decisões pendentes;
- link da issue/PR GitHub;
- resultado de CI e evidências da RTM.

Não atribuir responsáveis pelo nome sem acordo. Não reutilizar um quadro genérico como se fosse o quadro oficial do projeto sem confirmar isso com a equipe. Se ainda não existir quadro do projeto, solicitar/obter confirmação da equipe antes de criar ou reorganizar um quadro existente.

No GitHub, trabalhar em branch própria e abrir PR. O título, a descrição e o cartão devem referenciar `SPEC-GOV-002`. Encerrar o cartão somente depois da revisão e dos critérios de aceitação.

## 8. Pendências da fonte que permanecem sem decisão

Esta spec não resolve DP-01 a DP-15. A RTM deve manter cada item exatamente ligado à pergunta original, com responsável sugerido e evidência necessária para decisão.

Exemplos de áreas que não podem ser presumidas: quantitativo real de colaboradores e filiais; segmento e convenções/acordos; fórmulas e percentuais de horas extras/adicional noturno; adoção e parâmetros de banco de horas; médias de férias; regras de admissão/desligamento; fornecedor/layout/frequência do ponto; layout/canal do arquivo financeiro; leiautes, certificados e tratamento de erros do eSocial; permissões e prazos de reabertura; política de retenção, exportação, migração e restauração. Os itens concretos devem ser transcritos e acompanhados conforme a tabela DP-01 a DP-15 do documento original, sem substituir a fonte por esta lista resumida.

## 9. Próxima etapa depois desta spec

Após a aceitação de SPEC-GOV-002, selecionar uma única especificação funcional por vez, usando a fonte primária e a RTM atualizada.

Uma candidata técnica importante é **RNF-07/RNF-08 — backup periódico e restauração testada**, porque a fonte exige rotina automatizada e recuperação documentada. Ela só deve virar uma spec de implementação depois de registrar as decisões operacionais necessárias, como frequência, retenção, local seguro, responsável e objetivos de recuperação. Outra funcionalidade de folha só deve avançar quando suas regras e critérios de cálculo estiverem formalmente aprovados.

Não implementar toda a folha, todas as integrações ou todos os requisitos RF-57 a RF-62 em um único ciclo.

## 10. Histórico

| Versão | Alteração | Estado |
|---|---|---|
| 1.0 | Spec corretiva criada após revisão dos commits de governança e comparação com o documento oficial de requisitos. | Aguardando revisão |

**Nota:** esta spec é uma instrução de trabalho. A sua existência não comprova que qualquer item foi corrigido, que os workflows passaram, que as regras de negócio foram aprovadas ou que o sistema está pronto para uso real.
