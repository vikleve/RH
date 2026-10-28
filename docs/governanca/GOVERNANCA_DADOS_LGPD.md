# Política de Governança de Dados e Conformidade LGPD (Lei nº 13.709/2018)

**Projeto:** Portal DP & RH — Sistema de Departamento Pessoal & Recursos Humanos  
**Contexto:** Projeto Interdisciplinar dos Cursos de Recursos Humanos & Gestão da Tecnologia da Informação  
**Versão:** 1.0 — Oficial  
**Status:** Aprovado para Governança do Projeto  

---

## 1. Objetivo e Escopo

O presente documento estabelece as diretrizes de **Governança de Dados** e as salvaguardas de privacidade e segurança adotadas no **Portal DP & RH**, garantindo total conformidade com a **Lei Geral de Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018)** e a Consolidação das Leis do Trabalho (CLT).

Este documento orienta os desenvolvedores, analistas de RH e auditores acadêmicos sobre como os dados pessoais de colaboradores e seus dependentes são coletados, processados, armazenados, protegidos e inativados.

---

## 2. Inventário e Classificação de Dados Tratados

O sistema classifica as informações manipuladas em três categorias fundamentais:

| Categoria de Dados | Campos Mapeados no Sistema | Nível de Sensibilidade | Finalidade e Base Legal (LGPD) |
|---|---|:---:|---|
| **Dados Pessoais Identificáveis** | Nome Completo, CPF, RG, Data de Nascimento, E-mail, Telefone, Endereço Residencial | Alto | Identificação formal, comunicação e cumprimento de obrigação legal/contratual (Art. 7º, II e V). |
| **Dados Pessoais de Crianças / Dependentes** | Nome do Dependente, Grau de Parentesco, Data de Nascimento, CPF do Dependente | Alto / Proteção Especial | Dedução legal de dependentes em Imposto de Renda e salário-família (Art. 14 da LGPD - Melhor interesse da criança). |
| **Dados Contratuais e Financeiros** | Matrícula, Cargo, Setor, Data de Admissão, Salário-base, Horas Extras, Descontos INSS/IRRF, FGTS, Salário Líquido | Crítico / Sigiloso | Execução do contrato de trabalho e obrigações tributárias e previdenciárias (Art. 7º, II e V). |
| **Dados de Autenticação e Rastreabilidade** | E-mail de login, Hash de senha (PBKDF2), Tokens de sessão, IP e Timestamps de auditoria | Crítico / Segurança | Controle de acesso, segurança da informação e prevenção a fraudes (Art. 7º, IX). |

> [!IMPORTANT]
> **Minimização de Dados (Art. 6º, III da LGPD):** O sistema coleta estritamente os campos indispensáveis para a gestão do vínculo trabalhista e processamento da folha. Não são armazenados dados sensíveis supérfluos (como biometria facial, dados de saúde não ocupacionais, convicções políticas ou religiosas).

---

## 3. Bases Legais Adotadas (Art. 7º da LGPD)

1. **Cumprimento de Obrigação Legal ou Regulatória (Art. 7º, II):**
   - Transmissão e retenção de informações para órgãos públicos (Receita Federal, INSS, Ministério do Trabalho e Emprego / eSocial).
2. **Execução de Contrato de Trabalho (Art. 7º, V):**
   - Pagamento de remuneração contratual, emissão de contracheques/holerites e gestão de benefícios.
3. **Exercício Regular de Direitos (Art. 7º, VI):**
   - Manutenção de histórico funcional e de folhas processadas para comprovação de quitação trabalhista e fiscal perante a Justiça do Trabalho.

---

## 4. Medidas Técnicas de Segurança e Proteção de Dados

### 4.1. Criptografia e Segregação de Credenciais
- **Senhas:** Nenhuma senha é armazenada em texto puro. Utiliza-se derivação de hash **PBKDF2-HMAC-SHA256** com 100.000 iterações e salt criptográfico individual de 16 bytes.
- **Sessões:** Identificadores de sessão são tokens pseudoaleatórios criptograficamente seguros de 32 bytes (64 caracteres hexadecimais), transmitidos preferencialmente em cookies com atributos de segurança (`HttpOnly`, `SameSite=Lax` e `Secure`).

### 4.2. Controle de Acesso Baseado em Perfis (RBAC)
- O acesso aos módulos de dados cadastrais e de folha é restrito a operadores autenticados.
- Três níveis de privilégio estruturados:
  - `operador_dp`: Consulta e lançamentos operacionais de folha.
  - `analista_rh`: Gestão cadastral de colaboradores e emissão de relatórios.
  - `administrador`: Gestão de parâmetros globais do sistema, auditoria e revogação de acessos.

### 4.3. Trilha de Auditoria Imutável (Logs de Conformidade)
Todas as operações de alteração de dados cadastrais e eventos de folha geram registros imutáveis nas tabelas `historico_alteracoes` e `folha_historico`, armazenando:
- Identificador do registro alterado;
- Campo afetado;
- Valor anterior (*before-state*);
- Novo valor (*after-state*);
- Data e hora exatas da transação (UTC/ISO 8601);
- Identificador do usuário responsável pela ação.

---

## 5. Ciclo de Vida dos Dados e Retenção

1. **Coleta e Entrada:** Efetuada via formulários validados com validação de formato e unicidade no cliente e no servidor.
2. **Armazenamento:** Persistência durável em SQLite com integridade referencial ou PostgreSQL gerenciado (Supabase com *Row Level Security*).
3. **Inativação Lógica vs. Exclusão Física:**
   - Em conformidade com as exigências da CLT e prazos prescricionais trabalhistas (Art. 11 da CLT: 5 anos até o limite de 2 anos após extinção do contrato; FGTS até 30 anos), o sistema **não realiza deleção física** de colaboradores que possuem histórico de folha.
   - Aplica-se a **inativação lógica** (`situacao = 'Inativo'`), preservando o histórico para auditoria judicial e previdenciária.
4. **Política de Testes e Desenvolvimento:**
   - Proibição absoluta de cópia de bases de produção para testes locais.
   - Utilização exclusiva de dados sintéticos e anônimos nos testes automatizados.

---

## 6. Direitos dos Titulares de Dados (Art. 18 da LGPD)

O sistema foi concebido para atender às solicitações legítimas dos colaboradores:
- **Confirmação e Acesso (Art. 18, I e II):** O colaborador pode visualizar seus dados cadastrais, dependentes e comprovantes de pagamento a qualquer tempo.
- **Correção de Dados Incompletos ou Inexatos (Art. 18, III):** O sistema oferece interface com controle de versões para retificação cadastral auditada.
- **Transparência e Informação (Art. 18, VII):** Fornecimento do holerite discriminado com todas as memórias de cálculo de proventos e descontos aplicados.
