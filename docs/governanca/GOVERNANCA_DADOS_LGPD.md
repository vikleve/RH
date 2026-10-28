# Política de Governança de Dados e Diretrizes LGPD (Lei nº 13.709/2018)

**Projeto:** Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos  
**Contexto:** Projeto Interdisciplinar dos Cursos de Recursos Humanos & Gestão da Tecnologia da Informação  
**Versão:** 2.0 — Alinhada à Especificação Oficial (SPEC-GOV-002)  
**Status:** Política Documentada / Em Validação Contínua  

---

## 1. Objetivo e Escopo

O presente documento estabelece as diretrizes de **Governança de Dados** e as salvaguardas de privacidade e segurança adotadas no **Portal DP & RH**, orientando o tratamento de dados pessoais em consonância com a **Lei Geral de Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018)**, a Consolidação das Leis do Trabalho (CLT) e os requisitos oficiais do projeto (`Requisitos_Sistema_Folha.docx`).

Este documento orienta os desenvolvedores, analistas de RH/DP e auditores sobre como os dados pessoais de colaboradores e dependentes são coletados, processados, armazenados, protegidos e inativados.

---

## 2. Inventário e Classificação de Dados Tratados

O sistema classifica as informações manipuladas em categorias formais:

| Categoria de Dados | Campos Mapeados no Sistema | Nível de Sensibilidade | Finalidade e Base Legal (LGPD) |
|---|---|:---:|---|
| **Dados Pessoais Identificáveis** | Nome Completo, CPF, RG, Data de Nascimento, E-mail, Telefone, Endereço Residencial | Alto | Identificação formal, comunicação funcional e cumprimento de obrigação legal/contratual (Art. 7º, II e V). |
| **Dados Pessoais de Crianças / Dependentes** | Nome do Dependente, Grau de Parentesco, Data de Nascimento, CPF do Dependente | Alto / Proteção Especial | Dedução legal de dependentes em Imposto de Renda e salário-família (Art. 14 da LGPD - Melhor interesse da criança). |
| **Dados Contratuais e Financeiros** | Matrícula, Cargo, Setor, Data de Admissão, Salário-base, Horas Extras, Descontos INSS/IRRF, FGTS, Salário Líquido | Crítico / Sigiloso | Execução do contrato de trabalho e cumprimento de obrigações tributárias e previdenciárias (Art. 7º, II e V). |
| **Dados de Autenticação e Rastreabilidade** | E-mail de login, Usuário, Hash de senha (PBKDF2), Salt, Tokens de sessão, Timestamps de auditoria | Crítico / Segurança | Controle de acesso corporativo, segurança da informação e prevenção a acessos não autorizados (Art. 7º, IX). |

> [!IMPORTANT]
> **Minimização de Dados (Art. 6º, III da LGPD):** O sistema coleta estritamente os campos necessários para a gestão do vínculo trabalhista e processamento da folha. Não são armazenados dados sensíveis supérfluos (como biometria facial, dados de saúde não ocupacionais, convicções políticas ou religiosas).

---

## 3. Bases Legais Adotadas (Art. 7º da LGPD)

1. **Cumprimento de Obrigação Legal ou Regulatória (Art. 7º, II):**
   - Transmissão e retenção de informações para órgãos fiscalizadores (Receita Federal, INSS, Ministério do Trabalho e Emprego / eSocial).
2. **Execução de Contrato de Trabalho (Art. 7º, V):**
   - Pagamento de remuneração contratual, emissão e conferência de contracheques e controle de encargos trabalhistas.
3. **Exercício Regular de Direitos (Art. 7º, VI):**
   - Manutenção de histórico funcional e de folhas processadas para comprovação de quitação trabalhista e previdenciária perante a Justiça do Trabalho.

---

## 4. Medidas Técnicas de Segurança e Proteção de Dados

### 4.1. Criptografia e Segregação de Credenciais
- **Senhas:** Nenhuma senha é armazenada em texto puro. Utiliza-se derivação de hash **PBKDF2-HMAC-SHA256** com 100.000 iterações e salt criptográfico individual de 16 bytes gerado aleatoriamente (`secrets.token_hex(16)`).
- **Sessões:** Identificadores de sessão são tokens pseudoaleatórios criptograficamente seguros de 32 bytes (64 caracteres hexadecimais), transmitidos preferencialmente em cookies com atributos de segurança (`HttpOnly`, `SameSite=Lax`).
- **Segurança Operacional:** Bloqueio mandatório de inicialização em ambientes compartilhados ou produtivos sem credencial administrativa forte definida via variável de ambiente (`ADMIN_INITIAL_PASSWORD`).

### 4.2. Controle de Acesso Baseado em Perfis (RBAC)
- O acesso aos módulos de dados cadastrais e de folha é restrito a operadores de RH/DP devidamente autenticados.
- Perfis estruturados no backend:
  - `analista_rh`: Gestão cadastral de colaboradores e consulta operacional de dados.
  - `administrador`: Gestão de parâmetros globais do sistema, reabertura de folhas fechadas, auditoria e controle de acessos.

### 4.3. Trilha de Auditoria Rastreável (Logs de Modificação)
Todas as operações de alteração de dados cadastrais e eventos de folha geram registros estruturados nas tabelas `historico_alteracoes` e `folha_historico`, armazenando:
- Identificador do registro alterado;
- Campo afetado;
- Valor anterior (*before-state*);
- Novo valor (*after-state*);
- Data e hora exatas da transação (UTC/ISO 8601);
- Identificador do usuário responsável pela ação.

> [!NOTE]
> **Ressalva de Auditoria:** Os registros de auditoria são mantidos de forma relacional no banco de dados da aplicação (`historico_alteracoes` e `folha_historico`). A solução atual não emprega mídia de gravação física WORM (*Write Once, Read Many*) nem assinatura digital qualificada em logs, constituindo uma trilha de auditoria rastreável a nível de software.

---

## 5. Ciclo de Vida dos Dados e Retenção

1. **Coleta e Entrada:** Efetuada exclusivamente por operadores autorizados via formulários validados no cliente e no servidor (`backend/validators.py`).
2. **Armazenamento:** Persistência durável em SQLite com integridade referencial ou PostgreSQL gerenciado.
3. **Inativação Lógica vs. Exclusão Física:**
   - Em conformidade com os prazos prescricionais trabalhistas (Art. 11 da CLT: 5 anos até o limite de 2 anos após extinção do contrato; FGTS até 30 anos), o sistema **não realiza deleção física** de colaboradores que possuem histórico no sistema.
   - Aplica-se a **inativação lógica** (`situacao = 'inativo'`), preservando o histórico para auditoria judicial e previdenciária.
4. **Política de Testes e Desenvolvimento:**
   - Proibição de cópia de bases reais para testes locais.
   - Utilização exclusiva de dados sintéticos e fictícios nos testes automatizados.
5. **Backup e Continuidade Operacional (RNF-07 e RNF-08):**
   - Parâmetros formais de periodicidade, retenção, RPO e RTO estão classificados como **Decisão Pendente (DP-10)** e aguardam homologação da equipe de infraestrutura de TI e gestão.

---

## 6. Exercício dos Direitos dos Titulares (Art. 18 da LGPD)

> [!IMPORTANT]
> **Modelo de Atendimento e Ausência de Autoatendimento na Versão 1.0 (RF-44 e DP-03):**  
> Em estrita conformidade com o requisito funcional **RF-44** (*"Não oferecer acesso direto ao colaborador na versão inicial"*) e a decisão pendente **DP-03**, o Portal DP & RH é uma ferramenta de uso exclusivo dos operadores internos do Departamento Pessoal e Recursos Humanos. Não há portal de autoatendimento (*self-service*) ou login direto para empregados na versão inicial.

Dessa forma, o atendimento aos direitos previstos no Art. 18 da LGPD é operacionalizado por meio de **fluxo administrativo interno**:

- **Confirmação e Acesso aos Dados (Art. 18, I e II):** O colaborador solicita formalmente ao Departamento Pessoal a consulta de seus dados cadastrais, dependentes ou histórico funcional. O operador de DP realiza a consulta interna autorizada e fornece a certidão/relatório correspondente.
- **Correção de Dados Incompletos, Inexatos ou Desatualizados (Art. 18, III):** Mediante apresentação de documentação comprobatória pelo colaborador, o operador de DP realiza a atualização cadastral no portal, gerando registro automático na trilha de auditoria (`historico_alteracoes`).
- **Transparência e Memória de Cálculo (Art. 18, VII):** A emissão e entrega de holerites e comprovantes de rendimentos discriminados é efetuada pelo Departamento Pessoal por canal físico ou corporativo homologado pela empresa.
