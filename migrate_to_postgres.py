"""
Script de Migração de Dados: SQLite -> PostgreSQL
Copia todos os dados de colaboradores.db para o PostgreSQL configurado no .env / DATABASE_URL.
Execução: python migrate_to_postgres.py
"""
import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import (
    get_database_url, _get_pg_conn, init_db, _SQLITE_PATH
)


def migrar():
    print("=" * 60)
    print("MIGRAÇÃO DE DADOS: SQLite -> PostgreSQL")
    print("=" * 60)

    pg_url = get_database_url()
    if not pg_url:
        print("[ERRO] Nenhuma URL do PostgreSQL encontrada.")
        print("Defina a variável DATABASE_URL no seu arquivo .env:")
        print("Exemplo: DATABASE_URL=postgresql://usuario:senha@host:5432/nome_banco")
        print("Dica: você pode criar um banco gratuito instantâneo em https://supabase.com ou https://neon.tech")
        return False

    sqlite_path = os.path.abspath(_SQLITE_PATH)
    if not os.path.exists(sqlite_path):
        print(f"[ERRO] Arquivo SQLite não encontrado em: {sqlite_path}")
        return False

    print(f"Origem (SQLite): {sqlite_path}")
    print(f"Destino (PostgreSQL): {pg_url.split('@')[-1] if '@' in pg_url else pg_url}")

    print("\n1. Conectando e inicializando schema no PostgreSQL...")
    try:
        pg_conn = _get_pg_conn()
        # Forca criacao das tabelas no PostgreSQL
        # os.environ["DATABASE_URL"] ja esta setado
        init_db(auto_provision=False)
        print("   -> Schema e tabelas no PostgreSQL prontos!")
    except Exception as e:
        print(f"   [ERRO] Falha ao conectar no PostgreSQL: {e}")
        return False

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sq_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    try:
        # Migrar usuarios
        sq_cursor.execute("SELECT * FROM usuarios ORDER BY id;")
        usuarios = sq_cursor.fetchall()
        print(f"\n2. Migrando {len(usuarios)} usuarios...")
        for u in usuarios:
            pg_cursor.execute("""
                INSERT INTO usuarios (id, email, usuario, nome_completo, senha_hash, salt, perfil, status, criado_em, ultimo_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    nome_completo = EXCLUDED.nome_completo,
                    senha_hash = EXCLUDED.senha_hash,
                    salt = EXCLUDED.salt,
                    perfil = EXCLUDED.perfil,
                    status = EXCLUDED.status,
                    ultimo_login = EXCLUDED.ultimo_login;
            """, (
                u["id"], u["email"], u["usuario"], u["nome_completo"],
                u["senha_hash"], u["salt"], u["perfil"], u["status"],
                u["criado_em"], u["ultimo_login"]
            ))
        pg_cursor.execute("SELECT setval('usuarios_id_seq', COALESCE((SELECT MAX(id) FROM usuarios), 1));")

        # Migrar colaboradores
        sq_cursor.execute("SELECT * FROM colaboradores ORDER BY id;")
        colaboradores = sq_cursor.fetchall()
        print(f"3. Migrando {len(colaboradores)} colaboradores...")
        for c in colaboradores:
            pg_cursor.execute("""
                INSERT INTO colaboradores (
                    id, matricula, nome_completo, cpf, rg, data_nascimento,
                    telefone, email, logradouro, numero, bairro, cidade, uf, cep,
                    data_admissao, cargo, setor, salario_base, situacao,
                    criado_em, atualizado_em
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (cpf) DO NOTHING;
            """, (
                c["id"], c["matricula"], c["nome_completo"], c["cpf"], c["rg"],
                c["data_nascimento"], c["telefone"], c["email"], c["logradouro"],
                c["numero"], c["bairro"], c["cidade"], c["uf"], c["cep"],
                c["data_admissao"], c["cargo"], c["setor"], c["salario_base"],
                c["situacao"], c["criado_em"], c["atualizado_em"]
            ))
        pg_cursor.execute("SELECT setval('colaboradores_id_seq', COALESCE((SELECT MAX(id) FROM colaboradores), 1));")

        # Migrar dependentes
        sq_cursor.execute("SELECT * FROM dependentes ORDER BY id;")
        dependentes = sq_cursor.fetchall()
        print(f"4. Migrando {len(dependentes)} dependentes...")
        for d in dependentes:
            pg_cursor.execute("""
                INSERT INTO dependentes (id, colaborador_id, nome, cpf, parentesco)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (d["id"], d["colaborador_id"], d["nome"], d["cpf"], d["parentesco"]))
        pg_cursor.execute("SELECT setval('dependentes_id_seq', COALESCE((SELECT MAX(id) FROM dependentes), 1));")

        # Migrar historico
        sq_cursor.execute("SELECT * FROM historico_alteracoes ORDER BY id;")
        historico = sq_cursor.fetchall()
        print(f"5. Migrando {len(historico)} registros de auditoria...")
        for h in historico:
            pg_cursor.execute("""
                INSERT INTO historico_alteracoes (id, colaborador_id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                h["id"], h["colaborador_id"], h["data_hora"], h["campo_alterado"],
                h["valor_anterior"], h["valor_novo"], h["usuario_responsavel"]
            ))
        pg_cursor.execute("SELECT setval('historico_alteracoes_id_seq', COALESCE((SELECT MAX(id) FROM historico_alteracoes), 1));")

        pg_conn.commit()
        print("\n[SUCESSO] Todos os dados foram migrados com sucesso para o PostgreSQL!")
        return True

    except Exception as e:
        pg_conn.rollback()
        print(f"\n[ERRO] Falha durante a migração: {e}")
        return False
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    sucesso = migrar()
    sys.exit(0 if sucesso else 1)
