"""
Script de Diagnóstico e Teste de Conexão com o Banco de Dados — RH/DP
Execução: python test_db.py
"""
import os
import sys

# Adiciona o diretorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import _usar_postgres, get_connection, get_database_url, init_db


def testar_banco():
    print("=" * 60)
    print("DIAGNÓSTICO DO BANCO DE DADOS — SISTEMA RH / DP")
    print("=" * 60)

    usando_pg = _usar_postgres()
    modo = "PostgreSQL (Produção / Nuvem / Concorrente)" if usando_pg else "SQLite (Local / Desenvolvimento / Testes)"

    print(f"Modo detectado: {modo}")
    if usando_pg:
        db_url = get_database_url()
        # Oculta senha para seguranca
        url_mascarada = db_url
        if "@" in db_url and "://" in db_url:
            prefix, rest = db_url.split("://", 1)
            creds, host_db = rest.split("@", 1)
            user = creds.split(":", 1)[0]
            url_mascarada = f"{prefix}://{user}:****@{host_db}"
        print(f"URL configurada: {url_mascarada}")
    else:
        sqlite_path = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "colaboradores.db"))
        print(f"Arquivo SQLite: {os.path.abspath(sqlite_path)}")

    print("\n1. Inicializando DDL (tabelas, índices e constraints)...")
    try:
        init_db(auto_provision=True)
        print("   -> Tabelas e índices verificados/criados com sucesso!")
    except Exception as e:
        print(f"   [ERRO] Falha ao inicializar banco: {e}")
        return False

    print("\n2. Testando conexão e contagem de registros...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM colaboradores;")
        total_colabs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dependentes;")
        total_dep = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM historico_alteracoes;")
        total_hist = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM folha_parametros;")
        total_param = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM folhas_pagamento;")
        total_folhas = cursor.fetchone()[0]

        conn.close()

        print(f"   -> Colaboradores cadastrados: {total_colabs}")
        print(f"   -> Usuários do sistema:      {total_users}")
        print(f"   -> Dependentes cadastrados:   {total_dep}")
        print(f"   -> Registros de auditoria:    {total_hist}")
        print(f"   -> Parâmetros de folha:       {total_param}")
        print(f"   -> Folhas de pagamento:       {total_folhas}")
        print("\n[SUCESSO] O banco de dados está operando 100% corretamente!")
        return True
    except Exception as e:
        print(f"   [ERRO] Falha ao consultar registros: {e}")
        return False


if __name__ == "__main__":
    sucesso = testar_banco()
    sys.exit(0 if sucesso else 1)
