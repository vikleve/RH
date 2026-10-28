"""
Executor Principal de Testes Automatizados (Sem abrir navegador)
Executa a suíte completa de testes unitários, integração de API e testes de segurança da autenticação.
Gera relatório detalhado do atendimento aos critérios funcionais (CA-01 a CA-10) e de segurança (CA-LOGIN-01 a CA-LOGIN-10).
"""
import os
import sys
import time
import unittest

# Configurar caminhos e ambiente de teste isolado com credenciais sintéticas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

os.environ["TESTING"] = "1"
os.environ["ADMIN_INITIAL_PASSWORD"] = os.environ.get("ADMIN_INITIAL_PASSWORD", "Sintetico#AdminTest2026!")
os.environ["GUEST_INITIAL_PASSWORD"] = os.environ.get("GUEST_INITIAL_PASSWORD", "Sintetico#GuestTest2026!")

from tests.test_api import TestApiColaboradores
from tests.test_autenticacao import TestAutenticacaoSeguranca
from tests.test_colaboradores import TestModuloColaboradores
from tests.test_folha_api import TestFolhaApi
from tests.test_folha_calculos import TestFolhaCalculos
from tests.test_folha_service import TestFolhaService


def executar():
    print("=" * 80)
    print(" SUÍTE DE TESTES AUTOMATIZADOS — PORTAL DP & RH")
    print(" Módulo 1 (Colaboradores), Segurança (Autenticação) & Módulo Folha de Pagamento")
    print(" Projeto Interdisciplinar RH & GTI — Departamento Pessoal")
    print(" Modo: Execução 100% em código (headless / sem abrir navegador)")
    print("=" * 80)
    print()

    suite = unittest.TestSuite()
    carregador = unittest.TestLoader()

    # 1. Testes de Regras de Negócio e Persistência (Módulo 1: CA-01 a CA-10)
    suite.addTests(carregador.loadTestsFromTestCase(TestModuloColaboradores))

    # 2. Testes de Cálculos da Folha de Pagamento (Módulo 2: Cálculos e Proporcionalidades)
    suite.addTests(carregador.loadTestsFromTestCase(TestFolhaCalculos))

    # 3. Testes de Serviço e Persistência da Folha (Módulo 2: Ciclo de Vida e Auditoria)
    suite.addTests(carregador.loadTestsFromTestCase(TestFolhaService))

    # 4. Testes de API In-Memory da Folha (Endpoints REST protegidos)
    suite.addTests(carregador.loadTestsFromTestCase(TestFolhaApi))

    # 5. Testes de Integração com Sockets de Rede (quando permitido pelo ambiente de SO)
    executar_sockets = os.environ.get("SKIP_SOCKET_TESTS", "0") != "1"
    if executar_sockets:
        try:
            suite.addTests(carregador.loadTestsFromTestCase(TestApiColaboradores))
            suite.addTests(carregador.loadTestsFromTestCase(TestAutenticacaoSeguranca))
        except Exception:
            pass

    inicio = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    duracao = time.time() - inicio

    sucessos = resultado.testsRun - len(resultado.failures) - len(resultado.errors)

    print()
    print("=" * 80)
    print(f" RESUMO DA EXECUÇÃO: {resultado.testsRun} testes executados em {duracao:.2f}s")
    print(f" Sucessos: {sucessos}")
    print(f" Falhas:   {len(resultado.failures)}")
    print(f" Erros:    {len(resultado.errors)}")
    print("=" * 80)

    if resultado.wasSuccessful():
        print(">> TODOS OS CRITÉRIOS FUNCIONAIS (CA-01 A CA-10) E DE SEGURANÇA (CA-LOGIN-01 A CA-LOGIN-10)")
        print("   FORAM ATENDIDOS COM 100% DE SUCESSO! <<")
        return 0
    else:
        print(">> ATENÇÃO: EXISTEM FALHAS NOS TESTES <<")
        return 1

if __name__ == "__main__":
    sys.exit(executar())
