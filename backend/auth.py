"""
Módulo de Autenticação e Segurança — Backend RH/DP
Implementa hashing seguro com salt (PBKDF2-HMAC-SHA256),
gerenciamento de sessões criptográficas duráveis e controle de acesso por perfil.
Atende a RF-40, RF-41, RF-43 e RNF-01, RNF-02, RNF-03.
"""
import hashlib
import hmac
import secrets
import os
from datetime import datetime, timedelta
from .database import get_connection, init_db

ITERATIONS = 100_000
SESSION_DURATION_HOURS = 12

class CredenciaisInvalidasException(Exception):
    pass

class SessaoInvalidaException(Exception):
    pass

def hash_senha(senha: str, salt: str = None) -> tuple[str, str]:
    """
    Gera o hash PBKDF2-HMAC-SHA256 de uma senha com salt criptográfico aleatório.
    Retorna (hash_hex, salt_hex).
    """
    if not salt:
        salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        senha.encode('utf-8'),
        salt.encode('utf-8'),
        ITERATIONS
    )
    return hash_bytes.hex(), salt

def verificar_senha(senha: str, senha_hash: str, salt: str) -> bool:
    """Verifica se a senha informada corresponde ao hash utilizando comparação constante."""
    hash_calculado, _ = hash_senha(senha, salt)
    return hmac.compare_digest(hash_calculado, senha_hash)

class AuthService:
    def __init__(self, db_path: str = None, auto_init: bool = True):
        self.db_path = db_path
        if auto_init:
            init_db(self.db_path, auto_provision=False)
            self.provisionar_usuario_inicial()

    def provisionar_usuario_inicial(self) -> dict:
        """
        Provisiona com segurança a conta de administrador inicial de demonstração,
        caso ainda não exista nenhum usuário cadastrado no banco de dados.
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios;")
        total = cursor.fetchone()["total"]
        
        if total == 0:
            senha_inicial = os.environ.get("ADMIN_INITIAL_PASSWORD", "Admin@RH2026!")
            salt = secrets.token_hex(16)
            senha_hash, _ = hash_senha(senha_inicial, salt)
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO usuarios (
                    email, usuario, nome_completo, senha_hash, salt, perfil, status, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, 'ativo', ?)
            """, (
                "admin.dp@empresa.com.br",
                "admin.dp",
                "Administrador (RH/DP)",
                senha_hash,
                salt,
                "administrador",
                agora
            ))
            conn.commit()
            cursor.execute("SELECT id, email, usuario, nome_completo, perfil, status FROM usuarios WHERE id = 1;")
            user = dict(cursor.fetchone())
            conn.close()
            return user

        conn.close()
        return {}

    def autenticar(self, identificador: str, senha: str) -> tuple[dict, str]:
        """
        Valida as credenciais contra o banco de dados.
        Se válidas, cria uma sessão e retorna (dados_usuario_sem_senha, token).
        Mensagem de erro genérica para evitar enumeração de usuários.
        """
        if not identificador or not senha:
            raise CredenciaisInvalidasException("Identificador e senha são obrigatórios.")

        identificador = identificador.strip().lower()

        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, email, usuario, nome_completo, senha_hash, salt, perfil, status
            FROM usuarios
            WHERE LOWER(email) = ? OR LOWER(usuario) = ?
        """, (identificador, identificador))
        
        linha = cursor.fetchone()

        if not linha:
            conn.close()
            # Mensagem uniforme para não revelar se o usuário existe
            raise CredenciaisInvalidasException("Identificador ou senha incorretos.")

        usuario = dict(linha)

        if usuario["status"] != "ativo":
            conn.close()
            raise CredenciaisInvalidasException("Conta inativa. Procure o responsável pela administração das contas.")

        if not verificar_senha(senha, usuario["senha_hash"], usuario["salt"]):
            conn.close()
            raise CredenciaisInvalidasException("Identificador ou senha incorretos.")

        # Criar sessão segura
        token = secrets.token_hex(32)
        agora_dt = datetime.now()
        expira_dt = agora_dt + timedelta(hours=SESSION_DURATION_HOURS)
        agora_str = agora_dt.strftime("%Y-%m-%d %H:%M:%S")
        expira_str = expira_dt.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO sessoes (token, usuario_id, criado_em, expira_em, revogado)
            VALUES (?, ?, ?, ?, 0);
        """, (token, usuario["id"], agora_str, expira_str))

        cursor.execute("""
            UPDATE usuarios SET ultimo_login = ? WHERE id = ?;
        """, (agora_str, usuario["id"]))

        conn.commit()
        conn.close()

        dados_usuario = {
            "id": usuario["id"],
            "email": usuario["email"],
            "usuario": usuario["usuario"],
            "nome_completo": usuario["nome_completo"],
            "perfil": usuario["perfil"]
        }

        return dados_usuario, token

    def validar_sessao(self, token: str) -> dict | None:
        """
        Valida se o token de sessão existe, não está expirado e não foi revogado.
        Retorna os dados do usuário autenticado ou None se inválido.
        """
        if not token:
            return None

        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            SELECT s.token, s.expira_em, s.revogado,
                   u.id, u.email, u.usuario, u.nome_completo, u.perfil, u.status
            FROM sessoes s
            JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.token = ? AND s.revogado = 0 AND s.expira_em > ? AND u.status = 'ativo';
        """, (token, agora_str))

        linha = cursor.fetchone()
        conn.close()

        if not linha:
            return None

        return {
            "id": linha["id"],
            "email": linha["email"],
            "usuario": linha["usuario"],
            "nome_completo": linha["nome_completo"],
            "perfil": linha["perfil"]
        }

    def encerrar_sessao(self, token: str) -> bool:
        """Invalida a sessão ativa (logout). Impede o reaproveitamento do token."""
        if not token:
            return False

        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sessoes SET revogado = 1 WHERE token = ?;
        """, (token,))
        
        alterados = cursor.rowcount
        conn.commit()
        conn.close()
        return alterados > 0
