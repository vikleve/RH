"""
Modulo de Autenticacao e Seguranca — Backend RH/DP
Implementa hashing seguro com salt (PBKDF2-HMAC-SHA256),
gerenciamento de sessoes criptograficas duraveis e controle de acesso por perfil.
Atende a RF-40, RF-41, RF-43 e RNF-01, RNF-02, RNF-03.
Funciona com PostgreSQL (producao) e SQLite (desenvolvimento local e testes).
"""
import hashlib
import hmac
import os
import secrets
import sys
from datetime import datetime, timedelta

from .database import _usar_postgres, get_connection, init_db, insert_returning_id, ph, row_to_dict

ITERATIONS = 100_000
SESSION_DURATION_HOURS = 12


class CredenciaisInvalidasException(Exception):
    pass


class SessaoInvalidaException(Exception):
    pass


def hash_senha(senha: str, salt: str = None) -> tuple:
    """
    Gera o hash PBKDF2-HMAC-SHA256 de uma senha com salt criptografico.
    Retorna (hash_hex, salt_hex).
    """
    if not salt:
        salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    )
    return hash_bytes.hex(), salt


def verificar_senha(senha: str, senha_hash: str, salt: str) -> bool:
    """Verifica se a senha corresponde ao hash usando comparacao constante."""
    hash_calculado, _ = hash_senha(senha, salt)
    return hmac.compare_digest(hash_calculado, senha_hash)


class AuthService:
    def __init__(self, db_path: str = None, auto_init: bool = True):
        self.db_path = db_path
        if auto_init:
            init_db(db_path=self.db_path, auto_provision=False)
            self.provisionar_usuario_inicial()

    # ──────────────────────────────────────────────────────────
    # Shortcuts que carregam db_path automaticamente
    # ──────────────────────────────────────────────────────────

    def _ph(self) -> str:
        return ph(self.db_path)

    def _pg(self) -> bool:
        return _usar_postgres(self.db_path)

    def _conn(self):
        return get_connection(self.db_path)

    def _row(self, cursor, row) -> dict:
        return row_to_dict(cursor, row, self.db_path)

    # ──────────────────────────────────────────────────────────
    # Provisionamento Seguro (GOV-002-02)
    # ──────────────────────────────────────────────────────────

    def provisionar_usuario_inicial(self) -> dict:
        """
        Provisiona as contas padrão de administrador e visitante/convidado
        caso ainda não existam no banco de dados.
        Exige ADMIN_INITIAL_PASSWORD explícita para prevenir senhas padrão em produção.
        """
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        # 1. Provisionar Administrador se não existir
        cursor.execute(f"SELECT id, email, usuario, nome_completo, perfil, status FROM usuarios WHERE email = {P} OR usuario = {P}", ("admin.dp@empresa.com.br", "admin.dp"))
        admin_existente = cursor.fetchone()

        # Determinar se a execução ocorre em contexto de testes automatizados
        em_ambiente_teste = os.environ.get("TESTING") == "1" or (
            "unittest" in sys.modules and os.environ.get("TESTING") != "0"
        )

        if not admin_existente:
            senha_inicial = os.environ.get("ADMIN_INITIAL_PASSWORD")
            if not senha_inicial:
                # Permitir credencial sintética apenas em ambiente explícito de testes automatizados
                if em_ambiente_teste:
                    senha_inicial = os.environ.get("TEST_ADMIN_PASSWORD", "Sintetico#AdminTest2026!")
                else:
                    conn.close()
                    raise RuntimeError(
                        "Falha de segurança operacional: A variável de ambiente ADMIN_INITIAL_PASSWORD "
                        "não foi configurada. É obrigatório definir uma senha inicial forte no arquivo .env "
                        "ou nas variáveis de ambiente antes da inicialização do Portal DP & RH em ambientes reais ou compartilhados."
                    )

            salt = secrets.token_hex(16)
            senha_hash, _ = hash_senha(senha_inicial, salt)
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            params = (
                "admin.dp@empresa.com.br",
                "admin.dp",
                "Administrador (RH/DP)",
                senha_hash,
                salt,
                "administrador",
                agora,
            )

            sql_pg = """
                INSERT INTO usuarios (
                    email, usuario, nome_completo,
                    senha_hash, salt, perfil, status, criado_em
                ) VALUES (%s,%s,%s,%s,%s,%s,'ativo',%s)
                RETURNING id, email, usuario, nome_completo, perfil, status
            """
            sql_sqlite = """
                INSERT INTO usuarios (
                    email, usuario, nome_completo,
                    senha_hash, salt, perfil, status, criado_em
                ) VALUES (?,?,?,?,?,?,'ativo',?)
            """

            insert_returning_id(cursor, conn, sql_pg, sql_sqlite, params, self.db_path)
            conn.commit()

        # 2. Provisionar Convidado / Visitante se não existir e se configurado
        cursor.execute(f"SELECT id, email, usuario, nome_completo, perfil, status FROM usuarios WHERE email = {P} OR usuario = {P}", ("visitante@empresa.com.br", "visitante"))
        convidado_existente = cursor.fetchone()

        if not convidado_existente:
            senha_convidado = os.environ.get("GUEST_INITIAL_PASSWORD")
            if not senha_convidado and em_ambiente_teste:
                senha_convidado = os.environ.get("TEST_GUEST_PASSWORD", "Sintetico#GuestTest2026!")

            if senha_convidado:
                salt = secrets.token_hex(16)
                senha_hash, _ = hash_senha(senha_convidado, salt)
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                params = (
                    "visitante@empresa.com.br",
                    "visitante",
                    "Convidado (Analista RH)",
                    senha_hash,
                    salt,
                    "analista_rh",
                    agora,
                )

                sql_pg = """
                    INSERT INTO usuarios (
                        email, usuario, nome_completo,
                        senha_hash, salt, perfil, status, criado_em
                    ) VALUES (%s,%s,%s,%s,%s,%s,'ativo',%s)
                    RETURNING id, email, usuario, nome_completo, perfil, status
                """
                sql_sqlite = """
                    INSERT INTO usuarios (
                        email, usuario, nome_completo,
                        senha_hash, salt, perfil, status, criado_em
                    ) VALUES (?,?,?,?,?,?,'ativo',?)
                """

                insert_returning_id(cursor, conn, sql_pg, sql_sqlite, params, self.db_path)
                conn.commit()

        cursor.execute(f"SELECT id, email, usuario, nome_completo, perfil, status FROM usuarios WHERE email = {P} OR usuario = {P}", ("admin.dp@empresa.com.br", "admin.dp"))
        row_admin = cursor.fetchone()
        user = self._row(cursor, row_admin) if row_admin else {}
        conn.close()
        return user

    # ──────────────────────────────────────────────────────────
    # Autenticacao
    # ──────────────────────────────────────────────────────────

    def autenticar(self, identificador: str, senha: str) -> tuple:
        """
        Valida as credenciais contra o banco de dados.
        Retorna (dados_usuario_sem_senha, token) se valido.
        Usa mensagem generica para evitar enumeracao de usuarios.
        """
        if not identificador or not senha:
            raise CredenciaisInvalidasException("Identificador e senha sao obrigatorios.")

        identificador = identificador.strip().lower()
        P = self._ph()

        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT id, email, usuario, nome_completo,
                   senha_hash, salt, perfil, status
            FROM usuarios
            WHERE LOWER(email) = {P} OR LOWER(usuario) = {P}
        """, (identificador, identificador))

        row = cursor.fetchone()
        if not row:
            conn.close()
            raise CredenciaisInvalidasException("Identificador ou senha incorretos.")

        usuario = self._row(cursor, row)

        if usuario["status"] != "ativo":
            conn.close()
            raise CredenciaisInvalidasException("Conta inativa. Procure o responsavel pela administracao das contas.")

        if not verificar_senha(senha, usuario["senha_hash"], usuario["salt"]):
            conn.close()
            raise CredenciaisInvalidasException("Identificador ou senha incorretos.")

        token = secrets.token_hex(32)
        agora_dt = datetime.now()
        expira_dt = agora_dt + timedelta(hours=SESSION_DURATION_HOURS)
        agora_str = agora_dt.strftime("%Y-%m-%d %H:%M:%S")
        expira_str = expira_dt.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(f"""
            INSERT INTO sessoes (token, usuario_id, criado_em, expira_em, revogado)
            VALUES ({P},{P},{P},{P},0)
        """, (token, usuario["id"], agora_str, expira_str))

        cursor.execute(f"""
            UPDATE usuarios SET ultimo_login={P} WHERE id={P}
        """, (agora_str, usuario["id"]))

        conn.commit()
        conn.close()

        return {
            "id":            usuario["id"],
            "email":         usuario["email"],
            "usuario":       usuario["usuario"],
            "nome_completo": usuario["nome_completo"],
            "perfil":        usuario["perfil"],
        }, token

    # ──────────────────────────────────────────────────────────
    # Sessoes
    # ──────────────────────────────────────────────────────────

    def validar_sessao(self, token: str):
        """
        Valida se o token existe, nao expirou e nao foi revogado.
        Retorna os dados do usuario autenticado ou None.
        """
        if not token:
            return None

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(f"""
            SELECT u.id, u.email, u.usuario, u.nome_completo, u.perfil
            FROM sessoes s
            JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.token = {P}
              AND s.revogado = 0
              AND s.expira_em > {P}
              AND u.status = 'ativo'
        """, (token, agora_str))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        usuario = self._row(cursor, row)
        conn.close()
        return usuario

    def encerrar_sessao(self, token: str) -> bool:
        """Invalida a sessao ativa (logout)."""
        if not token:
            return False

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE sessoes SET revogado=1 WHERE token={P}", (token,))
        alterados = cursor.rowcount
        conn.commit()
        conn.close()
        return alterados > 0
