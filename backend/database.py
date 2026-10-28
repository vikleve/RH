"""
Modulo de Banco de Dados — Dual-mode: PostgreSQL (producao) + SQLite (local/testes)
Camada de persistencia relacional com integridade referencial.
Atende a RF-01 a RF-09, CA-07, CA-08.

Em producao (Vercel): define DATABASE_URL como variavel de ambiente apontando para
  PostgreSQL externo (Supabase, Neon, Railway, etc).
Em desenvolvimento local: usa SQLite automaticamente se DATABASE_URL nao estiver definida.
Os testes passam db_path explicito => sempre SQLite isolado.
"""
import os
import sqlite3
import tempfile
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Configuracao de Ambiente e Drivers
# ─────────────────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    _env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(_env_file):
        load_dotenv(_env_file)
except ImportError:
    pass

_SQLITE_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(tempfile.gettempdir(), "colaboradores.db") if os.environ.get("VERCEL")
    else os.path.join(os.path.dirname(__file__), "..", "colaboradores.db")
)


def get_database_url() -> str:
    """
    Retorna a URL do banco PostgreSQL a partir das variaveis de ambiente:
    - DATABASE_URL (Supabase, Railway, Neon, Render, Docker, etc.)
    - POSTGRES_URL / POSTGRES_PRISMA_URL (integracao nativa da Vercel)
    - Variaveis individuais PGHOST, PGDATABASE, PGUSER, PGPASSWORD
    """
    url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or ""
    ).strip()

    if not url and os.environ.get("PGHOST") and os.environ.get("PGDATABASE"):
        user = os.environ.get("PGUSER", "postgres")
        pwd = os.environ.get("PGPASSWORD", "")
        host = os.environ.get("PGHOST", "localhost")
        port = os.environ.get("PGPORT", "5432")
        db = os.environ.get("PGDATABASE", "rh_db")
        url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    return url


# ─────────────────────────────────────────────────────────────────────────────
# Deteccao do modo
# ─────────────────────────────────────────────────────────────────────────────

def _usar_postgres(db_path: str = None) -> bool:
    """
    Retorna True se devemos usar PostgreSQL.
    Se db_path for fornecido explicitamente, usa SQLite com esse caminho (ex: testes).
    """
    if db_path:
        return False
    return bool(get_database_url())


def _get_pg_conn():
    """Retorna conexao psycopg2 para PostgreSQL com tratamento de DSN e SSL."""
    try:
        import psycopg2
    except ImportError:
        raise ImportError(
            "psycopg2-binary nao encontrado. Execute: pip install psycopg2-binary"
        )
    url = get_database_url()
    dsn = url.replace("postgres://", "postgresql://", 1)

    # Se for servico em nuvem (Neon, Supabase, Railway, Render) e nao especificar sslmode, garante sslmode=require
    if (
        "localhost" not in dsn
        and "127.0.0.1" not in dsn
        and "sslmode=" not in dsn
    ):
        dsn += ("&" if "?" in dsn else "?") + "sslmode=require"

    return psycopg2.connect(dsn)


def _get_sqlite_conn(db_path: str = None) -> sqlite3.Connection:
    """Retorna conexao SQLite para desenvolvimento local ou testes."""
    caminho = os.path.abspath(db_path if db_path else _SQLITE_PATH)
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_connection(db_path: str = None):
    """
    Retorna conexao ao banco adequado ao ambiente.

    - SQLite com db_path explicito: testes isolados e desenvolvimento controlado.
    - PostgreSQL: quando uma URL de banco persistente estiver configurada.
    - SQLite local: desenvolvimento fora da Vercel, sem URL de PostgreSQL.

    Em Vercel, nunca recorrer silenciosamente a SQLite em /tmp: esse sistema
    de arquivos nao e uma base compartilhada/duravel para funcoes serverless.
    """
    if _usar_postgres(db_path):
        return _get_pg_conn()

    if not db_path and os.environ.get("VERCEL") and not get_database_url():
        raise RuntimeError(
            "Banco persistente nao configurado na Vercel. "
            "Conecte um PostgreSQL pelo Marketplace e defina DATABASE_URL "
            "ou POSTGRES_URL no ambiente deste projeto. "
            "A aplicacao recusou o SQLite temporario para evitar perda ou "
            "fragmentacao de sessoes e cadastros entre funcoes serverless."
        )

    return _get_sqlite_conn(db_path)


# ─────────────────────────────────────────────────────────────────────────────
# DDL
# ─────────────────────────────────────────────────────────────────────────────

_DDL_COLABORADORES_PG = """
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
"""

_DDL_COLABORADORES_SQLITE = """
    CREATE TABLE IF NOT EXISTS colaboradores (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
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
        salario_base     REAL NOT NULL,
        situacao         TEXT NOT NULL DEFAULT 'ativo'
                         CHECK (situacao IN ('ativo', 'inativo')),
        criado_em        TEXT NOT NULL,
        atualizado_em    TEXT NOT NULL
    );
"""

_DDL_DEPENDENTES = """
    CREATE TABLE IF NOT EXISTS dependentes (
        id               {serial} PRIMARY KEY,
        colaborador_id   INTEGER NOT NULL
                         REFERENCES colaboradores(id) ON DELETE CASCADE,
        nome             TEXT NOT NULL,
        cpf              TEXT,
        parentesco       TEXT NOT NULL
    );
"""

_DDL_HISTORICO = """
    CREATE TABLE IF NOT EXISTS historico_alteracoes (
        id                  {serial} PRIMARY KEY,
        colaborador_id      INTEGER NOT NULL
                            REFERENCES colaboradores(id) ON DELETE CASCADE,
        data_hora           TEXT NOT NULL,
        campo_alterado      TEXT NOT NULL,
        valor_anterior      TEXT,
        valor_novo          TEXT,
        usuario_responsavel TEXT NOT NULL DEFAULT 'Sistema/Administrador'
    );
"""

_DDL_USUARIOS_PG = """
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
"""

_DDL_USUARIOS_SQLITE = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        email         TEXT UNIQUE NOT NULL,
        usuario       TEXT UNIQUE NOT NULL,
        nome_completo TEXT NOT NULL,
        senha_hash    TEXT NOT NULL,
        salt          TEXT NOT NULL,
        perfil        TEXT NOT NULL CHECK (perfil IN ('administrador', 'analista_rh', 'operador_dp')),
        status        TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
        criado_em     TEXT NOT NULL,
        ultimo_login  TEXT
    );
"""

_DDL_SESSOES = """
    CREATE TABLE IF NOT EXISTS sessoes (
        token        TEXT PRIMARY KEY,
        usuario_id   INTEGER NOT NULL
                     REFERENCES usuarios(id) ON DELETE CASCADE,
        criado_em    TEXT NOT NULL,
        expira_em    TEXT NOT NULL,
        revogado     INTEGER NOT NULL DEFAULT 0
    );
"""

_DDL_FOLHA_PARAMETROS_PG = """
    CREATE TABLE IF NOT EXISTS folha_parametros (
        id                          SERIAL PRIMARY KEY,
        codigo                      TEXT UNIQUE NOT NULL,
        descricao                   TEXT NOT NULL,
        vigencia_inicio             TEXT NOT NULL,
        vigencia_fim                TEXT,
        horas_mensais_padrao        NUMERIC(6,2) NOT NULL DEFAULT 220.00,
        dias_mes_padrao             INTEGER NOT NULL DEFAULT 30,
        percentual_he_padrao        NUMERIC(5,2) NOT NULL DEFAULT 50.00,
        percentual_he_extra         NUMERIC(5,2) NOT NULL DEFAULT 100.00,
        percentual_adicional_noturno NUMERIC(5,2) NOT NULL DEFAULT 20.00,
        aplicar_reducao_noturna     INTEGER NOT NULL DEFAULT 0,
        fator_reducao_noturna       NUMERIC(8,6) NOT NULL DEFAULT 1.142857,
        aplicar_inss                INTEGER NOT NULL DEFAULT 1,
        aplicar_irrf                INTEGER NOT NULL DEFAULT 1,
        aliquota_fgts               NUMERIC(5,2) NOT NULL DEFAULT 8.00,
        teto_inss                   NUMERIC(15,2) NOT NULL DEFAULT 8157.41,
        deducao_dependente_irrf     NUMERIC(15,2) NOT NULL DEFAULT 189.59,
        ativo                       INTEGER NOT NULL DEFAULT 1,
        validado_por_profissional   INTEGER NOT NULL DEFAULT 0,
        criado_em                   TEXT NOT NULL,
        atualizado_em               TEXT NOT NULL
    );
"""

_DDL_FOLHA_PARAMETROS_SQLITE = """
    CREATE TABLE IF NOT EXISTS folha_parametros (
        id                          INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo                      TEXT UNIQUE NOT NULL,
        descricao                   TEXT NOT NULL,
        vigencia_inicio             TEXT NOT NULL,
        vigencia_fim                TEXT,
        horas_mensais_padrao        REAL NOT NULL DEFAULT 220.00,
        dias_mes_padrao             INTEGER NOT NULL DEFAULT 30,
        percentual_he_padrao        REAL NOT NULL DEFAULT 50.00,
        percentual_he_extra         REAL NOT NULL DEFAULT 100.00,
        percentual_adicional_noturno REAL NOT NULL DEFAULT 20.00,
        aplicar_reducao_noturna     INTEGER NOT NULL DEFAULT 0,
        fator_reducao_noturna       REAL NOT NULL DEFAULT 1.142857,
        aplicar_inss                INTEGER NOT NULL DEFAULT 1,
        aplicar_irrf                INTEGER NOT NULL DEFAULT 1,
        aliquota_fgts               REAL NOT NULL DEFAULT 8.00,
        teto_inss                   REAL NOT NULL DEFAULT 8157.41,
        deducao_dependente_irrf     REAL NOT NULL DEFAULT 189.59,
        ativo                       INTEGER NOT NULL DEFAULT 1,
        validado_por_profissional   INTEGER NOT NULL DEFAULT 0,
        criado_em                   TEXT NOT NULL,
        atualizado_em               TEXT NOT NULL
    );
"""

_DDL_FOLHAS_PAGAMENTO_PG = """
    CREATE TABLE IF NOT EXISTS folhas_pagamento (
        id                          SERIAL PRIMARY KEY,
        colaborador_id              INTEGER NOT NULL
                                    REFERENCES colaboradores(id) ON DELETE RESTRICT,
        competencia                 TEXT NOT NULL,
        periodo_inicio              TEXT NOT NULL,
        periodo_fim                 TEXT NOT NULL,
        data_pagamento              TEXT,
        dias_trabalhados            NUMERIC(4,1) NOT NULL DEFAULT 30.0,
        dias_mes                    INTEGER NOT NULL DEFAULT 30,
        horas_mensais_divisor       NUMERIC(6,2) NOT NULL DEFAULT 220.00,
        salario_base_contratual     NUMERIC(15,2) NOT NULL,
        salario_base_proporcional   NUMERIC(15,2) NOT NULL,
        total_proventos             NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        total_descontos             NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        salario_liquido             NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        base_inss                   NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        base_fgts                   NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        valor_fgts_informativo      NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        base_irrf                   NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        situacao                    TEXT NOT NULL DEFAULT 'rascunho'
                                    CHECK (situacao IN ('rascunho', 'calculada', 'fechada', 'cancelada')),
        observacoes                 TEXT,
        parametro_id                INTEGER REFERENCES folha_parametros(id),
        criado_por                  TEXT NOT NULL,
        criado_em                   TEXT NOT NULL,
        atualizado_por              TEXT,
        atualizado_em               TEXT,
        fechado_por                 TEXT,
        fechado_em                  TEXT,
        CONSTRAINT unq_colab_competencia UNIQUE (colaborador_id, competencia)
    );
"""

_DDL_FOLHAS_PAGAMENTO_SQLITE = """
    CREATE TABLE IF NOT EXISTS folhas_pagamento (
        id                          INTEGER PRIMARY KEY AUTOINCREMENT,
        colaborador_id              INTEGER NOT NULL
                                    REFERENCES colaboradores(id) ON DELETE RESTRICT,
        competencia                 TEXT NOT NULL,
        periodo_inicio              TEXT NOT NULL,
        periodo_fim                 TEXT NOT NULL,
        data_pagamento              TEXT,
        dias_trabalhados            REAL NOT NULL DEFAULT 30.0,
        dias_mes                    INTEGER NOT NULL DEFAULT 30,
        horas_mensais_divisor       REAL NOT NULL DEFAULT 220.00,
        salario_base_contratual     REAL NOT NULL,
        salario_base_proporcional   REAL NOT NULL,
        total_proventos             REAL NOT NULL DEFAULT 0.00,
        total_descontos             REAL NOT NULL DEFAULT 0.00,
        salario_liquido             REAL NOT NULL DEFAULT 0.00,
        base_inss                   REAL NOT NULL DEFAULT 0.00,
        base_fgts                   REAL NOT NULL DEFAULT 0.00,
        valor_fgts_informativo      REAL NOT NULL DEFAULT 0.00,
        base_irrf                   REAL NOT NULL DEFAULT 0.00,
        situacao                    TEXT NOT NULL DEFAULT 'rascunho'
                                    CHECK (situacao IN ('rascunho', 'calculada', 'fechada', 'cancelada')),
        observacoes                 TEXT,
        parametro_id                INTEGER REFERENCES folha_parametros(id),
        criado_por                  TEXT NOT NULL,
        criado_em                   TEXT NOT NULL,
        atualizado_por              TEXT,
        atualizado_em               TEXT,
        fechado_por                 TEXT,
        fechado_em                  TEXT,
        CONSTRAINT unq_colab_competencia UNIQUE (colaborador_id, competencia)
    );
"""

_DDL_FOLHA_ITENS = """
    CREATE TABLE IF NOT EXISTS folha_itens (
        id                  {serial} PRIMARY KEY,
        folha_id            INTEGER NOT NULL
                            REFERENCES folhas_pagamento(id) ON DELETE CASCADE,
        codigo_evento       TEXT NOT NULL,
        descricao           TEXT NOT NULL,
        tipo                TEXT NOT NULL CHECK (tipo IN ('provento', 'desconto', 'informativo')),
        referencia          REAL DEFAULT 0.0,
        unidade_referencia  TEXT,
        valor_unitario      REAL DEFAULT 0.0,
        valor_total         REAL NOT NULL DEFAULT 0.0,
        origem              TEXT NOT NULL DEFAULT 'calculado'
                            CHECK (origem IN ('sistema', 'calculado', 'manual', 'importado')),
        memoria_calculo     TEXT,
        criado_em           TEXT NOT NULL
    );
"""

_DDL_FOLHA_HISTORICO = """
    CREATE TABLE IF NOT EXISTS folha_historico (
        id                  {serial} PRIMARY KEY,
        folha_id            INTEGER NOT NULL
                            REFERENCES folhas_pagamento(id) ON DELETE CASCADE,
        data_hora           TEXT NOT NULL,
        acao                TEXT NOT NULL,
        descricao           TEXT NOT NULL,
        dados_anteriores    TEXT,
        dados_novos         TEXT,
        usuario_responsavel TEXT NOT NULL
    );
"""

# ─────────────────────────────────────────────────────────────────────────────
# Inicializacao
# ─────────────────────────────────────────────────────────────────────────────

def init_db(db_path: str = None, auto_provision: bool = True):
    """
    Cria as tabelas e indices necessarios se nao existirem.
    Funciona tanto com PostgreSQL quanto com SQLite.
    """
    pg = _usar_postgres(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    serial = "SERIAL" if pg else "INTEGER"

    cursor.execute(_DDL_COLABORADORES_PG if pg else _DDL_COLABORADORES_SQLITE)
    cursor.execute(_DDL_DEPENDENTES.format(serial=serial))
    cursor.execute(_DDL_HISTORICO.format(serial=serial))
    cursor.execute(_DDL_USUARIOS_PG if pg else _DDL_USUARIOS_SQLITE)
    cursor.execute(_DDL_SESSOES)
    cursor.execute(_DDL_FOLHA_PARAMETROS_PG if pg else _DDL_FOLHA_PARAMETROS_SQLITE)
    cursor.execute(_DDL_FOLHAS_PAGAMENTO_PG if pg else _DDL_FOLHAS_PAGAMENTO_SQLITE)
    cursor.execute(_DDL_FOLHA_ITENS.format(serial=serial))
    cursor.execute(_DDL_FOLHA_HISTORICO.format(serial=serial))

    indices = [
        "CREATE INDEX IF NOT EXISTS idx_colab_matricula ON colaboradores(matricula);",
        "CREATE INDEX IF NOT EXISTS idx_colab_cpf       ON colaboradores(cpf);",
        "CREATE INDEX IF NOT EXISTS idx_colab_nome      ON colaboradores(nome_completo);",
        "CREATE INDEX IF NOT EXISTS idx_colab_situacao  ON colaboradores(situacao);",
        "CREATE INDEX IF NOT EXISTS idx_colab_setor     ON colaboradores(setor);",
        "CREATE INDEX IF NOT EXISTS idx_hist_colab      ON historico_alteracoes(colaborador_id);",
        "CREATE INDEX IF NOT EXISTS idx_dep_colab       ON dependentes(colaborador_id);",
        "CREATE INDEX IF NOT EXISTS idx_usuario_email   ON usuarios(email);",
        "CREATE INDEX IF NOT EXISTS idx_usuario_login   ON usuarios(usuario);",
        "CREATE INDEX IF NOT EXISTS idx_sessao_token    ON sessoes(token);",
        "CREATE INDEX IF NOT EXISTS idx_sessao_user     ON sessoes(usuario_id);",
        "CREATE INDEX IF NOT EXISTS idx_folha_colab     ON folhas_pagamento(colaborador_id);",
        "CREATE INDEX IF NOT EXISTS idx_folha_comp      ON folhas_pagamento(competencia);",
        "CREATE INDEX IF NOT EXISTS idx_folha_situacao  ON folhas_pagamento(situacao);",
        "CREATE INDEX IF NOT EXISTS idx_folha_itens_folha ON folha_itens(folha_id);",
        "CREATE INDEX IF NOT EXISTS idx_folha_hist_folha  ON folha_historico(folha_id);",
    ]
    for idx_sql in indices:
        try:
            cursor.execute(idx_sql)
        except Exception:
            pass

    # Provisiona parâmetro padrão de cálculo caso não exista
    try:
        p_mark = "%s" if pg else "?"
        cursor.execute(f"SELECT COUNT(*) FROM folha_parametros WHERE codigo = {p_mark};", ("PADRAO_CLT_2026",))
        qtd = cursor.fetchone()[0]
        if qtd == 0:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"""
                INSERT INTO folha_parametros (
                    codigo, descricao, vigencia_inicio, vigencia_fim,
                    horas_mensais_padrao, dias_mes_padrao, percentual_he_padrao,
                    percentual_he_extra, percentual_adicional_noturno, aplicar_reducao_noturna,
                    fator_reducao_noturna, aplicar_inss, aplicar_irrf, aliquota_fgts,
                    teto_inss, deducao_dependente_irrf, ativo, validado_por_profissional,
                    criado_em, atualizado_em
                ) VALUES ({p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark}, {p_mark});
            """, (
                "PADRAO_CLT_2026", "Parâmetros Gerais CLT 220h / Vigência 2026 (Padrão)",
                "2026-01-01", None,
                220.0, 30, 50.0, 100.0, 20.0, 0, 1.142857,
                1, 1, 8.0, 8157.41, 189.59, 1, 1,
                agora, agora
            ))
    except Exception:
        pass

    conn.commit()
    conn.close()

    if auto_provision:
        try:
            from .auth import AuthService
        except ImportError:
            import sys
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            from backend.auth import AuthService
        auth_service = AuthService(db_path=db_path, auto_init=False)
        auth_service.provisionar_usuario_inicial()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de cursor — abstraem as diferencas entre psycopg2 e sqlite3
# ─────────────────────────────────────────────────────────────────────────────

def row_to_dict(cursor, row, db_path: str = None) -> dict:
    """Converte uma linha em dicionario independente do driver."""
    if _usar_postgres(db_path):
        cols = [desc[0] for desc in cursor.description]
        return dict(zip(cols, row))
    return dict(row)  # SQLite row_factory=sqlite3.Row


def fetchone_dict(cursor, db_path: str = None):
    row = cursor.fetchone()
    if row is None:
        return None
    return row_to_dict(cursor, row, db_path)


def fetchall_dict(cursor, db_path: str = None) -> list:
    return [row_to_dict(cursor, r, db_path) for r in cursor.fetchall()]


def insert_returning_id(
    cursor, conn, sql_pg: str, sql_sqlite: str,
    params: tuple, db_path: str = None
) -> int:
    """
    Executa um INSERT e retorna o id gerado.
    PostgreSQL: usa RETURNING id. SQLite: usa lastrowid.
    """
    if _usar_postgres(db_path):
        cursor.execute(sql_pg, params)
        return cursor.fetchone()[0]
    cursor.execute(sql_sqlite, params)
    return cursor.lastrowid


def ph(db_path: str = None) -> str:
    """Retorna o placeholder correto para o banco ativo: %s (PG) ou ? (SQLite)."""
    return "%s" if _usar_postgres(db_path) else "?"


if __name__ == "__main__":
    init_db()
    modo = "PostgreSQL" if _usar_postgres() else "SQLite"
    print(f"Banco de dados ({modo}) inicializado com sucesso!")
