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
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Configuracao
# ─────────────────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")

_SQLITE_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "colaboradores.db")
)

# ─────────────────────────────────────────────────────────────────────────────
# Deteccao do modo
# ─────────────────────────────────────────────────────────────────────────────

def _usar_postgres(db_path: str = None) -> bool:
    """
    Retorna True se devemos usar PostgreSQL.
    Se db_path for fornecido explicitamente, usa SQLite com esse caminho.
    """
    if db_path:
        return False  # caminho explicito => sempre SQLite (ex: testes isolados)
    return bool(DATABASE_URL and DATABASE_URL.strip())


def _get_pg_conn():
    """Retorna conexao psycopg2 para PostgreSQL."""
    try:
        import psycopg2
    except ImportError:
        raise ImportError(
            "psycopg2-binary nao encontrado. Execute: pip install psycopg2-binary"
        )
    dsn = DATABASE_URL.replace("postgres://", "postgresql://", 1)
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
    Retorna conexao ao banco de dados correto:
      - SQLite no caminho db_path se fornecido (testes isolados / dev especifico)
      - PostgreSQL se DATABASE_URL estiver definida e db_path nao for fornecido
      - SQLite padrao caso contrario
    """
    if _usar_postgres(db_path):
        return _get_pg_conn()
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
    ]
    for idx_sql in indices:
        try:
            cursor.execute(idx_sql)
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
