"""
Testes Automatizados da Camada de Serviço de Folha de Pagamento
Testa persistência relacional, validação de duplicidade, auditoria histórica,
cálculos integrados e ciclo de vida da folha (Rascunho -> Calculada -> Fechada -> Reaberta).
"""
import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.service import ColaboradorService
from backend.folha_service import (
    FolhaService, FolhaValidacaoException, FolhaBloqueadaException, FolhaNaoEncontradaException
)


class TestFolhaService(unittest.TestCase):

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)

        self.colab_service = ColaboradorService(db_path=self.temp_db_path)
        self.folha_service = FolhaService(db_path=self.temp_db_path)

        # Cadastra colaborador para os testes
        dados_colab = {
            "matricula": "RH-1001",
            "nome_completo": "Carlos Eduardo Pereira",
            "cpf": "52998224725",  # CPF matematicamente válido
            "rg": "MG-12.345.678",
            "data_nascimento": "1990-05-15",
            "telefone": "(31) 98765-4321",
            "email": "carlos.pereira@empresa.com.br",
            "data_admissao": "2022-03-01",
            "cargo": "Analista de Departamento Pessoal",
            "setor": "Departamento Pessoal",
            "salario_base": 4400.00,
            "situacao": "ativo"
        }
        self.colaborador = self.colab_service.cadastrar(dados_colab, usuario="Admin Teste")

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except PermissionError:
                pass

    def test_criar_e_calcular_folha(self):
        """Cria folha com eventos de horas extras e faltas e valida cálculos persistidos."""
        eventos = [
            {"codigo": "HE50", "quantidade": 10, "percentual": 50.0},
            {"codigo": "FALTA", "quantidade": 1}
        ]

        folha = self.folha_service.criar_ou_atualizar_folha(
            colaborador_id=self.colaborador["id"],
            competencia="2026-10",
            periodo_inicio="2026-10-01",
            periodo_fim="2026-10-31",
            data_pagamento="2026-11-05",
            dias_trabalhados=30,
            dias_mes=30,
            horas_divisor=220.0,
            eventos=eventos,
            observacoes="Folha mensal regular",
            usuario="Analista RH"
        )

        self.assertIsNotNone(folha["id"])
        self.assertEqual(folha["competencia"], "2026-10")
        self.assertEqual(folha["situacao"], "calculada")
        self.assertEqual(folha["salario_base_contratual"], 4400.00)
        self.assertGreater(folha["total_proventos"], 4400.00)
        self.assertGreater(folha["total_descontos"], 0.00)
        self.assertAlmostEqual(folha["salario_liquido"], folha["total_proventos"] - folha["total_descontos"], places=2)

        # Verifica itens persistidos
        codigos = [it["codigo_evento"] for it in folha["itens"]]
        self.assertIn("001", codigos)  # Salário Base
        self.assertIn("101", codigos)  # HE 50%
        self.assertIn("201", codigos)  # Faltas
        self.assertIn("501", codigos)  # INSS
        self.assertIn("901", codigos)  # FGTS (informativo)

        # Auditoria gravada
        self.assertTrue(len(folha["historico"]) > 0)
        self.assertEqual(folha["historico"][0]["acao"], "CRIACAO")
        self.assertIn("Analista RH", folha["historico"][0]["usuario_responsavel"])

    def test_bloqueio_duplicidade_mesmo_colaborador_e_competencia(self):
        """Impede criação de duas folhas para o mesmo funcionário na mesma competência."""
        # Primeira folha criada com sucesso
        self.folha_service.criar_ou_atualizar_folha(
            colaborador_id=self.colaborador["id"],
            competencia="2026-10",
            periodo_inicio="2026-10-01",
            periodo_fim="2026-10-31",
            usuario="Operador 1"
        )

        # Tentativa de criar segunda folha para mesma competência deve falhar
        with self.assertRaises(FolhaValidacaoException) as ctx:
            self.folha_service.criar_ou_atualizar_folha(
                colaborador_id=self.colaborador["id"],
                competencia="2026-10",
                periodo_inicio="2026-10-01",
                periodo_fim="2026-10-31",
                usuario="Operador 2"
            )
        self.assertIn("Já existe uma folha cadastrada", str(ctx.exception.erros.get("competencia", "")))

    def test_fechamento_e_bloqueio_de_edicao(self):
        """Folha fechada não pode ser alterada sem reabertura expressa."""
        folha = self.folha_service.criar_ou_atualizar_folha(
            colaborador_id=self.colaborador["id"],
            competencia="2026-10",
            periodo_inicio="2026-10-01",
            periodo_fim="2026-10-31",
            usuario="Operador"
        )

        # Fechar a folha
        folha_fechada = self.folha_service.fechar_folha(folha["id"], usuario="Gestor DP")
        self.assertEqual(folha_fechada["situacao"], "fechada")
        self.assertEqual(folha_fechada["fechado_por"], "Gestor DP")
        self.assertIsNotNone(folha_fechada["fechado_em"])

        # Tentar editar folha fechada deve levantar exceção
        with self.assertRaises(FolhaBloqueadaException):
            self.folha_service.criar_ou_atualizar_folha(
                colaborador_id=self.colaborador["id"],
                competencia="2026-10",
                periodo_inicio="2026-10-01",
                periodo_fim="2026-10-31",
                folha_id_existente=folha["id"],
                usuario="Operador"
            )

    def test_reabertura_de_folha_com_auditoria(self):
        """Permite reabrir folha fechada registrando o motivo e responsável."""
        folha = self.folha_service.criar_ou_atualizar_folha(
            colaborador_id=self.colaborador["id"],
            competencia="2026-10",
            periodo_inicio="2026-10-01",
            periodo_fim="2026-10-31",
            usuario="Operador"
        )
        self.folha_service.fechar_folha(folha["id"], usuario="Gestor")

        # Reabre folha com justificativa
        folha_reaberta = self.folha_service.reabrir_folha(
            folha["id"],
            motivo="Inclusão de atestado médico que anula 1 falta.",
            usuario="Admin DP"
        )
        self.assertEqual(folha_reaberta["situacao"], "calculada")

        # Confere histórico
        acoes = [h["acao"] for h in folha_reaberta["historico"]]
        self.assertIn("REABERTURA", acoes)

    def test_listagem_e_filtros(self):
        """Testa listagem com filtros de competência e busca por termo."""
        self.folha_service.criar_ou_atualizar_folha(
            colaborador_id=self.colaborador["id"],
            competencia="2026-09",
            periodo_inicio="2026-09-01",
            periodo_fim="2026-09-30"
        )
        self.folha_service.criar_ou_atualizar_folha(
            colaborador_id=self.colaborador["id"],
            competencia="2026-10",
            periodo_inicio="2026-10-01",
            periodo_fim="2026-10-31"
        )

        # Filtro por competência 2026-10
        lista_outubro = self.folha_service.listar_folhas(competencia="2026-10")
        self.assertEqual(len(lista_outubro), 1)
        self.assertEqual(lista_outubro[0]["competencia"], "2026-10")

        # Filtro por termo (Carlos)
        lista_busca = self.folha_service.listar_folhas(termo="Carlos")
        self.assertEqual(len(lista_busca), 2)


if __name__ == "__main__":
    unittest.main()
