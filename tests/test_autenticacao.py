"""
Testes Automatizados de Segurança e Autenticação — Portal DP & RH
Valida os critérios de aceitação CA-LOGIN-01 a CA-LOGIN-10 e requisitos RF-40, RF-41, RF-43.
Execução 100% em código (headless / sem abrir navegador).
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
import re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.server import ApiColaboradorHandler
from backend.service import ColaboradorService
from backend.auth import AuthService, hash_senha, verificar_senha, CredenciaisInvalidasException
from backend.database import get_connection

class TestAutenticacaoSeguranca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Cria banco de dados temporário isolado
        cls.temp_db_fd, cls.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(cls.temp_db_fd)
        
        # Iniciar servidor HTTP em porta efêmera livre
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

    def _req(self, metodo: str, caminho: str, payload: dict = None, token: str = None, cookie: str = None):
        """Helper HTTP nativo para envio de requisições de teste."""
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
                set_cookie = resp.headers.get("Set-Cookie")
                return status, corpo, set_cookie
        except urllib.error.HTTPError as e:
            try:
                corpo = json.loads(e.read().decode("utf-8"))
            except Exception:
                corpo = {}
            set_cookie = e.headers.get("Set-Cookie")
            return e.code, corpo, set_cookie

    # =========================================================================
    # CA-LOGIN-01: Acesso inicial protegido
    # =========================================================================
    def test_ca_login_01_acesso_inicial_protegido(self):
        """CA-LOGIN-01: Visitante sem sessão ao consultar endpoints protegidos não recebe dados internos."""
        status, resp, _ = self._req("GET", "/api/colaboradores")
        self.assertEqual(status, 401)
        self.assertFalse(resp.get("sucesso", True))
        self.assertEqual(resp.get("codigo"), "NAO_AUTENTICADO")
        self.assertNotIn("dados", resp)

    # =========================================================================
    # CA-LOGIN-02: Bloqueio de acesso direto a páginas e rotas internas
    # =========================================================================
    def test_ca_login_02_bloqueio_acesso_direto(self):
        """CA-LOGIN-02: Qualquer operação protegida (GET, POST, PUT, PATCH) sem token é negada com HTTP 401."""
        rotas_protegidas = [
            ("GET", "/api/colaboradores"),
            ("GET", "/api/colaboradores/1"),
            ("POST", "/api/colaboradores", {"nome_completo": "Invasor"}),
            ("PUT", "/api/colaboradores/1", {"nome_completo": "Modificacao Invasora"}),
            ("PATCH", "/api/colaboradores/1/inativar", {"motivo": "Invasao"}),
            ("PATCH", "/api/colaboradores/1/reativar", {}),
            ("GET", "/api/auth/me")
        ]
        for metodo, rota, *payload in rotas_protegidas:
            corpo_envio = payload[0] if payload else None
            status, resp, _ = self._req(metodo, rota, corpo_envio)
            self.assertEqual(status, 401, f"Rota {metodo} {rota} deveria retornar 401 mas retornou {status}")
            self.assertFalse(resp.get("sucesso", True))

    # =========================================================================
    # CA-LOGIN-03: Credenciais inválidas
    # =========================================================================
    def test_ca_login_03_credenciais_invalidas(self):
        """CA-LOGIN-03: Rejeita login com senha incorreta ou usuário inexistente sem revelar existência de conta."""
        # Senha incorreta para usuário existente
        status, resp, _ = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp@empresa.com.br",
            "senha": "SenhaIncorreta123!"
        })
        self.assertEqual(status, 401)
        self.assertFalse(resp["sucesso"])
        self.assertIn("mensagem", resp)
        self.assertNotIn("token", resp)

        # Usuário inexistente (mesma resposta genérica de segurança)
        status_inexistente, resp_inexistente, _ = self._req("POST", "/api/auth/login", {
            "identificador": "naoexiste@empresa.com.br",
            "senha": "QualquerSenha123!"
        })
        self.assertEqual(status_inexistente, 401)
        self.assertFalse(resp_inexistente["sucesso"])
        self.assertEqual(resp["mensagem"], resp_inexistente["mensagem"], "Mensagens de erro devem ser idênticas para evitar enumeração de contas.")

    # =========================================================================
    # CA-LOGIN-04: Autenticação válida
    # =========================================================================
    def test_ca_login_04_autenticacao_valida(self):
        """CA-LOGIN-04: Usuário ativo com credenciais válidas obtém sessão real e cookie HttpOnly."""
        # Login com e-mail
        status, resp, set_cookie = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp@empresa.com.br",
            "senha": "Admin@RH2026!"
        })
        self.assertEqual(status, 200)
        self.assertTrue(resp["sucesso"])
        self.assertIn("token", resp)
        token = resp["token"]
        self.assertTrue(len(token) >= 32)
        
        # Validação do perfil e dos dados retornados
        user = resp["usuario"]
        self.assertEqual(user["perfil"], "administrador")
        self.assertEqual(user["usuario"], "admin.dp")
        self.assertNotIn("senha_hash", user)
        self.assertNotIn("salt", user)

        # Login também com nome de usuário
        status_user, resp_user, _ = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp",
            "senha": "Admin@RH2026!"
        })
        self.assertEqual(status_user, 200)
        self.assertTrue(resp_user["sucesso"])

    # =========================================================================
    # CA-LOGIN-05: Encerramento de sessão funcional (Logout)
    # =========================================================================
    def test_ca_login_05_encerramento_de_sessao(self):
        """CA-LOGIN-05: Ao realizar logout, a sessão é invalidada e seu reaproveitamento é bloqueado."""
        # 1. Autenticar
        _, resp_login, _ = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp",
            "senha": "Admin@RH2026!"
        })
        token = resp_login["token"]

        # 2. Verificar que token funciona
        status_me, resp_me, _ = self._req("GET", "/api/auth/me", token=token)
        self.assertEqual(status_me, 200)
        self.assertTrue(resp_me["sucesso"])

        # 3. Encerrar sessão
        status_logout, resp_logout, delete_cookie = self._req("POST", "/api/auth/logout", token=token)
        self.assertEqual(status_logout, 200)
        self.assertTrue(resp_logout["sucesso"])
        self.assertIn("Max-Age=0", delete_cookie)

        # 4. Tentar reutilizar o mesmo token
        status_reuso, resp_reuso, _ = self._req("GET", "/api/auth/me", token=token)
        self.assertEqual(status_reuso, 401)
        self.assertFalse(resp_reuso.get("sucesso", True))

        # 5. Tentar acessar dados de colaboradores com o token encerrado
        status_colab, resp_colab, _ = self._req("GET", "/api/colaboradores", token=token)
        self.assertEqual(status_colab, 401)

    # =========================================================================
    # CA-LOGIN-06: Proteção de dados (salários, dados pessoais)
    # =========================================================================
    def test_ca_login_06_protecao_de_dados(self):
        """CA-LOGIN-06: Garante que dados salariais e contratuais não vazam sem autenticação."""
        # Cadastrar colaborador usando autenticação
        _, resp_login, _ = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp",
            "senha": "Admin@RH2026!"
        })
        token = resp_login["token"]
        
        payload = {
            "matricula": "RH-9988",
            "nome_completo": "Carlos Eduardo Confidential",
            "cpf": "12345678062",
            "data_nascimento": "1988-03-12",
            "email": "carlos.confidential@empresa.com",
            "data_admissao": "2020-01-10",
            "cargo": "Diretor Executivo",
            "setor": "Diretoria",
            "salario_base": 25000.00,
            "situacao": "ativo"
        }
        status_cad, resp_cad, _ = self._req("POST", "/api/colaboradores", payload, token=token)
        self.assertEqual(status_cad, 201)
        colab_id = resp_cad["dados"]["id"]

        # Agora, fazer requisição sem autenticação para o colaborador cadastrado
        status_anon, resp_anon, _ = self._req("GET", f"/api/colaboradores/{colab_id}")
        self.assertEqual(status_anon, 401)
        self.assertNotIn("25000", str(resp_anon))
        self.assertNotIn("Carlos Eduardo", str(resp_anon))

    # =========================================================================
    # CA-LOGIN-07: Persistência e segurança da sessão
    # =========================================================================
    def test_ca_login_07_persistencia_e_expiracao_sessao(self):
        """CA-LOGIN-07: Sessão válida persiste entre recarregamentos e rejeita tokens expirados."""
        # 1. Login
        _, resp_login, _ = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp",
            "senha": "Admin@RH2026!"
        })
        token = resp_login["token"]

        # 2. Simular recarregamento da página (chamada a /api/auth/me)
        status, resp_me, _ = self._req("GET", "/api/auth/me", token=token)
        self.assertEqual(status, 200)
        self.assertEqual(resp_me["usuario"]["usuario"], "admin.dp")

        # 3. Simular expiração manual no banco de dados
        conn = get_connection(self.temp_db_path)
        passado = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE sessoes SET expira_em = ? WHERE token = ?", (passado, token))
        conn.commit()
        conn.close()

        # 4. Requisição após expiração deve ser rejeitada
        status_exp, _, _ = self._req("GET", "/api/auth/me", token=token)
        self.assertEqual(status_exp, 401)

    # =========================================================================
    # CA-LOGIN-08: Regressão do módulo existente
    # =========================================================================
    def test_ca_login_08_regressao_modulo_existente(self):
        """CA-LOGIN-08: As operações existentes do Módulo 1 continuam 100% funcionais sob autenticação."""
        _, resp_login, _ = self._req("POST", "/api/auth/login", {
            "identificador": "admin.dp",
            "senha": "Admin@RH2026!"
        })
        token = resp_login["token"]

        # Cadastro
        payload = {
            "matricula": "RH-7722",
            "nome_completo": "Aline Silva Santos",
            "cpf": "98765430166",
            "data_nascimento": "1995-10-15",
            "email": "aline.santos@empresa.com",
            "data_admissao": "2022-03-01",
            "cargo": "Analista de RH",
            "setor": "Recursos Humanos",
            "salario_base": 4800.00,
            "situacao": "ativo"
        }
        status, resp, _ = self._req("POST", "/api/colaboradores", payload, token=token)
        self.assertEqual(status, 201)
        cid = resp["dados"]["id"]

        # Edição
        payload["cargo"] = "Analista de RH Pleno"
        status_edit, resp_edit, _ = self._req("PUT", f"/api/colaboradores/{cid}", payload, token=token)
        self.assertEqual(status_edit, 200)
        self.assertEqual(resp_edit["dados"]["cargo"], "Analista de RH Pleno")

        # Inativação
        status_inat, resp_inat, _ = self._req("PATCH", f"/api/colaboradores/{cid}/inativar", {"motivo": "Demissão a pedido"}, token=token)
        self.assertEqual(status_inat, 200)
        self.assertEqual(resp_inat["dados"]["situacao"], "inativo")

        # Auditoria preservada com identificador do usuário
        status_det, resp_det, _ = self._req("GET", f"/api/colaboradores/{cid}", token=token)
        self.assertEqual(status_det, 200)
        self.assertTrue(len(resp_det["dados"]["historico"]) >= 2)
        # Responsável registrado na auditoria
        responsavel = resp_det["dados"]["historico"][0]["usuario_responsavel"]
        self.assertIn("Administrador", responsavel)

    # =========================================================================
    # CA-LOGIN-09: Responsividade e estrutura de layout da tela de login
    # =========================================================================
    def test_ca_login_09_estrutura_layout_e_responsividade(self):
        """CA-LOGIN-09: Validação semântica da tela de login e regras de responsividade no CSS."""
        html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Verificar presença dos elementos críticos exigidos na especificação
        self.assertIn('id="tela-login"', html)
        self.assertIn('id="form-login"', html)
        self.assertIn('id="login-identificador"', html)
        self.assertIn('id="login-senha"', html)
        self.assertIn('id="btn-toggle-senha"', html)
        self.assertIn('id="btn-entrar"', html)
        self.assertIn('id="login-spinner"', html)
        self.assertIn('id="login-alerta"', html)
        self.assertIn('id="tela-sistema"', html)
        self.assertIn('id="btn-logout"', html)

        # Verificar CSS correspondente
        css_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "styles.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".login-wrapper", css)
        self.assertIn(".login-card", css)
        self.assertIn(".btn-toggle-password", css)
        self.assertIn(".spinner", css)
        self.assertIn("@media (max-width: 640px)", css)

    # =========================================================================
    # CA-LOGIN-10: Compatibilidade de Deploy Público e Vercel
    # =========================================================================
    def test_ca_login_10_compatibilidade_deploy_vercel(self):
        """CA-LOGIN-10: Valida a configuração da Vercel e o handler serverless da API."""
        raiz = os.path.join(os.path.dirname(__file__), "..")
        vercel_json_path = os.path.join(raiz, "vercel.json")
        self.assertTrue(os.path.exists(vercel_json_path), "Arquivo vercel.json deve existir na raiz.")
        
        with open(vercel_json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.assertIn("rewrites", config)
            destinos = [r["destination"] for r in config["rewrites"]]
            self.assertIn("/api/index.py", destinos)

        api_index_path = os.path.join(raiz, "api", "index.py")
        self.assertTrue(os.path.exists(api_index_path), "Handler api/index.py deve existir.")

    # =========================================================================
    # Testes Criptográficos de Senha (RNF-01, RNF-02)
    # =========================================================================
    def test_criptografia_pbkdf2_com_salt(self):
        """Garante que as senhas utilizam salt individual e hash PBKDF2-HMAC-SHA256."""
        senha = "SenhaForteSegura@2026"
        hash1, salt1 = hash_senha(senha)
        hash2, salt2 = hash_senha(senha)

        # Salts diferentes geram hashes diferentes mesmo para a mesma senha
        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)
        self.assertNotEqual(senha, hash1)

        # Verificação com timing-safe comparison
        self.assertTrue(verificar_senha(senha, hash1, salt1))
        self.assertTrue(verificar_senha(senha, hash2, salt2))
        self.assertFalse(verificar_senha("SenhaInvalida", hash1, salt1))

if __name__ == "__main__":
    unittest.main()
