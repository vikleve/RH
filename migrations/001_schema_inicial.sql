-- ============================================================================
-- MIGRAÇÃO SUPABASE / POSTGRESQL — SCHEMA BASE DO SISTEMA DP & RH
-- Arquivo: migrations/001_schema_inicial.sql
-- ============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS colaboradores (
    id               SERIAL PRIMARY KEY,
    matricula        TEXT UNIQUE NOT NULL,
    nome_completo    TEXT NOT NULL,
    cpf              TEXT UNIQUE NOT NULL,
    rg               TEXT,
    data_nascimento  TEXT NOT NULL,
    telefone         TEXT,
    email            TEXT NOT NULL,
    logradouro       TEXT,
    numero           TEXT,
    bairro           TEXT,
    cidade           TEXT,
    uf               TEXT,
    cep              TEXT,
    data_admissao    TEXT NOT NULL,
    cargo            TEXT NOT NULL,
    setor            TEXT NOT NULL,
    salario_base     NUMERIC(15,2) NOT NULL,
    situacao         TEXT NOT NULL DEFAULT 'ativo'
                     CHECK (situacao IN ('ativo', 'inativo')),
    criado_em        TEXT NOT NULL,
    atualizado_em    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dependentes (
    id               SERIAL PRIMARY KEY,
    colaborador_id   INTEGER NOT NULL
                     REFERENCES colaboradores(id) ON DELETE CASCADE,
    nome             TEXT NOT NULL,
    cpf              TEXT,
    parentesco       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS historico_alteracoes (
    id                  SERIAL PRIMARY KEY,
    colaborador_id      INTEGER NOT NULL
                        REFERENCES colaboradores(id) ON DELETE CASCADE,
    data_hora           TEXT NOT NULL,
    campo_alterado      TEXT NOT NULL,
    valor_anterior      TEXT,
    valor_novo          TEXT,
    usuario_responsavel TEXT NOT NULL DEFAULT 'Sistema/Administrador'
);

CREATE TABLE IF NOT EXISTS usuarios (
    id            SERIAL PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    usuario       TEXT UNIQUE NOT NULL,
    nome_completo TEXT NOT NULL,
    senha_hash    TEXT NOT NULL,
    salt          TEXT NOT NULL,
    perfil        TEXT NOT NULL
                  CHECK (perfil IN ('administrador', 'analista_rh', 'operador_dp')),
    status        TEXT NOT NULL DEFAULT 'ativo'
                  CHECK (status IN ('ativo', 'inativo')),
    criado_em     TEXT NOT NULL,
    ultimo_login  TEXT
);

CREATE TABLE IF NOT EXISTS sessoes (
    token        TEXT PRIMARY KEY,
    usuario_id   INTEGER NOT NULL
                 REFERENCES usuarios(id) ON DELETE CASCADE,
    criado_em    TEXT NOT NULL,
    expira_em    TEXT NOT NULL,
    revogado     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_colab_matricula ON colaboradores(matricula);
CREATE INDEX IF NOT EXISTS idx_colab_cpf       ON colaboradores(cpf);
CREATE INDEX IF NOT EXISTS idx_colab_nome      ON colaboradores(nome_completo);
CREATE INDEX IF NOT EXISTS idx_colab_situacao  ON colaboradores(situacao);
CREATE INDEX IF NOT EXISTS idx_colab_setor     ON colaboradores(setor);
CREATE INDEX IF NOT EXISTS idx_hist_colab      ON historico_alteracoes(colaborador_id);
CREATE INDEX IF NOT EXISTS idx_dep_colab       ON dependentes(colaborador_id);
CREATE INDEX IF NOT EXISTS idx_usuario_email   ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuario_login   ON usuarios(usuario);
CREATE INDEX IF NOT EXISTS idx_sessao_token    ON sessoes(token);
CREATE INDEX IF NOT EXISTS idx_sessao_user     ON sessoes(usuario_id);

ALTER TABLE colaboradores ENABLE ROW LEVEL SECURITY;
ALTER TABLE dependentes ENABLE ROW LEVEL SECURITY;
ALTER TABLE historico_alteracoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessoes ENABLE ROW LEVEL SECURITY;

COMMIT;

