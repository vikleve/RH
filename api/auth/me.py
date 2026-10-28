"""
Handler Vercel Serverless — GET /api/auth/me
Valida o token de sessao e retorna os dados do usuario autenticado.
"""
import http.cookies
import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

from http.server import BaseHTTPRequestHandler

from backend.auth import AuthService

_auth_service = None

def _get_auth():
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


class handler(BaseHTTPRequestHandler):

    def _enviar_json(self, status: int, dados: dict):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        origem = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origem)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(corpo)

    def _extrair_token(self) -> str:
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            t = auth_header[7:].strip()
            if t:
                return t
        cookie_header = self.headers.get("Cookie", "")
        if cookie_header:
            try:
                cookies = http.cookies.SimpleCookie()
                cookies.load(cookie_header)
                if "session_token" in cookies:
                    return cookies["session_token"].value
            except Exception:
                pass
        return None

    def do_OPTIONS(self):
        self.send_response(204)
        origem = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origem)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        token = self._extrair_token()
        if not token:
            return self._enviar_json(401, {
                "sucesso": False,
                "mensagem": "Nao autenticado.",
                "codigo": "NAO_AUTENTICADO"
            })
        try:
            usuario = _get_auth().validar_sessao(token)
        except Exception as e:
            return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        if not usuario:
            return self._enviar_json(401, {
                "sucesso": False,
                "mensagem": "Sessao invalida ou expirada.",
                "codigo": "NAO_AUTENTICADO"
            })

        return self._enviar_json(200, {"sucesso": True, "usuario": usuario})
