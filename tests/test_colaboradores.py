"""
Suíte de Testes Automatizados — Módulo 1: Cadastro de Colaboradores
Executado 100% via código sem necessidade de abrir navegador.
Valida os Critérios de Aceitação CA-01 a CA-10 e Requisitos RF-01 a RF-09.
"""
import os
import sys
import tempfile
import unittest

# Adicionar caminho base ao sys.path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.service import ColaboradorService, ValidacaoException


class TestModuloColaboradores(unittest.TestCase):
    def setUp(self):
        """Cria um banco de dados temporário em arquivo isolado para cada teste."""
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        self.service = ColaboradorService(db_path=self.temp_db_path)

        # Dados padrão válidos para testes
        self.dados_validos = {
            "matricula": "RH-1001",
            "nome_completo": "Ana Clara Santos",
            "cpf": "52998224725",  # CPF matematicamente válido
            "rg": "12.345.678-9",
            "data_nascimento": "1995-04-15",
            "telefone": "(11) 98765-4321",
            "email": "ana.clara@empresa.com.br",
            "logradouro": "Av. Paulista",
            "numero": "1000",
            "bairro": "Bela Vista",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01310-100",
            "data_admissao": "2022-03-01",
            "cargo": "Analista de Recursos Humanos",
            "setor": "Recursos Humanos",
            "salario_base": 4850.50,
            "situacao": "ativo",
            "dependentes": [
                {
                    "nome": "Lucas Santos",
                    "cpf": "",
                    "parentesco": "Filho(a)"
                }
            ]
        }

    def tearDown(self):
        """Remove o banco de dados temporário após o teste."""
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except PermissionError:
                pass

    # =========================================================================
    # CA-01: NOVO CADASTRO
    # =========================================================================
    def test_ca01_novo_cadastro_sucesso(self):
        """CA-01: Cadastro com dados válidos persiste e fica disponível na listagem."""
        criado = self.service.cadastrar(self.dados_validos)

        self.assertIsNotNone(criado.get("id"))
        self.assertEqual(criado["matricula"], "RH-1001")
        self.assertEqual(criado["nome_completo"], "Ana Clara Santos")
        self.assertEqual(criado["situacao"], "ativo")
        self.assertEqual(len(criado["dependentes"]), 1)
        self.assertEqual(criado["dependentes"][0]["nome"], "Lucas Santos")

        # Verificar presença na listagem
        lista = self.service.listar()
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0]["matricula"], "RH-1001")

    # =========================================================================
    # CA-02: VALIDAÇÃO DE DADOS
    # =========================================================================
    def test_ca02_validacao_campos_obrigatorios(self):
        """CA-02: Rejeita cadastro quando campos obrigatórios estão ausentes."""
        dados_vazios = {}
        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(dados_vazios)

        erros = ctx.exception.erros
        self.assertIn("nome_completo", erros)
        self.assertIn("cpf", erros)
        self.assertIn("email", erros)
        self.assertIn("matricula", erros)
        self.assertIn("data_admissao", erros)
        self.assertIn("salario_base", erros)

    def test_ca02_validacao_cpf_invalido(self):
        """CA-02: Rejeita CPFs inválidos ou repetidos (ex: 111.111.111-11)."""
        dados = dict(self.dados_validos)
        dados["cpf"] = "111.111.111-11"
        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(dados)
        self.assertIn("cpf", ctx.exception.erros)

        dados["cpf"] = "123.456.789-00"  # Dígito verificador incorreto
        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(dados)
        self.assertIn("cpf", ctx.exception.erros)

    def test_ca02_validacao_email_invalido(self):
        """CA-02: Rejeita formato de e-mail incorreto."""
        dados = dict(self.dados_validos)
        dados["email"] = "email-sem-arroba.com"
        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(dados)
        self.assertIn("email", ctx.exception.erros)

    def test_ca02_validacao_datas(self):
        """CA-02: Rejeita data de nascimento futura ou admissão anterior ao nascimento."""
        dados = dict(self.dados_validos)
        dados["data_nascimento"] = "2099-01-01"
        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(dados)
        self.assertIn("data_nascimento", ctx.exception.erros)

    def test_ca02_validacao_salario_invalido(self):
        """CA-02: Rejeita salário zero, negativo ou não numérico."""
        dados = dict(self.dados_validos)
        dados["salario_base"] = -50.00
        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(dados)
        self.assertIn("salario_base", ctx.exception.erros)

    # =========================================================================
    # CA-03: DUPLICIDADE DE IDENTIFICADORES
    # =========================================================================
    def test_ca03_bloqueio_duplicidade_cpf(self):
        """CA-03: Impede o cadastro de dois colaboradores com o mesmo CPF."""
        self.service.cadastrar(self.dados_validos)

        segundo = dict(self.dados_validos)
        segundo["matricula"] = "RH-1002"  # Matrícula diferente
        segundo["nome_completo"] = "Outro Colaborador"

        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(segundo)
        self.assertIn("cpf", ctx.exception.erros)

    def test_ca03_bloqueio_duplicidade_matricula(self):
        """CA-03: Impede o cadastro de dois colaboradores com a mesma matrícula."""
        self.service.cadastrar(self.dados_validos)

        segundo = dict(self.dados_validos)
        segundo["cpf"] = "85328103068"  # Outro CPF válido
        segundo["matricula"] = "RH-1001"  # Mesma matrícula

        with self.assertRaises(ValidacaoException) as ctx:
            self.service.cadastrar(segundo)
        self.assertIn("matricula", ctx.exception.erros)

    # =========================================================================
    # CA-04: CONSULTA E PESQUISA
    # =========================================================================
    def test_ca04_pesquisa_por_nome_cpf_matricula(self):
        """CA-04: Localiza colaboradores por nome, CPF e matrícula."""
        self.service.cadastrar(self.dados_validos)

        c2_dados = dict(self.dados_validos)
        c2_dados["matricula"] = "TI-2002"
        c2_dados["nome_completo"] = "Carlos Eduardo Souza"
        c2_dados["cpf"] = "85328103068"
        c2_dados["email"] = "carlos.souza@empresa.com.br"
        c2_dados["cargo"] = "Desenvolvedor"
        c2_dados["setor"] = "Tecnologia da Informação"
        c2 = self.service.cadastrar(c2_dados)

        # Pesquisa por Nome
        res_nome = self.service.listar(termo="Carlos")
        self.assertEqual(len(res_nome), 1)
        self.assertEqual(res_nome[0]["matricula"], "TI-2002")

        # Pesquisa por Matrícula
        res_mat = self.service.listar(termo="RH-1001")
        self.assertEqual(len(res_mat), 1)
        self.assertEqual(res_mat[0]["nome_completo"], "Ana Clara Santos")

        # Pesquisa por CPF limpo ou formatado
        res_cpf = self.service.listar(termo="85328103068")
        self.assertEqual(len(res_cpf), 1)
        self.assertEqual(res_cpf[0]["id"], c2["id"])

    # =========================================================================
    # CA-05: EDIÇÃO DE DADOS
    # =========================================================================
    def test_ca05_edicao_preservando_identificador(self):
        """CA-05: Edita dados de um colaborador sem criar registro duplicado."""
        criado = self.service.cadastrar(self.dados_validos)
        cid = criado["id"]

        dados_atualizados = dict(self.dados_validos)
        dados_atualizados["cargo"] = "Coordenadora de RH"
        dados_atualizados["salario_base"] = 6500.00

        atualizado = self.service.atualizar(cid, dados_atualizados)

        self.assertEqual(atualizado["id"], cid)
        self.assertEqual(atualizado["cargo"], "Coordenadora de RH")
        self.assertEqual(atualizado["salario_base"], 6500.00)

        # Garante que continua existindo apenas 1 registro no banco
        self.assertEqual(len(self.service.listar()), 1)

    # =========================================================================
    # CA-06: HISTÓRICO DE ALTERAÇÕES (AUDITORIA)
    # =========================================================================
    def test_ca06_auditoria_historico_alteracoes(self):
        """CA-06: Registra campo alterado, valor anterior, valor novo e data/hora."""
        criado = self.service.cadastrar(self.dados_validos)
        cid = criado["id"]

        dados_edicao = dict(self.dados_validos)
        dados_edicao["cargo"] = "Especialista em RH"
        dados_edicao["salario_base"] = 7200.00

        self.service.atualizar(cid, dados_edicao, usuario="Admin Teste")

        detalhes = self.service.obter_por_id(cid)
        historico = detalhes["historico"]

        # Deve ter ao menos o registro de criação e os de alteração de cargo e salário
        self.assertTrue(len(historico) >= 3)
        campos_modificados = [h["campo_alterado"] for h in historico]
        self.assertIn("Cargo", campos_modificados)
        self.assertIn("Salário-base", campos_modificados)

        # Verificar se os valores anterior e novo foram registrados
        hist_cargo = next(h for h in historico if h["campo_alterado"] == "Cargo")
        self.assertEqual(hist_cargo["valor_anterior"], "Analista de Recursos Humanos")
        self.assertEqual(hist_cargo["valor_novo"], "Especialista em RH")
        self.assertEqual(hist_cargo["usuario_responsavel"], "Admin Teste")

    # =========================================================================
    # CA-07: INATIVAÇÃO LÓGICA E REATIVAÇÃO
    # =========================================================================
    def test_ca07_inativacao_logica(self):
        """CA-07: Inativa colaborador sem apagar dados nem histórico."""
        criado = self.service.cadastrar(self.dados_validos)
        cid = criado["id"]

        inativado = self.service.inativar(cid, motivo="Desligamento a pedido", usuario="Gerente RH")

        self.assertEqual(inativado["situacao"], "inativo")

        # Continua acessível na consulta de inativos
        inativos = self.service.listar(situacao="inativo")
        self.assertEqual(len(inativos), 1)
        self.assertEqual(inativos[0]["id"], cid)

        # Dados cadastrais e dependentes permanecem intactos
        detalhes = self.service.obter_por_id(cid)
        self.assertEqual(detalhes["nome_completo"], "Ana Clara Santos")
        self.assertEqual(len(detalhes["dependentes"]), 1)

        # Histórico registrou a inativação
        historico = detalhes["historico"]
        hist_inativacao = next(h for h in historico if h["campo_alterado"] == "Situação do Vínculo")
        self.assertEqual(hist_inativacao["valor_anterior"], "ativo")
        self.assertIn("inativo", hist_inativacao["valor_novo"])

    def test_ca07_reativacao_logica(self):
        """CA-07 extra: Permite reativar colaborador inativo com registro no histórico."""
        criado = self.service.cadastrar(self.dados_validos)
        cid = criado["id"]
        self.service.inativar(cid)
        reativado = self.service.reativar(cid, usuario="Diretoria RH")
        self.assertEqual(reativado["situacao"], "ativo")

    # =========================================================================
    # CA-08: PERSISTÊNCIA APÓS REINÍCIO DE CONEXÃO
    # =========================================================================
    def test_ca08_persistencia_apos_reconexao(self):
        """CA-08: Dados persistem de forma durável no SQLite após nova conexão."""
        criado = self.service.cadastrar(self.dados_validos)
        cid = criado["id"]

        # Criar uma nova instância do serviço apontando para o mesmo arquivo de banco
        novo_service = ColaboradorService(db_path=self.temp_db_path)
        recuperado = novo_service.obter_por_id(cid)

        self.assertEqual(recuperado["matricula"], "RH-1001")
        self.assertEqual(recuperado["cpf"], "529.982.247-25")
        self.assertEqual(len(recuperado["dependentes"]), 1)

    # =========================================================================
    # CA-09: ESTRUTURA PARA RESPONSIVIDADE E FRONTEND
    # =========================================================================
    def test_ca09_estrutura_e_filtros(self):
        """CA-09: Suporte a filtragem por setor e contagem de dependentes para a interface."""
        self.service.cadastrar(self.dados_validos)

        outro = dict(self.dados_validos)
        outro["matricula"] = "FIN-3001"
        outro["cpf"] = "85328103068"
        outro["nome_completo"] = "Bruno Oliveira"
        outro["setor"] = "Financeiro"
        outro["dependentes"] = []
        self.service.cadastrar(outro)

        # Filtro por setor
        setor_rh = self.service.listar(setor="Recursos Humanos")
        self.assertEqual(len(setor_rh), 1)
        self.assertEqual(setor_rh[0]["matricula"], "RH-1001")
        self.assertEqual(setor_rh[0]["total_dependentes"], 1)

        setor_fin = self.service.listar(setor="Financeiro")
        self.assertEqual(len(setor_fin), 1)
        self.assertEqual(setor_fin[0]["total_dependentes"], 0)

    # =========================================================================
    # CA-10: REGRESSÃO E INTEGRIDADE
    # =========================================================================
    def test_ca10_integridade_e_nao_regressao(self):
        """CA-10: Não permite edição acidental que viole unicidade com outros colaboradores."""
        self.service.cadastrar(self.dados_validos)

        dados_c2 = dict(self.dados_validos)
        dados_c2["matricula"] = "TI-2002"
        dados_c2["cpf"] = "85328103068"
        dados_c2["nome_completo"] = "Colaborador 2"
        c2 = self.service.cadastrar(dados_c2)

        # Tentar editar c2 colocando o CPF de c1
        dados_c2_mod = dict(dados_c2)
        dados_c2_mod["cpf"] = self.dados_validos["cpf"]
        with self.assertRaises(ValidacaoException):
            self.service.atualizar(c2["id"], dados_c2_mod)

if __name__ == "__main__":
    unittest.main()
