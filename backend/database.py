"""
Módulo de Banco de Dados — SQLite
Camada de persistência relacional com integridade referencial.
Atende a RF-01 a RF-09, CA-07, CA-08.
"""
import sqlite3
import os
from datetime import datetime

DEFAULT_DB_PATH = "/tmp/colaboradores.db" if os.environ.get("VERCEL") else os.path.join(os.path.dirname(__file__), "..", "colaboradores.db")

def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Retorna uma conexão configurada com o banco SQLite."""
    caminho = db_path or os.environ.get("DB_PATH") or DEFAULT_DB_PATH
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = None, auto_provision: bool = True):
    """Cria as tabelas e índices necessários no banco de dados se não existirem."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Tabela de Colaboradores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            rg TEXT,
            data_nascimento TEXT NOT NULL,
            telefone TEXT,
            email TEXT NOT NULL,
            logradouro TEXT,
            numero TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            cep TEXT,
            data_admissao TEXT NOT NULL,
            cargo TEXT NOT NULL,
            setor TEXT NOT NULL,
            salario_base REAL NOT NULL,
            situacao TEXT NOT NULL DEFAULT 'ativo' CHECK (situacao IN ('ativo', 'inativo')),
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        );
    """)
    
    # 2. Tabela de Dependentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dependentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            cpf TEXT,
            parentesco TEXT NOT NULL,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores (id) ON DELETE CASCADE
        );
    """)
    
    # 3. Tabela de Histórico de Alterações (Auditoria)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_alteracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            campo_alterado TEXT NOT NULL,
            valor_anterior TEXT,
            valor_novo TEXT,
            usuario_responsavel TEXT NOT NULL DEFAULT 'Sistema/Administrador',
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores (id) ON DELETE CASCADE
        );
    """)

    # 4. Tabela de Usuários do Sistema (Autenticação e Perfis — RF-40, RF-41)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            perfil TEXT NOT NULL CHECK (perfil IN ('administrador', 'analista_rh', 'operador_dp')),
            status TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
            criado_em TEXT NOT NULL,
            ultimo_login TEXT
        );
    """)

    # 5. Tabela de Sessões Criptográficas Ativas (RF-43, RNF-01, RNF-02)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            token TEXT PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            criado_em TEXT NOT NULL,
            expira_em TEXT NOT NULL,
            revogado INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        );
    """)
    
    # Índices para pesquisa e performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colab_matricula ON colaboradores(matricula);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colab_cpf ON colaboradores(cpf);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colab_nome ON colaboradores(nome_completo);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colab_situacao ON colaboradores(situacao);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colab_setor ON colaboradores(setor);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_colab ON historico_alteracoes(colaborador_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dep_colab ON dependentes(colaborador_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuarios(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario_login ON usuarios(usuario);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessao_token ON sessoes(token);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessao_user ON sessoes(usuario_id);")
    
    conn.commit()
    conn.close()

    # Provisionar conta padrão de administrador se ainda não existir
    if auto_provision:
        try:
            from .auth import AuthService
        except ImportError:
            import sys
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            from backend.auth import AuthService
        auth_service = AuthService(db_path=db_path, auto_init=False)
        auth_service.provisionar_usuario_inicial()

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")
