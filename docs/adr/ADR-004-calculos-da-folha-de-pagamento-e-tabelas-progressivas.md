# ADR-004: Módulo de Folha de Pagamento e Regras de Cálculos Trabalhistas

## Status
Proposto / Pendente de Validação de Negócio (DP-08, DP-14, DP-15)

## Data
2026-10-28

## Contexto
O cálculo de folha de pagamento no Brasil é regido pela Consolidação das Leis do Trabalho (CLT), legislação previdenciária e regulamentação da Receita Federal. Erros de arredondamento, faixas incorretas ou falta de rastreabilidade de memórias de cálculo podem gerar passivos trabalhistas e fiscais. Conforme identificado no documento oficial de requisitos (`Requisitos_Sistema_Folha.docx`), as decisões pendentes DP-08, DP-14 e DP-15 demandam homologação formal por parte do especialista de Departamento Pessoal e Contabilidade antes de serem declaradas definitivas.

## Decisão
Estruturar tecnicamente o módulo de Folha de Pagamento com as seguintes premissas arquiteturais preliminares, mantendo-as parametrizáveis e auditáveis:
1. **Precisão Numérica Estrita:** Todos os cálculos e memórias de cálculo operam com precisão decimal (`round(valor, 2)` com divisores técnicos de 220 horas e 30 dias, pendente de validação formal em DP-13).
2. **Tabela Progressiva de INSS:** Aplicação preliminar da alíquota progressiva por faixas salariais (7,5%, 9%, 12%, 14%) com respeito ao teto previdenciário vigente (sujeita a atualização e homologação formal periódica).
3. **Cálculo Progressivo de IRRF:** Dedução prévia da contribuição de INSS e dedução legal por dependente homologado, aplicando a tabela progressiva com parcela a deduzir.
4. **Encargos e Variáveis Trabalhistas:**
   - Horas extras com adicional técnico de 50% e 100% (parametrizável para percentuais acordados em CCT/ACT).
   - Adicional noturno urbano (20%) com cálculo técnico de redução ficta da hora noturna (fator ~1,142857), aguardando homologação do enquadramento rural/urbano da empresa (DP-02, DP-14).
   - DSR (Descanso Semanal Remunerado) sobre horas extras e variáveis.
   - Desconto proporcional de faltas integrais e horas de atraso.
   - FGTS com alíquota padrão de 8% calculado em caráter informativo (sem desconto do colaborador).
5. **Ciclo de Vida da Folha e Rastreabilidade:**
   - Estados formais: `Aberta`, `Calculada`, `Fechada` e `Cancelada`.
   - **Bloqueio de Duplicidade:** Chave de unicidade `(colaborador_id, competencia)`.
   - **Fechamento e Trilha de Auditoria:** Uma vez fechada, a folha bloqueia novas edições ordinárias; qualquer reabertura exige justificativa formal e identificação do responsável em `folha_historico`.

## Consequências e Ressalvas
- A implementação técnica provê memória de cálculo detalhada e transparente para conferência da equipe de DP/RH, contabilidade e professor orientador.
- **Ressalva de Governança:** O módulo não deve ser declarado como formalmente aprovado ou em total conformidade legal até a conclusão das validações de negócio DP-08 (tabelas e eventos), DP-13 (critério de atraso), DP-14 (adicional noturno) e DP-15 (proporcionalidade de férias).
- 16 testes de cálculo matemático + 5 testes de serviço + 3 testes de API REST garantem que as regras codificadas funcionam exatamente conforme especificadas tecnicamente.
