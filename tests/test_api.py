"""
Testes de Integração de API HTTP — Módulo 1: Cadastro de Colaboradores
Execução 100% automatizada em código (sem abrir navegador).
Valida contratos de endpoints REST, serialização JSON e códigos HTTP.
"""
import unittest
import threading
import socketserver
import tempfile
import os
import sys
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.server import ApiColaboradorHandler
from backend.service import ColaboradorService

class TestApiColaboradores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Banco temporário isolado
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(cls.temp_db_fd)
        
        # Iniciar servidor em porta efêmera (0 escolhe automaticamente uma porta livre)
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), ApiColaboradorHandler)
        cls.server.colab_service = ColaboradorService(db_path=cls.temp_db_path)
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

    def _fazer_requisicao(self, metodo: str, caminho: str, payload: dict = None):
        """Helper para executar requisições HTTP."""
        url = f"{self.base_url}{caminho}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=metodo)
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                corpo = json.loads(resp.read().decode("utf-8"))
                return status, corpo
        except urllib.error.HTTPError as e:
            corpo = json.loads(e.read().decode("utf-8"))
            return e.code, corpo

    def test_fluxo_completo_api(self):
        """Testa o fluxo REST completo: Criação -> Consulta -> Edição -> Inativação -> Histórico."""
        # 1. POST /api/colaboradores - Cadastro de colaborador
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
        status, resp = self._fazer_requisicao("POST", "/api/colaboradores", payload)
        self.assertEqual(status, 201)
        self.assertTrue(resp["sucesso"])
        colab_id = resp["dados"]["id"]
        self.assertEqual(resp["dados"]["matricula"], "RH-5001")

        # 2. GET /api/colaboradores - Listagem
        status, resp = self._fazer_requisicao("GET", "/api/colaboradores")
        self.assertEqual(status, 200)
        self.assertTrue(resp["total"] >= 1)

        # 3. GET /api/colaboradores?q=Mariana - Pesquisa
        status, resp = self._fazer_requisicao("GET", "/api/colaboradores?q=Mariana")
        self.assertEqual(status, 200)
        self.assertEqual(len(resp["dados"]), 1)
        self.assertEqual(resp["dados"][0]["id"], colab_id)

        # 4. PUT /api/colaboradores/<id> - Edição
        payload_edit = dict(payload)
        payload_edit["cargo"] = "Gerente de Departamento Pessoal"
        payload_edit["salario_base"] = 8200.00
        status, resp = self._fazer_requisicao("PUT", f"/api/colaboradores/{colab_id}", payload_edit)
        self.assertEqual(status, 200)
        self.assertEqual(resp["dados"]["cargo"], "Gerente de Departamento Pessoal")

        # 5. PATCH /api/colaboradores/<id>/inativar - Inativação lógica
        status, resp = self._fazer_requisicao("PATCH", f"/api/colaboradores/{colab_id}/inativar", {
            "motivo": "Licença não remunerada",
            "usuario": "RH Supervisor"
        })
        self.assertEqual(status, 200)
        self.assertEqual(resp["dados"]["situacao"], "inativo")

        # 6. GET /api/colaboradores/<id> - Verificar integridade e histórico
        status, resp = self._fazer_requisicao("GET", f"/api/colaboradores/{colab_id}")
        self.assertEqual(status, 200)
        dados_completos = resp["dados"]
        self.assertEqual(dados_completos["situacao"], "inativo")
        self.assertTrue(len(dados_completos["historico"]) >= 3)

        # 7. Validação de Erros 400 (Bad Request)
        status, resp = self._fazer_requisicao("POST", "/api/colaboradores", {"nome_completo": "Apenas Nome"})
        self.assertEqual(status, 400)
        self.assertFalse(resp["sucesso"])
        self.assertIn("erros", resp)

if __name__ == "__main__":
    unittest.main()
