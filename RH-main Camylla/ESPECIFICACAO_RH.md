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
