"""
Servidor HTTP REST e Servidor de Arquivos Estáticos — Backend RH/DP
Atende aos requisitos de autenticação real (RF-40, RF-41, RF-43, RNF-01 a RNF-03),
persistência durável e controle de acesso a endpoints protegidos.
Executa de forma autônoma (localmente) e como Handler Serverless (Vercel).
"""
import http.cookies
import http.server
import json
import os
import socketserver
import urllib.parse

# Carrega variaveis de ambiente do arquivo .env (se existir)
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv nao instalado; variaveis devem ser definidas manualmente
try:
    from .auth import AuthService, CredenciaisInvalidasException
    from .folha_service import (
        FolhaBloqueadaException,
        FolhaNaoEncontradaException,
        FolhaService,
        FolhaValidacaoException,
    )
    from .service import ColaboradorService, RecursoNaoEncontradoException, ValidacaoException
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from backend.auth import AuthService, CredenciaisInvalidasException
    from backend.folha_service import (
        FolhaBloqueadaException,
        FolhaNaoEncontradaException,
        FolhaService,
        FolhaValidacaoException,
    )
    from backend.service import ColaboradorService, RecursoNaoEncontradoException, ValidacaoException

PORT = 8000
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

_global_colab_service = None
_global_auth_service = None
_global_folha_service = None

class ApiColaboradorHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._local_colab_service = None
        self._local_auth_service = None
        self._local_folha_service = None
        # Em ambientes serverless (Vercel), FRONTEND_DIR pode não existir no mesmo diretório local
        dir_to_serve = FRONTEND_DIR if os.path.exists(FRONTEND_DIR) else os.getcwd()
        super().__init__(*args, directory=dir_to_serve, **kwargs)

    @property
    def service(self) -> ColaboradorService:
        """Garante acesso ao ColaboradorService tanto em TCPServer quanto em Serverless Functions."""
        if hasattr(self, "server") and self.server is not None:
            if not hasattr(self.server, "colab_service"):
                self.server.colab_service = ColaboradorService()
            return self.server.colab_service

        if getattr(self, "_local_colab_service", None) is None:
            global _global_colab_service
            if _global_colab_service is None:
                _global_colab_service = ColaboradorService()
            self._local_colab_service = _global_colab_service
        return self._local_colab_service

    @property
    def auth_service(self) -> AuthService:
        """Garante acesso ao AuthService tanto em TCPServer quanto em Serverless Functions."""
        if hasattr(self, "server") and self.server is not None:
            if not hasattr(self.server, "auth_service"):
                db_path = getattr(self.service, "db_path", None)
                self.server.auth_service = AuthService(db_path=db_path)
            return self.server.auth_service

        if getattr(self, "_local_auth_service", None) is None:
            global _global_auth_service
            if _global_auth_service is None:
                db_path = getattr(self.service, "db_path", None)
                _global_auth_service = AuthService(db_path=db_path)
            self._local_auth_service = _global_auth_service
        return self._local_auth_service

    @property
    def folha_service(self) -> FolhaService:
        """Garante acesso ao FolhaService tanto em TCPServer quanto em Serverless Functions."""
        if hasattr(self, "server") and self.server is not None:
            if not hasattr(self.server, "folha_service"):
                db_path = getattr(self.service, "db_path", None)
                self.server.folha_service = FolhaService(db_path=db_path)
            return self.server.folha_service

        if getattr(self, "_local_folha_service", None) is None:
            global _global_folha_service
            if _global_folha_service is None:
                db_path = getattr(self.service, "db_path", None)
                _global_folha_service = FolhaService(db_path=db_path)
            self._local_folha_service = _global_folha_service
        return self._local_folha_service

    def _obter_caminho_e_query(self) -> tuple[str, dict]:
        """
        Extrai o caminho da requisição e os parâmetros de query.
        Suporta ambientes com proxy/rewrites (como Vercel) inspecionando cabeçalhos de rota original.
        """
        raw_uri = (
            self.headers.get("x-forwarded-uri") or
            self.headers.get("x-matched-path") or
            self.headers.get("x-invoke-path") or
            self.path
        )
        parsed = urllib.parse.urlparse(raw_uri)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Se houver parâmetro path na query (injetado por rewrite vercel: ?path=auth/login)
        if "path" in query:
            subpath = query["path"][0]
            path = f"/api/{subpath}" if not subpath.startswith("/") else subpath

        # 2. Remove sufixo .py caso o script seja invocado diretamente pela Vercel (ex: /api/auth/login.py)
        if path.endswith(".py"):
            path = path[:-3]

        # 3. Caso ainda seja /api/index ou /api, verificar route-matches legados
        if path in ("/api/index", "/api"):
            route_matches = self.headers.get("x-now-route-matches", "")
            if "1=" in route_matches:
                subroute = route_matches.split("1=")[-1].split("&")[0]
                path = f"/api/{subroute}"

        return path, query

    def _extrair_token_sessao(self) -> str | None:
        """Extrai o token de autenticação a partir do header Authorization ou Cookie de sessão."""
        # 1. Authorization: Bearer <token>
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            if token:
                return token

        # 2. Cookie: session_token=<token>
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

    def _obter_usuario_autenticado(self) -> dict | None:
        """Retorna os dados do usuário autenticado a partir do token de sessão."""
        token = self._extrair_token_sessao()
        if not token:
            return None
        return self.auth_service.validar_sessao(token)

    def _exigir_autenticacao(self) -> dict | None:
        """
        Verifica se a requisição possui autenticação válida.
        Caso contrário, envia imediatamente resposta HTTP 401 Unauthorized e retorna None.
        """
        usuario = self._obter_usuario_autenticado()
        if not usuario:
            self._enviar_json(401, {
                "sucesso": False,
                "mensagem": "Acesso não autorizado. É necessário efetuar login para acessar este recurso.",
                "codigo": "NAO_AUTENTICADO"
            })
            return None
        return usuario

    def _enviar_json(self, status_code: int, dados: dict | list, set_cookie: str = None, delete_cookie: str = None):
        """Envia resposta JSON com cabeçalhos de segurança e suporte a cookies HttpOnly."""
        corpo = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
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
        """Suporte a pre-flight CORS com credenciais."""
        self.send_response(204)
        origem = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origem)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _ler_json_body(self) -> dict:
        """Lê e desserializa o corpo da requisição JSON."""
        cl = self.headers.get("Content-Length") or self.headers.get("content-length") or 0
        content_length = int(cl)
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Corpo da requisição não é um JSON válido.")

    def do_GET(self):
        """Trata requisições GET para API e para arquivos estáticos."""
        path, query = self._obter_caminho_e_query()

        # Rota de verificação de sessão: GET /api/auth/me
        if path == "/api/auth/me":
            usuario = self._exigir_autenticacao()
            if not usuario:
                return
            return self._enviar_json(200, {
                "sucesso": True,
                "usuario": usuario
            })

        # Rota protegida: Listar colaboradores GET /api/colaboradores
        if path == "/api/colaboradores":
            usuario = self._exigir_autenticacao()
            if not usuario:
                return
            termo = query.get("q", [None])[0]
            situacao = query.get("situacao", [None])[0]
            setor = query.get("setor", [None])[0]
            colabs = self.service.listar(termo=termo, situacao=situacao, setor=setor)
            return self._enviar_json(200, {"sucesso": True, "total": len(colabs), "dados": colabs})

        # Rota protegida: Obter colaborador GET /api/colaboradores/<id>
        if path.startswith("/api/colaboradores/"):
            partes = path.strip("/").split("/")
            if len(partes) == 3 and partes[2].isdigit():
                usuario = self._exigir_autenticacao()
                if not usuario:
                    return
                colab_id = int(partes[2])
                try:
                    colab = self.service.obter_por_id(colab_id)
                    return self._enviar_json(200, {"sucesso": True, "dados": colab})
                except RecursoNaoEncontradoException as e:
                    return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})

        # Rota protegida: Parâmetros de cálculo GET /api/folha/parametros
        if path == "/api/folha/parametros":
            usuario = self._exigir_autenticacao()
            if not usuario:
                return
            param = self.folha_service.obter_parametro_vigente()
            return self._enviar_json(200, {"sucesso": True, "dados": param})

        # Rota protegida: Colaboradores elegíveis para folha GET /api/folha/colaboradores
        if path == "/api/folha/colaboradores":
            usuario = self._exigir_autenticacao()
            if not usuario:
                return
            colabs = self.service.listar(situacao="ativo")
            # Adiciona total de dependentes para cálculo facilitado no frontend
            conn = self.service._conn()
            cursor = conn.cursor()
            P = self.service._ph()
            resultado = []
            for c in colabs:
                cursor.execute(f"SELECT COUNT(*) FROM dependentes WHERE colaborador_id = {P}", (c["id"],))
                c["total_dependentes"] = cursor.fetchone()[0]
                resultado.append(c)
            conn.close()
            return self._enviar_json(200, {"sucesso": True, "total": len(resultado), "dados": resultado})

        # Rota protegida: Listar folhas GET /api/folha
        if path == "/api/folha":
            usuario = self._exigir_autenticacao()
            if not usuario:
                return
            comp = query.get("competencia", [None])[0]
            colab_id = query.get("colaborador_id", [None])[0]
            situacao = query.get("situacao", [None])[0]
            setor = query.get("setor", [None])[0]
            termo = query.get("q", [None])[0]

            folhas = self.folha_service.listar_folhas(
                competencia=comp,
                colaborador_id=int(colab_id) if colab_id and colab_id.isdigit() else None,
                situacao=situacao,
                setor=setor,
                termo=termo
            )
            return self._enviar_json(200, {"sucesso": True, "total": len(folhas), "dados": folhas})

        # Rota protegida: Obter folha por ID GET /api/folha/<id>
        if path.startswith("/api/folha/"):
            partes = path.strip("/").split("/")
            if len(partes) == 3 and partes[2].isdigit():
                usuario = self._exigir_autenticacao()
                if not usuario:
                    return
                folha_id = int(partes[2])
                try:
                    folha = self.folha_service.obter_folha_por_id(folha_id)
                    return self._enviar_json(200, {"sucesso": True, "dados": folha})
                except FolhaNaoEncontradaException as e:
                    return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})

        # Servir Frontend estático (index.html, styles.css, app.js) se arquivo existir
        return super().do_GET()

    def do_POST(self):
        """Trata requisições POST para autenticação e criação de colaboradores."""
        path, _ = self._obter_caminho_e_query()

        # Rota pública: Login POST /api/auth/login
        if path == "/api/auth/login":
            try:
                dados = self._ler_json_body()
                identificador = dados.get("identificador", "").strip()
                senha = dados.get("senha", "")

                if not identificador or not senha:
                    return self._enviar_json(400, {
                        "sucesso": False,
                        "mensagem": "Preencha o identificador (e-mail ou usuário) e a senha."
                    })

                usuario, token = self.auth_service.autenticar(identificador, senha)
                return self._enviar_json(200, {
                    "sucesso": True,
                    "mensagem": "Autenticação realizada com sucesso.",
                    "token": token,
                    "usuario": usuario
                }, set_cookie=f"session_token={token}")
            except CredenciaisInvalidasException as e:
                return self._enviar_json(401, {
                    "sucesso": False,
                    "mensagem": str(e)
                })
            except ValueError as e:
                return self._enviar_json(400, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        # Rota protegida: Logout POST /api/auth/logout
        if path == "/api/auth/logout":
            token = self._extrair_token_sessao()
            if token:
                self.auth_service.encerrar_sessao(token)
            return self._enviar_json(200, {
                "sucesso": True,
                "mensagem": "Sessão encerrada com sucesso."
            }, delete_cookie="session_token")

        # Rota protegida: Cadastrar colaborador POST /api/colaboradores
        if path == "/api/colaboradores":
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            try:
                dados = self._ler_json_body()
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"
                novo = self.service.cadastrar(dados, usuario=nome_responsavel)
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

        # Rota protegida: Salvar parâmetros da folha POST /api/folha/parametros
        if path == "/api/folha/parametros":
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            try:
                dados = self._ler_json_body()
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"
                salvo = self.folha_service.salvar_parametros(dados, usuario=nome_responsavel)
                return self._enviar_json(200, {
                    "sucesso": True,
                    "mensagem": "Parâmetros de cálculo da folha atualizados com sucesso!",
                    "dados": salvo
                })
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        # Rota protegida: Criar folha POST /api/folha
        if path == "/api/folha":
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            try:
                dados = self._ler_json_body()
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"

                colab_id = dados.get("colaborador_id")
                competencia = dados.get("competencia", "").strip()
                if not colab_id or not competencia:
                    return self._enviar_json(400, {
                        "sucesso": False,
                        "mensagem": "Informe o colaborador e a competência (AAAA-MM)."
                    })

                folha = self.folha_service.criar_ou_atualizar_folha(
                    colaborador_id=int(colab_id),
                    competencia=competencia,
                    periodo_inicio=dados.get("periodo_inicio", f"{competencia}-01"),
                    periodo_fim=dados.get("periodo_fim", f"{competencia}-30"),
                    data_pagamento=dados.get("data_pagamento"),
                    dias_trabalhados=float(dados.get("dias_trabalhados", 30)),
                    dias_mes=int(dados.get("dias_mes", 30)),
                    horas_divisor=float(dados.get("horas_divisor", 220.0)),
                    eventos=dados.get("eventos", []),
                    observacoes=dados.get("observacoes", ""),
                    usuario=nome_responsavel
                )
                return self._enviar_json(201, {
                    "sucesso": True,
                    "mensagem": "Folha de pagamento gerada e calculada com sucesso!",
                    "dados": folha
                })
            except FolhaValidacaoException as e:
                return self._enviar_json(400, {
                    "sucesso": False,
                    "mensagem": "Inconsistência nos parâmetros da folha.",
                    "erros": e.erros
                })
            except FolhaNaoEncontradaException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except ValueError as e:
                return self._enviar_json(400, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        # Rota protegida: Ações na folha POST /api/folha/<id>/fechar ou /reabrir ou /calcular
        if path.startswith("/api/folha/"):
            partes = path.strip("/").split("/")
            if len(partes) == 4 and partes[1] == "folha" and partes[2].isdigit():
                usuario_auth = self._exigir_autenticacao()
                if not usuario_auth:
                    return
                folha_id = int(partes[2])
                acao = partes[3]
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"

                try:
                    if acao == "fechar":
                        fechada = self.folha_service.fechar_folha(folha_id, usuario=nome_responsavel)
                        return self._enviar_json(200, {
                            "sucesso": True,
                            "mensagem": f"Folha #{folha_id} homologada e fechada com sucesso!",
                            "dados": fechada
                        })
                    elif acao == "reabrir":
                        corpo = self._ler_json_body()
                        motivo = corpo.get("motivo", "")
                        reaberta = self.folha_service.reabrir_folha(folha_id, motivo=motivo, usuario=nome_responsavel)
                        return self._enviar_json(200, {
                            "sucesso": True,
                            "mensagem": f"Folha #{folha_id} reaberta para edição.",
                            "dados": reaberta
                        })
                    elif acao == "calcular":
                        corpo = self._ler_json_body()
                        folha_antiga = self.folha_service.obter_folha_por_id(folha_id)
                        atualizada = self.folha_service.criar_ou_atualizar_folha(
                            colaborador_id=folha_antiga["colaborador_id"],
                            competencia=folha_antiga["competencia"],
                            periodo_inicio=corpo.get("periodo_inicio", folha_antiga["periodo_inicio"]),
                            periodo_fim=corpo.get("periodo_fim", folha_antiga["periodo_fim"]),
                            data_pagamento=corpo.get("data_pagamento", folha_antiga.get("data_pagamento")),
                            dias_trabalhados=float(corpo.get("dias_trabalhados", folha_antiga["dias_trabalhados"])),
                            dias_mes=int(corpo.get("dias_mes", folha_antiga["dias_mes"])),
                            horas_divisor=float(corpo.get("horas_divisor", folha_antiga["horas_mensais_divisor"])),
                            eventos=corpo.get("eventos", []),
                            observacoes=corpo.get("observacoes", folha_antiga.get("observacoes", "")),
                            usuario=nome_responsavel,
                            folha_id_existente=folha_id
                        )
                        return self._enviar_json(200, {
                            "sucesso": True,
                            "mensagem": "Folha recalculada com sucesso!",
                            "dados": atualizada
                        })
                except FolhaBloqueadaException as e:
                    return self._enviar_json(403, {"sucesso": False, "mensagem": str(e)})
                except FolhaValidacaoException as e:
                    return self._enviar_json(400, {"sucesso": False, "mensagem": str(e), "erros": e.erros})
                except FolhaNaoEncontradaException as e:
                    return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
                except Exception as e:
                    return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota não encontrada: {path}"})

    def do_PUT(self):
        """Trata atualização completa PUT /api/colaboradores/<id> ou /api/folha/<id>."""
        path, _ = self._obter_caminho_e_query()
        partes = path.strip("/").split("/")

        if len(partes) == 3 and partes[1] == "colaboradores" and partes[2].isdigit():
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            colab_id = int(partes[2])
            try:
                dados = self._ler_json_body()
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"
                atualizado = self.service.atualizar(colab_id, dados, usuario=nome_responsavel)
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

        if len(partes) == 3 and partes[1] == "folha" and partes[2].isdigit():
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            folha_id = int(partes[2])
            try:
                corpo = self._ler_json_body()
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"
                folha_antiga = self.folha_service.obter_folha_por_id(folha_id)
                atualizada = self.folha_service.criar_ou_atualizar_folha(
                    colaborador_id=folha_antiga["colaborador_id"],
                    competencia=folha_antiga["competencia"],
                    periodo_inicio=corpo.get("periodo_inicio", folha_antiga["periodo_inicio"]),
                    periodo_fim=corpo.get("periodo_fim", folha_antiga["periodo_fim"]),
                    data_pagamento=corpo.get("data_pagamento", folha_antiga.get("data_pagamento")),
                    dias_trabalhados=float(corpo.get("dias_trabalhados", folha_antiga["dias_trabalhados"])),
                    dias_mes=int(corpo.get("dias_mes", folha_antiga["dias_mes"])),
                    horas_divisor=float(corpo.get("horas_divisor", folha_antiga["horas_mensais_divisor"])),
                    eventos=corpo.get("eventos", []),
                    observacoes=corpo.get("observacoes", folha_antiga.get("observacoes", "")),
                    usuario=nome_responsavel,
                    folha_id_existente=folha_id
                )
                return self._enviar_json(200, {
                    "sucesso": True,
                    "mensagem": "Folha de pagamento atualizada com sucesso!",
                    "dados": atualizada
                })
            except FolhaBloqueadaException as e:
                return self._enviar_json(403, {"sucesso": False, "mensagem": str(e)})
            except FolhaValidacaoException as e:
                return self._enviar_json(400, {"sucesso": False, "mensagem": str(e), "erros": e.erros})
            except FolhaNaoEncontradaException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota não encontrada: {path}"})

    def do_DELETE(self):
        """Trata exclusão de folha: DELETE /api/folha/<id>."""
        path, _ = self._obter_caminho_e_query()
        partes = path.strip("/").split("/")

        if len(partes) == 3 and partes[1] == "folha" and partes[2].isdigit():
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            folha_id = int(partes[2])
            nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"
            try:
                self.folha_service.cancelar_folha(folha_id, usuario=nome_responsavel)
                return self._enviar_json(200, {
                    "sucesso": True,
                    "mensagem": f"Folha #{folha_id} cancelada com sucesso."
                })
            except FolhaBloqueadaException as e:
                return self._enviar_json(403, {"sucesso": False, "mensagem": str(e)})
            except FolhaNaoEncontradaException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota não encontrada: {path}"})

    def do_PATCH(self):
        """Trata inativação e reativação: PATCH /api/colaboradores/<id>/inativar ou /reativar."""
        path, _ = self._obter_caminho_e_query()
        partes = path.strip("/").split("/")

        if len(partes) == 4 and partes[1] == "colaboradores" and partes[2].isdigit():
            usuario_auth = self._exigir_autenticacao()
            if not usuario_auth:
                return
            colab_id = int(partes[2])
            acao = partes[3]

            try:
                corpo = self._ler_json_body()
                nome_responsavel = f"{usuario_auth['nome_completo']} ({usuario_auth['perfil']})"
                if acao == "inativar":
                    motivo = corpo.get("motivo", "")
                    res = self.service.inativar(colab_id, motivo=motivo, usuario=nome_responsavel)
                    return self._enviar_json(200, {
                        "sucesso": True,
                        "mensagem": "Colaborador inativado com sucesso. Histórico preservado.",
                        "dados": res
                    })
                elif acao == "reativar":
                    res = self.service.reativar(colab_id, usuario=nome_responsavel)
                    return self._enviar_json(200, {
                        "sucesso": True,
                        "mensagem": "Colaborador reativado com sucesso.",
                        "dados": res
                    })
            except RecursoNaoEncontradoException as e:
                return self._enviar_json(404, {"sucesso": False, "mensagem": str(e)})
            except Exception as e:
                return self._enviar_json(500, {"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

        return self._enviar_json(404, {"sucesso": False, "mensagem": f"Rota não encontrada: {path}"})

def run_server(port: int = PORT, db_path: str = None):
    """Inicia o servidor HTTP."""
    server_address = ("", port)
    httpd = socketserver.TCPServer(server_address, ApiColaboradorHandler)
    httpd.colab_service = ColaboradorService(db_path=db_path)
    httpd.auth_service = AuthService(db_path=db_path)
    httpd.folha_service = FolhaService(db_path=db_path)
    print(f"Servidor rodando em http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()
