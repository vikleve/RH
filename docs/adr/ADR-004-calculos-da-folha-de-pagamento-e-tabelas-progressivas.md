# ADR-004: Módulo de Folha de Pagamento e Regras de Cálculos Trabalhistas

## Status
Aprovado

## Data
2026-10-28

## Contexto
O cálculo de folha de pagamento no Brasil é regido pela Consolidação das Leis do Trabalho (CLT), legislação previdenciária e regulamentação da Receita Federal. Erros de arredondamento, faixas incorretas ou falta de rastreabilidade de memórias de cálculo podem gerar passivos trabalhistas e fiscais.

## Decisão
Estruturar o módulo de Folha de Pagamento com as seguintes premissas arquiteturais:
1. **Precisão Numérica Estrita:** Todos os cálculos e memórias de cálculo operam com precisão decimal exata (`round(valor, 2)` com divisores padronizados de 220 horas e 30 dias).
2. **Tabela Progressiva de INSS:** Aplicação estrita da alíquota progressiva por faixas salariais (7,5%, 9%, 12%, 14%) com respeito ao teto previdenciário vigente.
3. **Cálculo Progressivo de IRRF:** Dedução prévia da contribuição de INSS e dedução legal por dependente homologado, aplicando a tabela progressiva com parcela a deduzir.
4. **Encargos e Variáveis Trabalhistas:**
   - Horas extras com adicional mínimo de 50% e 100% (ou percentuais customizados de CCT).
   - Adicional noturno urbano (20%) com cálculo de redução ficta da hora noturna (fator 52,5 min).
   - DSR (Descanso Semanal Remunerado) sobre horas extras e variáveis.
   - Desconto proporcional de faltas integrais e horas de atraso.
   - FGTS com alíquota padrão de 8% calculado em caráter informativo (sem desconto do colaborador).
5. **Ciclo de Vida da Folha e Imutabilidade:**
   - Estados formais: `Aberta`, `Calculada`, `Fechada` e `Cancelada`.
   - **Bloqueio de Duplicidade:** Chave de unicidade `(colaborador_id, competencia)`.
   - **Fechamento Auditável:** Uma vez fechada, a folha não permite alteração de valores a menos que seja formalmente reaberta por usuário com perfil autorizado, gerando log em `folha_historico`.

## Consequências
- Total conformidade com a legislação trabalhista brasileira vigente.
- Memória de cálculo transparente para conferência da equipe de RH e do professor.
- 19 testes unitários dedicados a cálculos matemáticos + 5 testes de serviço + 3 testes de API REST.
