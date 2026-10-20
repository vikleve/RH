"""
Executor Principal de Testes Automatizados (Sem abrir navegador)
Executa a suíte completa de testes unitários e de integração de API.
Gera relatório detalhado do atendimento a RF-01 a RF-09 e CA-01 a CA-10.
"""
import unittest
import sys
import os
import time

# Configurar caminhos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from tests.test_colaboradores import TestModuloColaboradores
from tests.test_api import TestApiColaboradores

def executar():
    print("=" * 80)
    print(" SUÍTE DE TESTES AUTOMATIZADOS — MÓDULO 1: CADASTRO DE COLABORADORES")
    print(" Projeto Interdisciplinar RH & GTI — Departamento Pessoal")
    print(" Modo: Execução 100% em código (headless / sem abrir navegador)")
    print("=" * 80)
    print()

    suite = unittest.TestSuite()
    carregador = unittest.TestLoader()

    # Adicionar testes unitários e de negócio
    suite.addTests(carregador.loadTestsFromTestCase(TestModuloColaboradores))
    
    # Adicionar testes de integração da API HTTP
    suite.addTests(carregador.loadTestsFromTestCase(TestApiColaboradores))

    inicio = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    duracao = time.time() - inicio

    print()
    print("=" * 80)
    print(f" RESUMO DA EXECUÇÃO: {resultado.testsRun} testes executados em {duracao:.2f}s")
    print(f" Sucessos: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f" Falhas:   {len(resultado.failures)}")
    print(f" Erros:    {len(resultado.errors)}")
    print("=" * 80)

    if resultado.wasSuccessful():
        print(">> TODOS OS CRITÉRIOS DE ACEITAÇÃO (CA-01 A CA-10) FORAM ATENDIDOS COM SUCESSO! <<")
        return 0
    else:
        print(">> ATENÇÃO: EXISTEM FALHAS NOS TESTES <<")
        return 1

if __name__ == "__main__":
    sys.exit(executar())
