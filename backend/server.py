"""
Servidor HTTP REST e Servidor de Arquivos Estáticos — Backend
Atende aos requisitos de arquitetura desacoplada (GTI) e persistência.
Executa de forma autônoma sem dependências externas (biblioteca padrão Python).
"""
import http.server
import socketserver
import json
import os
import urllib.parse
from .service import ColaboradorService, ValidacaoException, RecursoNaoEncontradoException

PORT = 8000
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

class ApiColaboradorHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    @property
    def service(self) -> ColaboradorService:
        if not hasattr(self.server, "colab_service"):
            self.server.colab_service = ColaboradorService()
        return self.server.colab_service

    def _enviar_json(self, status_code: int, dados: dict | list):
        """Envia resposta JSON com headers apropriados."""
        corpo = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(corpo)

    def do_OPTIONS(self):
        """Suporte a pre-flight CORS."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _ler_json_body(self) -> dict:
        """Lê e desserializa o corpo da requisição JSON."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Corpo da requisição não é um JSON válido.")

    def do_GET(self):
        """Trata requisições GET para API e para arquivos estáticos."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Rota: Listar colaboradores GET /api/colaboradores
        if path == "/api/colaboradores":
            termo = query.get("q", [None])[0]
            situacao = query.get("situacao", [None])[0]
            setor = query.get("setor", [None])[0]
            colabs = self.service.listar(termo=termo, situacao=situacao, setor=setor)
            return self._enviar_json(200, {"sucesso": True, "total": len(colabs), "dados": colabs})

        # Rota: Obter colaborador GET /api/colaboradores/<id>
        if path.startswith("/api/colaboradores/"):
            partes = path.strip("/").split("/")
            if len(partes) == 3 and partes[2].isdigit():
                colab_id = int(partes[2])
                try:
                    colab = self.service.obter_por_id(colab_id)
                    return self._enviar_json(200, {"sucesso": True, "dados": colab})
                except RecursoNaoEncontradoException as e:
                    return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})

        # Servir Frontend estático (index.html, styles.css, app.js)
        return super().do_GET()

    def do_POST(self):
        """Trata criação de colaborador POST /api/colaboradores."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/colaboradores":
            try:
                dados = self._ler_json_body()
                novo = self.service.cadastrar(dados)
                return self._enviar_json(201, {
                    "sucesso": True,
                    "mensagem": "Colaborador cadastrado com sucesso!",
                    "dados": novo
                })
            except ValidacaoException as e:
                return self._enviar_json(400, {
                    "sucesso": False,
                    "mensagem": "Existem inconsistências nos dados informados.",
                    "erros": e.erros
                })
            except ValueError as e:
                return self._enviar_json(400, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": "Rota não encontrada."})

    def do_PUT(self):
        """Trata atualização completa PUT /api/colaboradores/<id>."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        partes = path.strip("/").split("/")

        if len(partes) == 3 and partes[1] == "colaboradores" and partes[2].isdigit():
            colab_id = int(partes[2])
            try:
                dados = self._ler_json_body()
                atualizado = self.service.atualizar(colab_id, dados)
                return self._enviar_json(200, {
                    "sucesso": True,
                    "mensagem": "Colaborador atualizado com sucesso!",
                    "dados": atualizado
                })
            except ValidacaoException as e:
                return self._enviar_json(400, {
                    "sucesso": False,
                    "mensagem": "Existem inconsistências nos dados informados.",
                    "erros": e.erros
                })
            except RecursoNaoEncontradoException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": "Rota não encontrada."})

    def do_PATCH(self):
        """Trata inativação e reativação: PATCH /api/colaboradores/<id>/inativar ou /reativar."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        partes = path.strip("/").split("/")

        if len(partes) == 4 and partes[1] == "colaboradores" and partes[2].isdigit():
            colab_id = int(partes[2])
            acao = partes[3]

            try:
                corpo = self._ler_json_body()
                if acao == "inativar":
                    motivo = corpo.get("motivo", "")
                    usuario = corpo.get("usuario", "Sistema/Administrador")
                    res = self.service.inativar(colab_id, motivo=motivo, usuario=usuario)
                    return self._enviar_json(200, {
                        "sucesso": True,
                        "mensagem": "Colaborador inativado com sucesso. Histórico preservado.",
                        "dados": res
                    })
                elif acao == "reativar":
                    usuario = corpo.get("usuario", "Sistema/Administrador")
                    res = self.service.reativar(colab_id, usuario=usuario)
                    return self._enviar_json(200, {
                        "sucesso": True,
                        "mensagem": "Colaborador reativado com sucesso.",
                        "dados": res
                    })
            except RecursoNaoEncontradoException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": "Rota não encontrada."})

def run_server(port: int = PORT, db_path: str = None):
    """Inicia o servidor HTTP."""
    server_address = ("", port)
    httpd = socketserver.TCPServer(server_address, ApiColaboradorHandler)
    httpd.colab_service = ColaboradorService(db_path=db_path)
    print(f"Servidor rodando em http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()
