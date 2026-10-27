# Mapeamento de Regras & Dúvidas para Validação com a Equipe de RH

Documento integrante do **Módulo 1: Cadastro de Colaboradores** (Projeto Interdisciplinar RH & GTI).
Este documento consolida as decisões tomadas nesta primeira versão e relaciona os tópicos que dependem de validação formal da equipe de Recursos Humanos para as próximas etapas do projeto.

---

## 1. Classificação dos Campos do Formulário

| Campo | Seção | Classificação no Módulo 1 | Justificativa / Regra Aplicada | Status para o RH |
|---|---|:---:|---|:---:|
| **Nome Completo** | Pessoais | **Obrigatório** | Identificação primária; exige ao menos nome e um sobrenome. | Aprovado |
| **CPF** | Pessoais | **Obrigatório** | Chave fiscal única perante a Receita Federal; validação matemática de 11 dígitos. | Aprovado |
| **RG** | Pessoais | **Opcional** | Nem todos os colaboradores possuem RG recente ou padronizado no ato da contratação. | **A validar com RH** |
| **Data de Nascimento** | Pessoais | **Obrigatório** | Necessária para verificação de maioridade ou jovem aprendiz (mínimo de 14 anos). | Aprovado |
| **E-mail** | Contato | **Obrigatório** | Canal padrão de comunicação institucional e envio de informativos futuros. | Aprovado |
| **Telefone / WhatsApp** | Contato | **Opcional** | Recomendado para contato de emergência e avisos operacionais. | **A validar com RH** |
| **Endereço Completo** | Contato | **Opcional** | Campos estruturados (Rua, Nº, Bairro, Cidade, UF, CEP) para futuro cálculo de vale-transporte. | **A validar com RH** |
| **Matrícula** | Profissional | **Obrigatório** | Identificador funcional exclusivo e imutável do colaborador na organização. | Aprovado |
| **Data de Admissão** | Profissional | **Obrigatório** | Marco inicial do vínculo trabalhista e contagem de tempo de serviço. | Aprovado |
| **Cargo / Função** | Profissional | **Obrigatório** | Definição da atividade desempenhada conforme o organograma da empresa. | Aprovado |
| **Setor / Departamento** | Profissional | **Obrigatório** | Centro de custo e alocação do colaborador. | Aprovado |
| **Salário-base** | Profissional | **Obrigatório** | Remuneração contratual fixa; valor estritamente numérico e maior que zero. | Aprovado |
| **Situação do Vínculo** | Profissional | **Obrigatório** | 'Ativo' ou 'Inativo'. Padrão 'Ativo' no cadastro. Inativação é lógica e preserva o histórico. | Aprovado |
| **Dependentes** | Dependentes | **Opcional** | Registro dinâmico de dependentes para futuras deduções fiscais e previdenciárias. | Aprovado |
| **Fotografia** | Pessoais | **Não implementada** | Decidido não exigir armazenamento de arquivos sem definição prévia da política de LGPD. | Aprovado |

---

## 2. Dúvidas e Questões que Precisam de Validação da Equipe de RH

### Dúvida 1: Geração e Padrão da Matrícula Funcional
- **Situação atual:** O sistema permite que o usuário digite a matrícula manualmente (ex: `RH-1001`, `TI-2002`, `10045`), validando apenas a unicidade.
- **Pergunta ao RH:** A empresa adota uma numeração sequencial automática gerada pelo sistema (ex: `2026001`, `2026002`) ou cada departamento/filial define seu próprio prefixo manual?

### Dúvida 2: Obrigatoriedade de CPF para Dependentes
- **Situação atual:** O CPF do dependente foi configurado como opcional no formulário. Caso preenchido, é validado rigorosamente.
- **Pergunta ao RH:** Para fins de conformidade com o eSocial e dedução de Imposto de Renda Retido na Fonte (IRRF), a organização exigirá que recém-nascidos e crianças já possuam CPF cadastrado no ato da admissão, ou haverá prazo de carência para entrega?

### Dúvida 3: Graus de Parentesco Homologados
- **Situação atual:** Foi disponibilizada a lista: `Filho(a)`, `Cônjuge/Companheiro(a)`, `Pai/Mãe`, `Enteado(a)`, `Irmão(ã)`, `Outro`.
- **Pergunta ao RH:** Esta lista atende integralmente à política de concessão de benefícios (ex: plano de saúde) e dependência legal da organização, ou termos específicos devem ser adicionados ou restritos?

### Dúvida 4: Período de Experiência e Tipo de Contrato
- **Situação atual:** Não foram criadas regras trabalhistas adicionais além da data de admissão e situação (ativo/inativo).
- **Pergunta ao RH:** Para o próximo módulo, será necessário registrar o prazo do contrato de experiência (ex: 45 + 45 dias ou 30 + 60 dias) e o tipo de contratação (CLT Indeterminado, CLT Determinado, Aprendiz, Estágio)?

### Dúvida 5: Motivos Padronizados de Inativação / Desligamento
- **Situação atual:** Ao inativar um colaborador, o sistema oferece um campo de texto livre para registrar o motivo no histórico de auditoria.
- **Pergunta ao RH:** Desejam que seja fornecida uma lista suspensa padronizada de motivos (ex: *Demissão sem justa causa, Demissão com justa causa, Pedido de demissão, Término de contrato, Aposentadoria*) para facilitar futuros relatórios gerenciais de turnover?

---

## 3. Próximos Passos (Alinhamento GTI & RH)
Após a validação destas 5 questões pela equipe de RH, as parametrizações aprovadas serão integradas diretamente no banco de dados e nos validadores sem necessidade de reestruturação do módulo.

---

## 4. Módulo 2: Folha de Pagamento — Regras Parametrizadas & Itens de Cálculo

O Módulo de Folha de Pagamento opera com separação estrita entre a camada de apresentação e a camada de cálculo matemático (`backend/folha_calculos.py`).
**Nenhuma regra trabalhista ou encargo fiscal foi inventado ou colocado em código de forma rígida.** Todas as alíquotas, divisores, tetos e percentuais são parametrizados na tabela `folha_parametros`.

### Rubricas e Eventos Homologados:

| Código | Rubrica | Tipo | Base de Cálculo / Regra Parametrizada | Status |
|:---:|---|:---:|---|:---:|
| **001** | **Salário Base Mensal** | Provento | `(Salário-base / Dias do Mês) * Dias Trabalhados` | Homologado |
| **101** | **Horas Extras 50%** | Provento | `(Hora Normal * 1.50) * Quantidade de Horas` | Homologado |
| **102** | **Horas Extras 100%** | Provento | `(Hora Normal * 2.00) * Quantidade de Horas` (Domingos e Feriados) | Homologado |
| **103** | **Adicional Noturno 20%** | Provento | `(Hora Normal * 0.20) * Horas Noturnas` (Opção de Hora Ficta Reduzida 52m30s) | Homologado |
| **105** | **DSR sobre Variáveis** | Provento | `(Total HE + Adic. Noturno / Dias Úteis) * Domingos e Feriados` | Parametrizado |
| **201** | **Faltas Integrais** | Desconto | `(Salário-base / Dias do Mês) * Dias de Falta` | Homologado |
| **202** | **Atrasos / Saídas** | Desconto | `Hora Normal * Horas Decimais de Atraso` | Homologado |
| **501** | **INSS Retido** | Desconto | Cálculo progressivo por faixas salariais vigentes até o teto legal | Parametrizado |
| **502** | **IRRF Retido na Fonte** | Desconto | `(Base - INSS - Dependentes) * Alíquota - Parcela a Deduzir` | Parametrizado |
| **901** | **FGTS do Mês** | Informativo | `8.0% sobre a base remuneratória` (Depósito da empresa, não descontado) | Homologado |

### Pontos Parametrizados e Sinalizados para Homologação pelo Responsável de Folha:
1. **Regime de Proporcionalidade:** Mês comercial fixo de 30 dias (padrão CLT) ou dias de calendário civil (ex: 28 em fevereiro, 31 em outubro).
2. **Jornada Contratual:** Divisor padrão 220 horas (44h semanais), 200 horas (40h semanais) ou 180 horas (36h semanais).
3. **Redução da Hora Noturna:** Fator 1.142857 (52 minutos e 30 segundos) configurável como ativo ou inativo conforme categoria/CCT.
4. **Vigência das Tabelas:** As faixas e alíquotas do INSS e da Tabela Progressiva do IRRF possuem vigência configurável e histórico mantido.
