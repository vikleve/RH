# ADR-002: Camada de Segurança, Autenticação e Gestão de Sessões

## Status
Aprovado

## Data
2026-10-28

## Contexto
O sistema gerencia informações altamente confidenciais e protegidas por legislação trabalhista e pela LGPD (dados cadastrais de colaboradores, dependentes menores de idade e salários). Sistemas de RH não podem permitir acessos anônimos a rotas protegidas nem armazenar credenciais em texto puro.

## Decisão
Implementar uma camada de segurança robusta baseada em:
1. **Derivação de Chave Criptográfica:** Algoritmo **PBKDF2-HMAC-SHA256** com 100.000 iterações e salt aleatório de 16 bytes por usuário gerado via `secrets.token_hex`.
2. **Comparação em Tempo Constante:** Utilização de `hmac.compare_digest` para evitar ataques de temporização (*timing attacks*).
3. **Sessões Criptográficas:** Tokens aleatórios de 32 bytes (64 caracteres hexadecimais) armazenados no banco com data de expiração e flag de revogação.
4. **Proteção Dual de Transporte:** Suporte a cookies de sessão com atributos `HttpOnly`, `SameSite=Lax` e `Secure` (quando HTTPS), além do cabeçalho `Authorization: Bearer <token>`.
5. **Bloqueio de Acesso Anônimo:** Endpoints `/api/colaboradores` e `/api/folha` retornam imediatamente `HTTP 401 Unauthorized` caso o visitante não possua sessão autenticada válida.
6. **Controle de Perfis (RBAC):** Estrutura inicial de papéis: `administrador`, `analista_rh` e `operador_dp`.

## Consequências
- Atende plenamente aos requisitos de segurança e auditoria (RF-40, RF-41, RF-43, RNF-01 a RNF-03).
- Validação 100% automatizada nos testes unitários e de integração (`test_autenticacao.py`).
