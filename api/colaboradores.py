"""
Handler Vercel Serverless — /api/colaboradores (e subrecursos)
Gerencia operacoes CRUD de colaboradores com autenticacao obrigatoria.

Rotas atendidas (via vercel.json):
  GET  /api/colaboradores               — listar (com filtros)
  POST /api/colaboradores               — cadastrar
  GET  /api/colaboradores/<id>          — obter por ID
  PUT  /api/colaboradores/<id>          — atualizar
  PATCH /api/colaboradores/<id>/inativar
  PATCH /api/colaboradores/<id>/reativar
"""
import http.cookies
import json
import os
import sys
import urllib.parse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

from http.server import BaseHTTPRequestHandler

from backend.auth import AuthService
from backend.service import ColaboradorService, RecursoNaoEncontradoException, ValidacaoException

_auth_service = None
_colab_service = None


def _get_auth():
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def _get_service():
    global _colab_service
    if _colab_service is None:
        _colab_service = ColaboradorService()
    return _colab_service


class handler(BaseHTTPRequestHandler):

    # ──────────────────────────────────────────────────────────
    # Utilitarios internos
    # ──────────────────────────────────────────────────────────

    def _enviar_json(self, status: int, dados: dict):
        corpo = json.dumps(dados, ensure_ascii=False, default=str).encode("utf-8")
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

    def _exigir_autenticacao(self):
        """Retorna o usuario autenticado ou envia 401 e retorna None."""
        token = self._extrair_token()
        if not token:
            self._enviar_json(401, {
                "sucesso": False,
                "mensagem": "Acesso nao autorizado. Faca login para acessar este recurso.",
                "codigo": "NAO_AUTENTICADO"
            })
            return None
        try:
            usuario = _get_auth().validar_sessao(token)
        except Exception as e:
            self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})
            return None
        if not usuario:
            self._enviar_json(401, {
                "sucesso": False,
                "mensagem": "Sessao invalida ou expirada. Faca login novamente.",
                "codigo": "NAO_AUTENTICADO"
            })
            return None
        return usuario

    def _ler_json_body(self) -> dict:
        cl = int(self.headers.get("Content-Length", 0) or 0)
        if cl == 0:
            return {}
        raw = self.rfile.read(cl).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Corpo da requisicao nao e um JSON valido.")

    def _parse_path(self):
        """Retorna (path_limpo, query_dict)."""
        raw = (
            self.headers.get("x-forwarded-uri") or
            self.headers.get("x-matched-path") or
            self.path
        )
        parsed = urllib.parse.urlparse(raw)
        path = parsed.path.rstrip("/")
        # Remove extensao .py se a Vercel a incluir
        if path.endswith(".py"):
            path = path[:-3]
        query = urllib.parse.parse_qs(parsed.query)
        return path, query

    # ──────────────────────────────────────────────────────────
    # Handlers HTTP
    # ──────────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(204)
        origem = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origem)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        path, query = self._parse_path()
        usuario = self._exigir_autenticacao()
        if not usuario:
            return

        partes = [p for p in path.split("/") if p]
        # /api/colaboradores
        if len(partes) == 2 and partes[1] == "colaboradores":
            termo    = (query.get("q",        [None])[0])
            situacao = (query.get("situacao", [None])[0])
            setor    = (query.get("setor",    [None])[0])
            try:
                colabs = _get_service().listar(termo=termo, situacao=situacao, setor=setor)
                return self._enviar_json(200, {"sucesso": True, "total": len(colabs), "dados": colabs})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": str(e)})

        # /api/colaboradores/<id>
        if len(partes) == 3 and partes[1] == "colaboradores" and partes[2].isdigit():
            try:
                colab = _get_service().obter_por_id(int(partes[2]))
                return self._enviar_json(200, {"sucesso": True, "dados": colab})
            except RecursoNaoEncontradoException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": str(e)})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota nao encontrada: {path}"})

    def do_POST(self):
        path, _ = self._parse_path()
        usuario = self._exigir_autenticacao()
        if not usuario:
            return

        partes = [p for p in path.split("/") if p]
        if len(partes) == 2 and partes[1] == "colaboradores":
            try:
                dados = self._ler_json_body()
                nome_resp = f"{usuario['nome_completo']} ({usuario['perfil']})"
                novo = _get_service().cadastrar(dados, usuario=nome_resp)
                return self._enviar_json(201, {
                    "sucesso": True,
                    "mensagem": "Colaborador cadastrado com sucesso!",
                    "dados": novo
                })
            except ValidacaoException as e:
                return self._enviar_json(400, {
                    "sucesso": False,
                    "mensagem": "Existem inconsistencias nos dados informados.",
                    "erros": e.erros
                })
            except ValueError as e:
                return self._enviar_json(400, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": str(e)})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota nao encontrada: {path}"})

    def do_PUT(self):
        path, _ = self._parse_path()
        usuario = self._exigir_autenticacao()
        if not usuario:
            return

        partes = [p for p in path.split("/") if p]
        if len(partes) == 3 and partes[1] == "colaboradores" and partes[2].isdigit():
            colab_id = int(partes[2])
            try:
                dados = self._ler_json_body()
                nome_resp = f"{usuario['nome_completo']} ({usuario['perfil']})"
                atualizado = _get_service().atualizar(colab_id, dados, usuario=nome_resp)
                return self._enviar_json(200, {
                    "sucesso": True,
                    "mensagem": "Colaborador atualizado com sucesso!",
                    "dados": atualizado
                })
            except ValidacaoException as e:
                return self._enviar_json(400, {
                    "sucesso": False,
                    "mensagem": "Existem inconsistencias nos dados informados.",
                    "erros": e.erros
                })
            except RecursoNaoEncontradoException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": str(e)})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota nao encontrada: {path}"})

    def do_PATCH(self):
        path, _ = self._parse_path()
        usuario = self._exigir_autenticacao()
        if not usuario:
            return

        partes = [p for p in path.split("/") if p]
        # /api/colaboradores/<id>/inativar  ou  /api/colaboradores/<id>/reativar
        if len(partes) == 4 and partes[1] == "colaboradores" and partes[2].isdigit():
            colab_id = int(partes[2])
            acao = partes[3]
            nome_resp = f"{usuario['nome_completo']} ({usuario['perfil']})"
            try:
                corpo = self._ler_json_body()
                if acao == "inativar":
                    motivo = corpo.get("motivo", "")
                    res = _get_service().inativar(colab_id, motivo=motivo, usuario=nome_resp)
                    return self._enviar_json(200, {
                        "sucesso": True,
                        "mensagem": "Colaborador inativado com sucesso. Historico preservado.",
                        "dados": res
                    })
                elif acao == "reativar":
                    res = _get_service().reativar(colab_id, usuario=nome_resp)
                    return self._enviar_json(200, {
                        "sucesso": True,
                        "mensagem": "Colaborador reativado com sucesso.",
                        "dados": res
                    })
                else:
                    return self._enviar_json(400, {"sucesso": False, "mensagem": f"Acao desconhecida: {acao}"})
            except RecursoNaoEncontradoException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": str(e)})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota nao encontrada: {path}"})
