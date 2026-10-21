"""
Camada de Servicos de Negocio — Colaboradores
Contem a logica de aplicacao, auditoria de alteracoes, validacoes de duplicidade
e manipulacao de dados conforme RF-01 a RF-09 e CA-01 a CA-08.
Funciona com PostgreSQL (producao) e SQLite (desenvolvimento local e testes).
"""
from datetime import datetime
import json
from .database import (
    get_connection, init_db, ph,
    fetchone_dict, fetchall_dict, insert_returning_id, _usar_postgres
)
from .validators import validar_formulario_colaborador, normalizar_cpf

CAMPOS_COMPARAVEIS = [
    ("nome_completo",   "Nome Completo"),
    ("cpf",             "CPF"),
    ("rg",              "RG"),
    ("data_nascimento", "Data de Nascimento"),
    ("telefone",        "Telefone"),
    ("email",           "E-mail"),
    ("logradouro",      "Logradouro"),
    ("numero",          "Numero"),
    ("bairro",          "Bairro"),
    ("cidade",          "Cidade"),
    ("uf",              "UF"),
    ("cep",             "CEP"),
    ("matricula",       "Matricula"),
    ("data_admissao",   "Data de Admissao"),
    ("cargo",           "Cargo"),
    ("setor",           "Setor"),
    ("salario_base",    "Salário-base"),
    ("situacao",        "Situação do Vínculo"),
]


class ValidacaoException(Exception):
    def __init__(self, erros: dict):
        super().__init__("Erros de validacao encontrados.")
        self.erros = erros


class RecursoNaoEncontradoException(Exception):
    pass


class ColaboradorService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(self.db_path)

    # ──────────────────────────────────────────────────────────
    # Shortcut helpers que carregam db_path automaticamente
    # ──────────────────────────────────────────────────────────

    def _ph(self) -> str:
        return ph(self.db_path)

    def _pg(self) -> bool:
        return _usar_postgres(self.db_path)

    def _conn(self):
        return get_connection(self.db_path)

    def _fetchone(self, cursor):
        return fetchone_dict(cursor, self.db_path)

    def _fetchall(self, cursor):
        return fetchall_dict(cursor, self.db_path)

    def _insert_id(self, cursor, conn, sql_pg, sql_sqlite, params):
        return insert_returning_id(cursor, conn, sql_pg, sql_sqlite, params, self.db_path)

    # ──────────────────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────────────────

    def cadastrar(self, dados: dict, usuario: str = "Sistema/Administrador") -> dict:
        """Cadastra um novo colaborador com validacao e checagem de duplicidade."""
        is_valido, erros, sanitizado = validar_formulario_colaborador(dados, is_edicao=False)
        if not is_valido:
            raise ValidacaoException(erros)

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(f"SELECT id FROM colaboradores WHERE cpf = {P}", (sanitizado["cpf"],))
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"cpf": f"Ja existe um colaborador com o CPF {sanitizado['cpf']}."})

        cursor.execute(f"SELECT id FROM colaboradores WHERE matricula = {P}", (sanitizado["matricula"],))
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"matricula": f"Ja existe um colaborador com a matricula {sanitizado['matricula']}."})

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql_pg = """
            INSERT INTO colaboradores (
                matricula, nome_completo, cpf, rg, data_nascimento,
                telefone, email, logradouro, numero, bairro, cidade, uf, cep,
                data_admissao, cargo, setor, salario_base, situacao,
                criado_em, atualizado_em
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """
        sql_sqlite = """
            INSERT INTO colaboradores (
                matricula, nome_completo, cpf, rg, data_nascimento,
                telefone, email, logradouro, numero, bairro, cidade, uf, cep,
                data_admissao, cargo, setor, salario_base, situacao,
                criado_em, atualizado_em
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        params = (
            sanitizado["matricula"],
            sanitizado["nome_completo"],
            sanitizado["cpf"],
            sanitizado.get("rg", ""),
            sanitizado["data_nascimento"],
            sanitizado.get("telefone", ""),
            sanitizado["email"],
            sanitizado.get("logradouro", ""),
            sanitizado.get("numero", ""),
            sanitizado.get("bairro", ""),
            sanitizado.get("cidade", ""),
            sanitizado.get("uf", ""),
            sanitizado.get("cep", ""),
            sanitizado["data_admissao"],
            sanitizado["cargo"],
            sanitizado["setor"],
            sanitizado["salario_base"],
            sanitizado.get("situacao", "ativo"),
            agora,
            agora,
        )

        colaborador_id = self._insert_id(cursor, conn, sql_pg, sql_sqlite, params)

        for dep in sanitizado.get("dependentes", []):
            cursor.execute(f"""
                INSERT INTO dependentes (colaborador_id, nome, cpf, parentesco)
                VALUES ({P},{P},{P},{P})
            """, (colaborador_id, dep["nome"], dep.get("cpf", ""), dep["parentesco"]))

        cursor.execute(f"""
            INSERT INTO historico_alteracoes (
                colaborador_id, data_hora, campo_alterado,
                valor_anterior, valor_novo, usuario_responsavel
            ) VALUES ({P},{P},{P},{P},{P},{P})
        """, (
            colaborador_id, agora, "Criacao de Cadastro",
            None,
            f"Colaborador {sanitizado['nome_completo']} admitido com matricula {sanitizado['matricula']}.",
            usuario,
        ))

        conn.commit()
        conn.close()
        return self.obter_por_id(colaborador_id)

    def listar(self, termo: str = None, situacao: str = None, setor: str = None) -> list:
        """Lista colaboradores com filtros opcionais."""
        P = self._ph()
        pg = self._pg()

        conn = self._conn()
        cursor = conn.cursor()

        sql = """
            SELECT c.*, COUNT(d.id) AS total_dependentes
            FROM colaboradores c
            LEFT JOIN dependentes d ON d.colaborador_id = c.id
            WHERE 1=1
        """
        params = []

        if situacao and situacao.lower() in ("ativo", "inativo"):
            sql += f" AND c.situacao = {P}"
            params.append(situacao.lower())

        if setor and setor.strip():
            if pg:
                sql += f" AND c.setor ILIKE {P}"
            else:
                sql += f" AND LOWER(c.setor) = LOWER({P})"
            params.append(setor.strip())

        if termo and termo.strip():
            termo_limpo = termo.strip()
            cpf_digitos = normalizar_cpf(termo_limpo)
            padrao = f"%{termo_limpo}%"
            padrao_cpf = f"%{cpf_digitos}%" if cpf_digitos else ""

            if pg:
                sql += f""" AND (
                    c.nome_completo ILIKE {P} OR
                    c.matricula     ILIKE {P} OR
                    c.cpf           ILIKE {P} OR
                    ({P} != '' AND REPLACE(REPLACE(c.cpf, '.', ''), '-', '') ILIKE {P})
                )"""
            else:
                sql += f""" AND (
                    LOWER(c.nome_completo) LIKE LOWER({P}) OR
                    c.matricula LIKE {P} OR
                    c.cpf LIKE {P} OR
                    ({P} != '' AND REPLACE(REPLACE(c.cpf, '.', ''), '-', '') LIKE {P})
                )"""
            params.extend([padrao, padrao, padrao, cpf_digitos, padrao_cpf])

        sql += " GROUP BY c.id ORDER BY c.nome_completo ASC"

        cursor.execute(sql, params)
        resultado = self._fetchall(cursor)
        conn.close()

        for r in resultado:
            if r.get("salario_base") is not None:
                r["salario_base"] = float(r["salario_base"])
        return resultado

    def obter_por_id(self, colaborador_id: int) -> dict:
        """Retorna dados completos do colaborador, dependentes e historico."""
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM colaboradores WHERE id = {P}", (colaborador_id,))
        colab = self._fetchone(cursor)
        if not colab:
            conn.close()
            raise RecursoNaoEncontradoException(f"Colaborador com ID {colaborador_id} nao encontrado.")

        cursor.execute(
            f"SELECT id, nome, cpf, parentesco FROM dependentes WHERE colaborador_id = {P}",
            (colaborador_id,)
        )
        colab["dependentes"] = self._fetchall(cursor)

        cursor.execute(f"""
            SELECT id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel
            FROM historico_alteracoes
            WHERE colaborador_id = {P}
            ORDER BY id DESC
        """, (colaborador_id,))
        colab["historico"] = self._fetchall(cursor)

        conn.close()

        if colab.get("salario_base") is not None:
            colab["salario_base"] = float(colab["salario_base"])
        return colab

    def atualizar(self, colaborador_id: int, dados: dict, usuario: str = "Sistema/Administrador") -> dict:
        """Atualiza dados do colaborador preservando o ID e auditando alteracoes."""
        atual = self.obter_por_id(colaborador_id)
        is_valido, erros, sanitizado = validar_formulario_colaborador(dados, is_edicao=True)
        if not is_valido:
            raise ValidacaoException(erros)

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT id FROM colaboradores WHERE cpf = {P} AND id != {P}",
            (sanitizado["cpf"], colaborador_id)
        )
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"cpf": f"O CPF {sanitizado['cpf']} ja pertence a outro colaborador."})

        cursor.execute(
            f"SELECT id FROM colaboradores WHERE matricula = {P} AND id != {P}",
            (sanitizado["matricula"], colaborador_id)
        )
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"matricula": f"A matricula {sanitizado['matricula']} ja pertence a outro colaborador."})

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        alteracoes = []
        for campo_bd, rotulo in CAMPOS_COMPARAVEIS:
            val_antigo = atual.get(campo_bd)
            val_novo   = sanitizado.get(campo_bd)
            str_antigo = "" if val_antigo is None else str(val_antigo).strip()
            str_novo   = "" if val_novo   is None else str(val_novo).strip()

            if campo_bd == "salario_base" and val_antigo is not None and val_novo is not None:
                if abs(float(val_antigo) - float(val_novo)) > 0.001:
                    alteracoes.append((rotulo, f"R$ {float(val_antigo):.2f}", f"R$ {float(val_novo):.2f}"))
            elif str_antigo != str_novo:
                alteracoes.append((rotulo, str_antigo, str_novo))

        cursor.execute(f"""
            UPDATE colaboradores SET
                matricula={P}, nome_completo={P}, cpf={P}, rg={P},
                data_nascimento={P}, telefone={P}, email={P},
                logradouro={P}, numero={P}, bairro={P}, cidade={P},
                uf={P}, cep={P}, data_admissao={P}, cargo={P},
                setor={P}, salario_base={P}, situacao={P}, atualizado_em={P}
            WHERE id={P}
        """, (
            sanitizado["matricula"], sanitizado["nome_completo"],
            sanitizado["cpf"], sanitizado.get("rg", ""),
            sanitizado["data_nascimento"], sanitizado.get("telefone", ""),
            sanitizado["email"], sanitizado.get("logradouro", ""),
            sanitizado.get("numero", ""), sanitizado.get("bairro", ""),
            sanitizado.get("cidade", ""), sanitizado.get("uf", ""),
            sanitizado.get("cep", ""), sanitizado["data_admissao"],
            sanitizado["cargo"], sanitizado["setor"],
            sanitizado["salario_base"], sanitizado.get("situacao", atual["situacao"]),
            agora, colaborador_id,
        ))

        deps_antigos = atual.get("dependentes", [])
        deps_novos   = sanitizado.get("dependentes", [])

        cursor.execute(f"DELETE FROM dependentes WHERE colaborador_id = {P}", (colaborador_id,))
        for dep in deps_novos:
            cursor.execute(f"""
                INSERT INTO dependentes (colaborador_id, nome, cpf, parentesco)
                VALUES ({P},{P},{P},{P})
            """, (colaborador_id, dep["nome"], dep.get("cpf", ""), dep["parentesco"]))

        if (len(deps_antigos) != len(deps_novos) or
                json.dumps(deps_antigos, sort_keys=True) != json.dumps(deps_novos, sort_keys=True)):
            alteracoes.append((
                "Dependentes",
                f"{len(deps_antigos)} dependente(s)",
                f"{len(deps_novos)} dependente(s)",
            ))

        for campo, antigo, novo in alteracoes:
            cursor.execute(f"""
                INSERT INTO historico_alteracoes (
                    colaborador_id, data_hora, campo_alterado,
                    valor_anterior, valor_novo, usuario_responsavel
                ) VALUES ({P},{P},{P},{P},{P},{P})
            """, (colaborador_id, agora, campo, antigo, novo, usuario))

        conn.commit()
        conn.close()
        return self.obter_por_id(colaborador_id)

    def inativar(self, colaborador_id: int, motivo: str = None, usuario: str = "Sistema/Administrador") -> dict:
        """Inativacao logica sem excluir historico ou dados."""
        atual = self.obter_por_id(colaborador_id)
        if atual["situacao"] == "inativo":
            return atual

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(f"""
            UPDATE colaboradores SET situacao='inativo', atualizado_em={P} WHERE id={P}
        """, (agora, colaborador_id))

        desc_motivo = f" (Motivo: {motivo})" if motivo and motivo.strip() else ""
        cursor.execute(f"""
            INSERT INTO historico_alteracoes (
                colaborador_id, data_hora, campo_alterado,
                valor_anterior, valor_novo, usuario_responsavel
            ) VALUES ({P},{P},{P},{P},{P},{P})
        """, (colaborador_id, agora, "Situação do Vínculo", "ativo", f"inativo{desc_motivo}", usuario))

        conn.commit()
        conn.close()
        return self.obter_por_id(colaborador_id)

    def reativar(self, colaborador_id: int, usuario: str = "Sistema/Administrador") -> dict:
        """Reativacao logica com auditoria."""
        atual = self.obter_por_id(colaborador_id)
        if atual["situacao"] == "ativo":
            return atual

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(f"""
            UPDATE colaboradores SET situacao='ativo', atualizado_em={P} WHERE id={P}
        """, (agora, colaborador_id))

        cursor.execute(f"""
            INSERT INTO historico_alteracoes (
                colaborador_id, data_hora, campo_alterado,
                valor_anterior, valor_novo, usuario_responsavel
            ) VALUES ({P},{P},{P},{P},{P},{P})
        """, (colaborador_id, agora, "Situação do Vínculo", "inativo", "ativo", usuario))

        conn.commit()
        conn.close()
        return self.obter_por_id(colaborador_id)
