# Diretrizes de Contribuição e Governança de Código

Bem-vindo ao projeto **Portal DP & RH** (Projeto Interdisciplinar dos cursos de **Recursos Humanos** e **Gestão da Tecnologia da Informação**).

Para manter a governança, integridade técnica e rastreabilidade acadêmica exigidas pelo corpo docente, todos os colaboradores devem seguir rigorosamente este guia.

---

## 1. Fluxo de Trabalho Git (GitFlow Simplificado)

1. **Branch `main` (Estável):**
   - Código auditado, testado e em estado de lançamento.
   - **Proibido commit direto na `main`**. Todas as alterações devem entrar via **Pull Request (PR)** aprovado.

2. **Padrão de Criação de Branches:**
   As branches devem ser criadas a partir da `main` com prefixos semânticos:
   - `feat/<nome-da-funcionalidade>`: Para novas funcionalidades (ex: `feat/calculo-rescisao`).
   - `fix/<descricao-do-bug>`: Para correções de erros (ex: `fix/deducao-inss-faixa-2`).
   - `docs/<assunto>`: Para documentação e governança (ex: `docs/matriz-rastreabilidade`).
   - `test/<nome-do-teste>`: Para inclusão ou melhoria de testes.
   - `refactor/<modulo>`: Para melhorias estruturais sem alteração de regra de negócio.

---

## 2. Padrão de Mensagens de Commit (Conventional Commits)

Utilizamos o padrão **Conventional Commits**:

```text
<tipo>(<escopo>): <descrição sucinta em português no imperativo>

[corpo opcional explicando o motivo e contexto]

[rodapé opcional com referência a issue: Closes #123]
```

### Tipos Permitidos:
- `feat`: Nova funcionalidade para o usuário ou sistema.
- `fix`: Correção de bug ou falha de regra.
- `docs`: Alterações exclusivamente em arquivos de documentação.
- `style`: Formatação, pontuação (sem impacto no código executável).
- `refactor`: Refatoração interna de código que não altera comportamento.
- `test`: Criação ou atualização de testes automatizados.
- `chore`: Atualização de dependências, tarefas de CI/CD ou configurações do projeto.

**Exemplos Válidos:**
- `feat(folha): adiciona cálculo progressivo de INSS conforme tabela 2026`
- `fix(auth): corrige tempo de expiração do token de sessão`
- `docs(governanca): adiciona ADR-003 sobre unificação do repositório`
- `test(colaboradores): adiciona caso de teste para validação de CPF inválido`

---

## 3. Higiene do Repositório (Regras de Governança Estrita)

1. **Arquivos Proibidos no Git:**
   - Nunca commite arquivos de banco de dados (`*.db`, `*.sqlite`, `*.sqlite3`).
   - Nunca commite diretórios de compilação ou bytecode (`__pycache__`, `*.pyc`).
   - Nunca commite arquivos compactados (`.zip`, `.rar`, `.tar.gz`).
   - Nunca commite credenciais, senhas, tokens ou arquivos `.env`.

2. **Proteção de Dados Pessoais (LGPD):**
   - É expressamente proibido usar dados reais de colaboradores da empresa ou colegas de sala (CPFs reais, endereços reais, salários reais) em testes ou exemplos.
   - Utilize exclusivamente dados fictícios e gerados por algoritmos sintéticos de teste.

---

## 4. Como Executar os Testes Localmente

Antes de abrir qualquer Pull Request, certifique-se de que a suíte completa de 63 testes passe com 100% de sucesso:

```powershell
# Executar a suíte completa consolidada
python tests/executar_todos_testes.py
```

Ou usando `uv`:
```powershell
uv run python tests/executar_todos_testes.py
```

---

## 5. Critérios de Aceitação para Aprovação de Pull Request (Definition of Done - DoD)

Um Pull Request só será aprovado e integrado à branch `main` se atender integralmente ao seguinte checklist:
1. **Compilação e Execução Limpa:** Nenhum erro sintático ou de execução.
2. **100% de Testes Aprovados:** Suíte automatizada sem falhas ou regressões.
3. **Revisão por Pares (Peer Review):** Pelo menos um outro membro do time (ou professor orientador) deve aprovar a mudança.
4. **Rastreabilidade:** O PR deve referenciar a respectiva especificação funcional (`SPEC-*`) ou issue correspondente.
5. **Aderência aos Padrões de Código:** Formatação respeitando `.editorconfig` e linter.
