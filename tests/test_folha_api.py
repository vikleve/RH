"""
Testes de Integração de API HTTP da Folha de Pagamento
Testa endpoints REST sem dependência de socket de rede (execução 100% in-memory / headless):
- Proteção 401 para requisições não autenticadas
- GET /api/folha/parametros
- GET /api/folha/colaboradores
- POST /api/folha (Criação e cálculo)
- GET /api/folha/<id> (Demonstrativo com itens e memória)
- POST /api/folha/<id>/fechar (Homologação e fechamento)
- POST /api/folha/<id>/reabrir (Reabertura com justificativa)
- DELETE /api/folha/<id> (Cancelamento)
"""
import unittest
import tempfile
import os
import sys
import io
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.server import ApiColaboradorHandler
from backend.service import ColaboradorService
from backend.auth import AuthService
from backend.folha_service import FolhaService


class FakeSocket:
    def __init__(self, data=b""):
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, data):
        self.wfile.write(data)


class MockServer:
    def __init__(self, db_path):
        self.colab_service = ColaboradorService(db_path=db_path)
        self.auth_service = AuthService(db_path=db_path)
        self.folha_service = FolhaService(db_path=db_path)


class TestFolhaApi(unittest.TestCase):

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.server = MockServer(self.temp_db_path)

        # Autentica e gera token
        self.admin_user, self.token = self.server.auth_service.autenticar("admin.dp@empresa.com.br", "Admin@RH2026!")

        # Cadastra colaborador
        self.colaborador = self.server.colab_service.cadastrar({
            "matricula": "RH-2001",
            "nome_completo": "Juliana Silveira",
            "cpf": "52998224725",
            "rg": "12.345.678-0",
            "data_nascimento": "1992-08-20",
            "telefone": "(11) 91234-5678",
            "email": "juliana.silveira@empresa.com.br",
            "data_admissao": "2021-06-01",
            "cargo": "Especialista em Recursos Humanos",
            "setor": "Recursos Humanos",
            "salario_base": 5500.00,
            "situacao": "ativo"
        }, usuario="Admin")

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except PermissionError:
                pass

    def _executar_requisicao(self, metodo: str, caminho: str, payload: dict = None, token: str = None) -> tuple[int, dict]:
        """Executa uma requisição diretamente pelo ApiColaboradorHandler via buffer in-memory."""
        body_bytes = json.dumps(payload).encode("utf-8") if payload is not None else b""
        headers_lines = [
            f"{metodo} {caminho} HTTP/1.1",
            "Host: localhost",
            f"Content-Length: {len(body_bytes)}",
            "Content-Type: application/json"
        ]
        if token:
            headers_lines.append(f"Authorization: Bearer {token}")

        raw_req = "\r\n".join(headers_lines).encode("utf-8") + b"\r\n\r\n" + body_bytes
        sock = FakeSocket(raw_req)

        handler = ApiColaboradorHandler(sock, ("127.0.0.1", 12345), self.server)
        resp_data = sock.wfile.getvalue()

        # Parse status e body
        resp_str = resp_data.decode("utf-8", errors="replace")
        partes = resp_str.split("\r\n\r\n", 1)
        header_part = partes[0]
        body_part = partes[1] if len(partes) > 1 else "{}"

        status_code = int(header_part.split(" ")[1])
        try:
            body_json = json.loads(body_part)
        except Exception:
            body_json = {"raw": body_part}

        return status_code, body_json

    def test_bloqueio_endpoints_sem_token(self):
        """Endpoints da folha exigem autenticação válida (HTTP 401)."""
        status, dados = self._executar_requisicao("GET", "/api/folha/parametros")
        self.assertEqual(status, 401)
        self.assertFalse(dados.get("sucesso", True))

        status_post, _ = self._executar_requisicao("POST", "/api/folha", {"competencia": "2026-10"})
        self.assertEqual(status_post, 401)

    def test_obter_parametros_e_colaboradores(self):
        """GET /api/folha/parametros e GET /api/folha/colaboradores."""
        status_p, param = self._executar_requisicao("GET", "/api/folha/parametros", token=self.token)
        self.assertEqual(status_p, 200)
        self.assertTrue(param["sucesso"])
        self.assertIn("PADRAO_CLT_2026", param["dados"]["codigo"])

        status_c, colabs = self._executar_requisicao("GET", "/api/folha/colaboradores", token=self.token)
        self.assertEqual(status_c, 200)
        self.assertTrue(colabs["sucesso"])
        self.assertGreater(len(colabs["dados"]), 0)

    def test_fluxo_completo_api_folha(self):
        """Fluxo REST: Criar folha -> Consultar -> Fechar -> Reabrir -> Cancelar."""
        # 1. Criar folha
        payload = {
            "colaborador_id": self.colaborador["id"],
            "competencia": "2026-10",
            "periodo_inicio": "2026-10-01",
            "periodo_fim": "2026-10-31",
            "data_pagamento": "2026-11-05",
            "dias_trabalhados": 30,
            "dias_mes": 30,
            "horas_divisor": 220.0,
            "eventos": [
                {"codigo": "HE50", "quantidade": 8, "percentual": 50.0},
                {"codigo": "DESC_ADTO", "descricao": "Adiantamento Quinzenal", "tipo": "desconto", "valor_total": 1500.00}
            ]
        }
        st_criar, res_criar = self._executar_requisicao("POST", "/api/folha", payload, token=self.token)
        self.assertEqual(st_criar, 201)
        self.assertTrue(res_criar["sucesso"])
        folha_id = res_criar["dados"]["id"]

        # 2. Consultar detalhes
        st_get, res_get = self._executar_requisicao("GET", f"/api/folha/{folha_id}", token=self.token)
        self.assertEqual(st_get, 200)
        self.assertEqual(res_get["dados"]["competencia"], "2026-10")
        self.assertTrue(len(res_get["dados"]["itens"]) >= 4)  # Salário base, HE50, Adiantamento, INSS, FGTS

        # 3. Fechar folha
        st_fechar, res_fechar = self._executar_requisicao("POST", f"/api/folha/{folha_id}/fechar", token=self.token)
        self.assertEqual(st_fechar, 200)
        self.assertEqual(res_fechar["dados"]["situacao"], "fechada")

        # 4. Reabrir folha
        st_reabrir, res_reabrir = self._executar_requisicao(
            "POST", f"/api/folha/{folha_id}/reabrir",
            {"motivo": "Reabertura administrativa para ajuste"},
            token=self.token
        )
        self.assertEqual(st_reabrir, 200)
        self.assertEqual(res_reabrir["dados"]["situacao"], "calculada")

        # 5. Cancelar folha
        st_del, res_del = self._executar_requisicao("DELETE", f"/api/folha/{folha_id}", token=self.token)
        self.assertEqual(st_del, 200)
        self.assertTrue(res_del["sucesso"])


if __name__ == "__main__":
    unittest.main()

