"""
Testes Unitários da Camada de Cálculos da Folha de Pagamento
Testa isoladamente cada função matemática e regra de negócio:
- Proporcionalidade de dias
- Valor da hora normal
- Horas extras (50%, 100%, percentuais arbitrários)
- Adicional noturno (normal e com redução ficta)
- Desconto de faltas e atrasos
- DSR sobre variáveis
- INSS e IRRF progressivos
- Valores zerados e limites
- Arredondamentos comerciais (ROUND_HALF_UP)
- Bloqueio de rubricas duplicadas
- Totalizadores: Salário Líquido = Proventos - Descontos
"""
import os
import sys
import unittest
from decimal import Decimal

# Adiciona o diretório base
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.folha_calculos import (
    calcular_adicional_noturno,
    calcular_desconto_atrasos,
    calcular_desconto_faltas,
    calcular_dsr_sobre_variaveis,
    calcular_horas_extras,
    calcular_inss_progressivo,
    calcular_irrf_progressivo,
    calcular_salario_proporcional,
    calcular_valor_hora_normal,
    processar_calculo_folha,
)


class TestFolhaCalculos(unittest.TestCase):

    def test_salario_proporcional_mes_completo(self):
        """Mês completo (30 dias) deve retornar o salário-base integral."""
        valor, mem = calcular_salario_proporcional(salario_base=3000.00, dias_trabalhados=30, dias_mes=30)
        self.assertEqual(valor, Decimal("3000.00"))
        self.assertIn("30/30 dias", mem)

    def test_salario_proporcional_dias_parciais(self):
        """Trabalhou 15 dias de um mês de 30 dias: deve receber exatamente metade."""
        valor, mem = calcular_salario_proporcional(salario_base=3000.00, dias_trabalhados=15, dias_mes=30)
        self.assertEqual(valor, Decimal("1500.00"))
        self.assertIn("15 dias", mem)

    def test_salario_proporcional_admissao_no_mes(self):
        """Trabalhou 10 dias em salário fracionado (ex: R$ 3.456,78)."""
        valor, mem = calcular_salario_proporcional(salario_base=3456.78, dias_trabalhados=10, dias_mes=30)
        # 3456.78 / 30 * 10 = 1152.26
        self.assertEqual(valor, Decimal("1152.26"))

    def test_salario_proporcional_valores_zerados(self):
        """Salário zerado ou dias zerados deve retornar 0.00 sem quebrar."""
        valor, _ = calcular_salario_proporcional(salario_base=0.00, dias_trabalhados=15)
        self.assertEqual(valor, Decimal("0.00"))

        valor2, _ = calcular_salario_proporcional(salario_base=3000.00, dias_trabalhados=0)
        self.assertEqual(valor2, Decimal("0.00"))

    def test_valor_hora_normal(self):
        """Divisor padrão de 220 horas mensais."""
        # R$ 2.200,00 / 220 = R$ 10,00/h
        vh, mem = calcular_valor_hora_normal(salario_base=2200.00, divisor_horas=220.0)
        self.assertEqual(vh, Decimal("10.0000"))
        self.assertIn("220", mem)

        # Divisor 200 horas (jornada de 40h semanais)
        vh200, _ = calcular_valor_hora_normal(salario_base=3000.00, divisor_horas=200.0)
        self.assertEqual(vh200, Decimal("15.0000"))

    def test_horas_extras_50_porcento(self):
        """Hora extra com 50% de acréscimo."""
        # Hora normal: R$ 10,00. HE 50%: R$ 15,00. 10 horas = R$ 150,00.
        total, vh_extra, mem = calcular_horas_extras(valor_hora_normal=10.00, quantidade_horas=10, percentual_adicional=50.0)
        self.assertEqual(vh_extra, Decimal("15.00"))
        self.assertEqual(total, Decimal("150.00"))
        self.assertIn("50", mem)

    def test_horas_extras_100_porcento(self):
        """Hora extra de 100% (domingos e feriados)."""
        # Hora normal: R$ 20,00. HE 100%: R$ 40,00. 5 horas = R$ 200,00.
        total, vh_extra, _ = calcular_horas_extras(valor_hora_normal=20.00, quantidade_horas=5, percentual_adicional=100.0)
        self.assertEqual(vh_extra, Decimal("40.00"))
        self.assertEqual(total, Decimal("200.00"))

    def test_horas_extras_percentual_customizado(self):
        """Hora extra com percentual acordado em CCT (ex: 75%)."""
        # Hora normal: R$ 16,00. Fator 1.75 = R$ 28,00. 4 horas = R$ 112,00.
        total, vh_extra, _ = calcular_horas_extras(valor_hora_normal=16.00, quantidade_horas=4, percentual_adicional=75.0)
        self.assertEqual(vh_extra, Decimal("28.00"))
        self.assertEqual(total, Decimal("112.00"))

    def test_adicional_noturno_padrao_20_porcento(self):
        """Adicional noturno urbano (20% sobre a hora normal)."""
        # Hora normal: R$ 20,00. Adicional 20%: R$ 4,00/h. 25 horas = R$ 100,00.
        total, vh_adic, mem = calcular_adicional_noturno(valor_hora_normal=20.00, quantidade_horas=25, percentual_adicional=20.0)
        self.assertEqual(vh_adic, Decimal("4.00"))
        self.assertEqual(total, Decimal("100.00"))
        self.assertIn("20", mem)

    def test_adicional_noturno_com_reducao_ficta(self):
        """Adicional noturno com hora ficta reduzida (52m30s / fator ~1.142857)."""
        # 35 horas relógio * 1.142857 = 40 horas noturnas computadas
        # Hora normal: R$ 10,00. 20% = R$ 2,00. 40h = R$ 80,00.
        total, vh_adic, mem = calcular_adicional_noturno(
            valor_hora_normal=10.00,
            quantidade_horas=35,
            percentual_adicional=20.0,
            aplicar_reducao_ficta=True,
            fator_reducao=Decimal("1.142857")
        )
        self.assertEqual(vh_adic, Decimal("2.00"))
        self.assertEqual(total, Decimal("80.00"))
        self.assertIn("redução ficta", mem)

    def test_desconto_faltas(self):
        """Desconto de 2 faltas integrais em salário de R$ 3.000,00 (mês 30 dias)."""
        # Valor dia: R$ 100,00. 2 faltas = R$ 200,00.
        total, mem = calcular_desconto_faltas(salario_base=3000.00, dias_falta=2, dias_mes=30)
        self.assertEqual(total, Decimal("200.00"))
        self.assertIn("2 dia(s)", mem)

    def test_desconto_atrasos(self):
        """Desconto de 3.5 horas de atraso com hora normal de R$ 12,00."""
        # 3.5 * 12.00 = R$ 42,00
        total, mem = calcular_desconto_atrasos(valor_hora_normal=12.00, horas_atraso=3.5)
        self.assertEqual(total, Decimal("42.00"))
        self.assertTrue("3,5h" in mem or "3.5h" in mem)

    def test_dsr_sobre_variaveis(self):
        """Cálculo do DSR sobre horas extras (25 dias úteis e 5 domingos/feriados)."""
        # Variáveis: R$ 500,00. DSR: (500 / 25) * 5 = R$ 100,00.
        dsr, mem = calcular_dsr_sobre_variaveis(total_variaveis=500.00, dias_uteis=25, domingos_feriados=5)
        self.assertEqual(dsr, Decimal("100.00"))
        self.assertIn("DSR", mem)

    def test_inss_progressivo_primeira_faixa(self):
        """Salário dentro da 1ª faixa de INSS (7.5%)."""
        # R$ 1.500,00 x 7.5% = R$ 112,50
        inss, aliq_efetiva, mem, faixas = calcular_inss_progressivo(base_inss=1500.00)
        self.assertEqual(inss, Decimal("112.50"))
        self.assertEqual(aliq_efetiva, Decimal("7.50"))
        self.assertEqual(len(faixas), 1)

    def test_inss_progressivo_multiplas_faixas(self):
        """Salário de R$ 3.000,00 incide na 1ª, 2ª e parte da 3ª faixa."""
        inss, aliq, mem, faixas = calcular_inss_progressivo(base_inss=3000.00)
        # Faixa 1 (1518 * 0.075) = 113.85
        # Faixa 2 ((2793.88 - 1518.01) * 0.09 = 1275.87 * 0.09) = 114.83
        # Faixa 3 ((3000 - 2793.89) * 0.12 = 206.11 * 0.12) = 24.73
        # Total esperado: 113.85 + 114.83 + 24.73 = 253.41
        self.assertGreater(inss, Decimal("250.00"))
        self.assertLess(inss, Decimal("260.00"))
        self.assertEqual(len(faixas), 3)

    def test_irrf_isencao(self):
        """Salário abaixo do piso de IRRF deve ser isento (R$ 0,00 de imposto)."""
        irrf, base, mem = calcular_irrf_progressivo(base_bruta_irrf=2500.00, desconto_inss=200.00)
        # Base: 2500 - 200 = 2300 (abaixo de 2826.65, mas acima de 2259.20? 2300 * 0.075 = 172.50 - 169.44 = 3.06)
        # Testando com base líquida bem abaixo de 2259.20:
        irrf_isento, _, _ = calcular_irrf_progressivo(base_bruta_irrf=2000.00, desconto_inss=150.00)
        self.assertEqual(irrf_isento, Decimal("0.00"))

    def test_irrf_deducao_dependentes(self):
        """Dependentes devem reduzir a base de cálculo tributável do IRRF."""
        # Base bruta 4000, inss 400. Sem dependentes: base 3600.
        irrf_sem_dep, base_sem, _ = calcular_irrf_progressivo(base_bruta_irrf=4000.00, desconto_inss=400.00, numero_dependentes=0)
        # Com 2 dependentes (2 * 189.59 = 379.18 a deduzir da base)
        irrf_com_dep, base_com, _ = calcular_irrf_progressivo(base_bruta_irrf=4000.00, desconto_inss=400.00, numero_dependentes=2)
        self.assertLess(base_com, base_sem)
        self.assertLess(irrf_com_dep, irrf_sem_dep)

    def test_processar_folha_completa_totalizadores(self):
        """Valida que: Salário Líquido = Total de Proventos - Total de Descontos."""
        eventos = [
            {"codigo": "HE50", "quantidade": 10, "percentual": 50.0},
            {"codigo": "HE100", "quantidade": 4, "percentual": 100.0},
            {"codigo": "NOTURNO", "quantidade": 20, "percentual": 20.0},
            {"codigo": "FALTA", "quantidade": 1},
            {"codigo": "DESC_CONV", "descricao": "Convênio Farmácia", "tipo": "desconto", "valor_total": 85.50},
            {"codigo": "BONUS", "descricao": "Bônus Desempenho", "tipo": "provento", "valor_total": 500.00}
        ]

        resultado = processar_calculo_folha(
            salario_base=4400.00,
            dias_trabalhados=30,
            dias_mes=30,
            divisor_horas=220.0,
            eventos_informados=eventos,
            numero_dependentes=1,
            parametros_config={"aplicar_inss": True, "aplicar_irrf": True}
        )

        resumo = resultado["resumo"]
        proventos = Decimal(str(resumo["total_proventos"]))
        descontos = Decimal(str(resumo["total_descontos"]))
        liquido = Decimal(str(resumo["salario_liquido"]))

        # Verifica consistência estrita: Liquido == Proventos - Descontos
        self.assertEqual(liquido, proventos - descontos)
        self.assertGreater(proventos, Decimal("4400.00"))  # Salário base + HEs + Noturno + Bônus
        self.assertGreater(descontos, Decimal("0.00"))

        # Verifica presença de itens com memória de cálculo
        for item in resultado["itens"]:
            self.assertTrue(len(item["memoria_calculo"]) > 0)
            self.assertIn(item["tipo"], ("provento", "desconto", "informativo"))

    def test_bloqueio_duplicidade_de_rubrica(self):
        """Não permite lançar duas vezes a mesma rubrica com o mesmo código e tipo na folha."""
        eventos_duplicados = [
            {"codigo": "HE50", "quantidade": 5},
            {"codigo": "HE50", "quantidade": 3}
        ]
        with self.assertRaises(ValueError) as ctx:
            processar_calculo_folha(
                salario_base=3000.00,
                eventos_informados=eventos_duplicados
            )
        self.assertIn("Evento duplicado", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
