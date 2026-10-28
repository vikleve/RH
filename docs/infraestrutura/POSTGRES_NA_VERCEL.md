# PostgreSQL persistente na Vercel — Portal DP & RH

## Objetivo

A aplicação usa PostgreSQL quando encontra uma URL de conexão configurada. Em desenvolvimento local e em testes isolados, pode usar SQLite. Na Vercel, a aplicação não deve recorrer silenciosamente a SQLite temporário: funções serverless podem executar em instâncias diferentes, e o diretório temporário não é um banco compartilhado ou durável.

## Provedor recomendado

Use uma integração PostgreSQL do Vercel Marketplace, como Neon ou Supabase. O projeto já reconhece as variáveis `DATABASE_URL`, `POSTGRES_URL`, `POSTGRES_PRISMA_URL` e `POSTGRES_URL_NON_POOLING`, além da configuração individual `PGHOST`/`PGDATABASE`/`PGUSER`/`PGPASSWORD`.

Para este backend Python, escolha uma connection string PostgreSQL compatível com `psycopg2`. Prefira a URL indicada pelo provedor para aplicações serverless/connection pooling quando disponibilizada.

## Provisionamento do banco pelo painel

1. Abra o projeto **portal-dp-rh** na Vercel e acesse **Storage** ou **Marketplace**.
2. Instale uma integração PostgreSQL (Neon ou Supabase) na equipe `Vikleve`.
3. Crie um banco de desenvolvimento/teste separado do banco de produção quando o provedor permitir.
4. Conecte a integração ao projeto `portal-dp-rh` e selecione os ambientes apropriados.
5. Confirme que a integração adicionou uma variável de conexão PostgreSQL ao ambiente **Preview**. Para produção, conecte-a apenas quando o banco estiver revisado e as validações forem aprovadas.
6. Não copie valores de segredo para o GitHub, issues, pull requests, logs ou chat. Armazene credenciais no gerenciador de variáveis da Vercel.

A Vercel não oferece mais o antigo produto Vercel Postgres; use uma integração PostgreSQL do Marketplace.

## Como o projeto seleciona o banco

- Com `DATABASE_URL` ou outra URL PostgreSQL suportada: usa PostgreSQL via `psycopg2`.
- Em desenvolvimento local sem URL: usa SQLite local.
- Em testes que passam `db_path` explícito: usa SQLite isolado.
- Na Vercel sem URL PostgreSQL: a aplicação deve falhar explicitamente e informar que o banco persistente precisa ser configurado. Isso evita perda ou fragmentação de sessões e cadastros.

Na inicialização, `init_db()` cria tabelas ausentes no banco configurado. Antes de uma primeira utilização real, valide a criação do schema, o login, a persistência de sessão, a criação/consulta/edição de um colaborador sintético e a leitura dos mesmos dados em requisições subsequentes.

## Checklist de verificação

- [ ] A integração PostgreSQL está conectada ao projeto e ao ambiente correto.
- [ ] A variável de conexão está presente no ambiente de Preview, sem divulgar seu valor.
- [ ] Um novo deployment foi criado depois da configuração das variáveis.
- [ ] A conexão PostgreSQL abre com SSL e o schema é inicializado sem erros.
- [ ] Uma sessão de login continua válida em outra requisição serverless.
- [ ] Um registro sintético criado em uma requisição aparece numa nova requisição.
- [ ] Reiniciar/reimplantar a aplicação não elimina os registros de teste.
- [ ] O banco de Preview não contém dados reais de colaboradores.
- [ ] Backup e recuperação foram tratados em atividade própria; não considerar backup validado apenas porque o banco é persistente.

## Segurança

Não use a senha inicial de acesso como credencial do banco. Mantenha segredos distintos, restrinja o acesso ao projeto e ao banco, e use apenas dados fictícios durante a inspeção. A existência de uma URL de conexão não comprova por si só que o banco está pronto para produção.
