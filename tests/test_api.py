"""
Testes de Integração de API HTTP — Módulo 1 & Autenticação
Execução 100% automatizada em código (sem abrir navegador).
Valida contratos de endpoints REST, serialização JSON, proteção por token/cookie e códigos HTTP.
"""
import json
import os
import socketserver
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.auth import AuthService
from backend.server import ApiColaboradorHandler
from backend.service import ColaboradorService


class TestApiColaboradores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "1"
        os.environ["ADMIN_INITIAL_PASSWORD"] = "Sintetico#AdminTest2026!"
        cls.admin_senha = "Sintetico#AdminTest2026!"
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(cls.temp_db_fd)

        cls.server = socketserver.TCPServer(("127.0.0.1", 0), ApiColaboradorHandler)
        cls.server.colab_service = ColaboradorService(db_path=cls.temp_db_path)
        cls.server.auth_service = AuthService(db_path=cls.temp_db_path)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        if os.path.exists(cls.temp_db_path):
            try:
                os.remove(cls.temp_db_path)
            except PermissionError:
                pass

    def _fazer_requisicao(self, metodo: str, caminho: str, payload: dict = None, token: str = None, cookie: str = None):
        """Helper para executar requisições HTTP com ou sem autenticação."""
        url = f"{self.base_url}{caminho}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=metodo)
        req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        if cookie:
            req.add_header("Cookie", cookie)

        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                corpo = json.loads(resp.read().decode("utf-8"))
                cookie_cabecalho = resp.headers.get("Set-Cookie")
                return status, corpo, cookie_cabecalho
        except urllib.error.HTTPError as e:
            corpo = json.loads(e.read().decode("utf-8"))
            cookie_cabecalho = e.headers.get("Set-Cookie")
            return e.code, corpo, cookie_cabecalho

    def test_bloqueio_endpoints_sem_autenticacao(self):
        """CA-LOGIN-02 / CA-LOGIN-06: Visitante sem sessão deve receber 401 e ter acesso negado."""
        # Tentativa de listar
        status, resp, _ = self._fazer_requisicao("GET", "/api/colaboradores")
        self.assertEqual(status, 401)
        self.assertFalse(resp["sucesso"])
        self.assertEqual(resp["codigo"], "NAO_AUTENTICADO")
        self.assertNotIn("dados", resp)

        # Tentativa de criar
        status, resp, _ = self._fazer_requisicao("POST", "/api/colaboradores", {"nome_completo": "Tentativa Invasao"})
        self.assertEqual(status, 401)
        self.assertFalse(resp["sucesso"])

    def test_fluxo_completo_api(self):
        """Testa o fluxo REST completo autenticado: Login -> Criação -> Consulta -> Edição -> Inativação -> Histórico."""
        # 1. Login com credenciais válidas
        status, resp, set_cookie = self._fazer_requisicao("POST", "/api/auth/login", {
            "identificador": "admin.dp@empresa.com.br",
            "senha": "Sintetico#AdminTest2026!"
        })
        self.assertEqual(status, 200)
        self.assertTrue(resp["sucesso"])
        self.assertIn("token", resp)
        self.assertIsNotNone(set_cookie)
        self.assertIn("session_token=", set_cookie)
        token = resp["token"]

        # 2. POST /api/colaboradores com token Bearer
        payload = {
            "matricula": "RH-5001",
            "nome_completo": "Mariana Ramos Ferreira",
            "cpf": "52998224725",
            "rg": "33.444.555-6",
            "data_nascimento": "1992-08-20",
            "telefone": "(11) 97777-8888",
            "email": "mariana.ramos@empresa.com",
            "logradouro": "Rua das Flores",
            "numero": "250",
            "bairro": "Jardins",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01400-000",
            "data_admissao": "2021-05-10",
            "cargo": "Supervisora de DP",
            "setor": "Departamento Pessoal",
            "salario_base": 5900.00,
            "situacao": "ativo",
            "dependentes": [
                {"nome": "Julia Ferreira", "cpf": "", "parentesco": "Filho(a)"}
            ]
        }
        status, resp, _ = self._fazer_requisicao("POST", "/api/colaboradores", payload, token=token)
        self.assertEqual(status, 201)
        self.assertTrue(resp["sucesso"])
        colab_id = resp["dados"]["id"]
        self.assertEqual(resp["dados"]["matricula"], "RH-5001")

        # 3. GET /api/colaboradores - Listagem autenticada
        status, resp, _ = self._fazer_requisicao("GET", "/api/colaboradores", token=token)
        self.assertEqual(status, 200)
        self.assertTrue(resp["total"] >= 1)

        # 4. GET /api/colaboradores?q=Mariana - Pesquisa autenticada
        status, resp, _ = self._fazer_requisicao("GET", "/api/colaboradores?q=Mariana", token=token)
        self.assertEqual(status, 200)
        self.assertEqual(len(resp["dados"]), 1)
        self.assertEqual(resp["dados"][0]["id"], colab_id)

        # 5. PUT /api/colaboradores/<id> - Edição autenticada
        payload_edit = dict(payload)
        payload_edit["cargo"] = "Gerente de Departamento Pessoal"
        payload_edit["salario_base"] = 8200.00
        status, resp, _ = self._fazer_requisicao("PUT", f"/api/colaboradores/{colab_id}", payload_edit, token=token)
        self.assertEqual(status, 200)
        self.assertEqual(resp["dados"]["cargo"], "Gerente de Departamento Pessoal")

        # 6. PATCH /api/colaboradores/<id>/inativar - Inativação lógica autenticada
        status, resp, _ = self._fazer_requisicao("PATCH", f"/api/colaboradores/{colab_id}/inativar", {
            "motivo": "Licença não remunerada"
        }, token=token)
        self.assertEqual(status, 200)
        self.assertEqual(resp["dados"]["situacao"], "inativo")

        # 7. GET /api/colaboradores/<id> - Histórico e auditoria
        status, resp, _ = self._fazer_requisicao("GET", f"/api/colaboradores/{colab_id}", token=token)
        self.assertEqual(status, 200)
        dados_completos = resp["dados"]
        self.assertEqual(dados_completos["situacao"], "inativo")
        self.assertTrue(len(dados_completos["historico"]) >= 3)

        # 8. Validação de Erros 400 (Bad Request) mesmo autenticado
        status, resp, _ = self._fazer_requisicao("POST", "/api/colaboradores", {"nome_completo": "Apenas Nome"}, token=token)
        self.assertEqual(status, 400)
        self.assertFalse(resp["sucesso"])
        self.assertIn("erros", resp)

if __name__ == "__main__":
    unittest.main()
