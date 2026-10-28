"""
Handler Vercel Serverless — POST /api/auth/login
Autentica o usuario e cria uma sessao segura.
"""
import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Carrega .env local se existir (nao tem efeito em producao)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

from http.server import BaseHTTPRequestHandler

from backend.auth import AuthService, CredenciaisInvalidasException

_auth_service = None

def _get_auth():
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


class handler(BaseHTTPRequestHandler):

    def _enviar_json(self, status: int, dados: dict, set_cookie: str = None, delete_cookie: str = None):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        origem = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origem)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        if set_cookie:
            proto = self.headers.get("X-Forwarded-Proto", "")
            secure_flag = "; Secure" if proto == "https" else ""
            self.send_header("Set-Cookie", f"{set_cookie}; Path=/; HttpOnly; SameSite=Lax{secure_flag}")
        if delete_cookie:
            self.send_header("Set-Cookie", f"{delete_cookie}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(corpo)

    def do_OPTIONS(self):
        self.send_response(204)
        origem = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origem)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        try:
            cl = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(cl).decode("utf-8") if cl > 0 else "{}"
            dados = json.loads(raw) if raw.strip() else {}
        except Exception:
            return self._enviar_json(400, {"sucesso": False, "mensagem": "JSON invalido."})

        identificador = (dados.get("identificador") or "").strip()
        senha = dados.get("senha") or ""

        if not identificador or not senha:
            return self._enviar_json(400, {
                "sucesso": False,
                "mensagem": "Preencha o identificador (e-mail ou usuario) e a senha."
            })

        try:
            usuario, token = _get_auth().autenticar(identificador, senha)
            return self._enviar_json(200, {
                "sucesso": True,
                "mensagem": "Autenticacao realizada com sucesso.",
                "token": token,
                "usuario": usuario,
            }, set_cookie=f"session_token={token}")
        except CredenciaisInvalidasException as e:
            return self._enviar_json(401, {"sucesso": False, "mensagem": str(e)})
        except Exception as e:
            return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})
