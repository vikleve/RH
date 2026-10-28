# Política de Segurança e Proteção de Dados

## 1. Compromisso com a Segurança

A equipe do projeto **Portal DP & RH** trata a segurança da informação e a privacidade de dados como pilares fundamentais de governança corporativa e conformidade legal (especialmente no tratamento de dados de colaboradores e folha de pagamento).

---

## 2. Padrões de Segurança Implementados

- **Criptografia de Senhas:** Derivação criptográfica via **PBKDF2-HMAC-SHA256** com 100.000 iterações e salt aleatório de 16 bytes.
- **Prevenção a Ataques de Temporização:** Utilização de `hmac.compare_digest` para validação de credenciais em tempo constante.
- **Gerenciamento Seguro de Sessões:** Tokens criptograficamente seguros de 32 bytes (64 hex), cookies `HttpOnly`, `SameSite=Lax` e `Secure` em HTTPS.
- **Proteção de Endpoints:** Todas as rotas de API sensíveis exigem autenticação ativa; acessos anônimos recebem resposta imediata `401 Unauthorized`.
- **Prevenção contra Enumeração de Usuários:** Mensagens neutras e genéricas para falhas de autenticação.
- **Trilha de Auditoria:** Registro rastreável em banco de dados de todas as alterações cadastrais e lançamentos de folha de pagamento, contendo usuário responsável, data/hora, valor anterior e novo valor.

---

## 3. Reporte Responsável de Vulnerabilidades

Se você identificar qualquer vulnerabilidade de segurança, falha de isolamento de dados ou vazamento potencial de credenciais:
1. **Não abra uma issue pública** contendo detalhes da vulnerabilidade.
2. Comunique os mantenedores do projeto ou o professor orientador através dos canais privados da equipe acadêmica.
3. Forneça um resumo detalhado, etapas para reprodução e impacto estimado.
4. A equipe atuará na correção prioritária e na publicação de um patch de segurança.
