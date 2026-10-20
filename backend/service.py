"""
Camada de Serviços de Negócio — Colaboradores
Contém a lógica de aplicação, auditoria de alterações, validações de duplicidade
e manipulação de dados conforme RF-01 a RF-09 e CA-01 a CA-08.
"""
from datetime import datetime
import json
from .database import get_connection, init_db
from .validators import validar_formulario_colaborador, normalizar_cpf, formatar_cpf

CAMPOS_COMPARAVEIS = [
    ("nome_completo", "Nome Completo"),
    ("cpf", "CPF"),
    ("rg", "RG"),
    ("data_nascimento", "Data de Nascimento"),
    ("telefone", "Telefone"),
    ("email", "E-mail"),
    ("logradouro", "Logradouro"),
    ("numero", "Número"),
    ("bairro", "Bairro"),
    ("cidade", "Cidade"),
    ("uf", "UF"),
    ("cep", "CEP"),
    ("matricula", "Matrícula"),
    ("data_admissao", "Data de Admissão"),
    ("cargo", "Cargo"),
    ("setor", "Setor"),
    ("salario_base", "Salário-base"),
    ("situacao", "Situação do Vínculo"),
]

class ValidacaoException(Exception):
    def __init__(self, erros: dict):
        super().__init__("Erros de validação encontrados.")
        self.erros = erros

class RecursoNaoEncontradoException(Exception):
    pass

class ColaboradorService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(self.db_path)

    def cadastrar(self, dados: dict, usuario: str = "Sistema/Administrador") -> dict:
        """Cadastra um novo colaborador com validação e checagem de duplicidade."""
        is_valido, erros, sanitizado = validar_formulario_colaborador(dados, is_edicao=False)
        if not is_valido:
            raise ValidacaoException(erros)
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Checar duplicidade de CPF (CA-03)
        cursor.execute("SELECT id FROM colaboradores WHERE cpf = ?", (sanitizado["cpf"],))
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"cpf": f"Já existe um colaborador cadastrado com o CPF {sanitizado['cpf']}."})
        
        # Checar duplicidade de Matrícula (CA-03)
        cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (sanitizado["matricula"],))
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"matricula": f"Já existe um colaborador cadastrado com a matrícula {sanitizado['matricula']}."})
        
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO colaboradores (
                matricula, nome_completo, cpf, rg, data_nascimento,
                telefone, email, logradouro, numero, bairro, cidade, uf, cep,
                data_admissao, cargo, setor, salario_base, situacao,
                criado_em, atualizado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
            agora
        ))
        
        colaborador_id = cursor.lastrowid
        
        # Inserir dependentes
        for dep in sanitizado.get("dependentes", []):
            cursor.execute("""
                INSERT INTO dependentes (colaborador_id, nome, cpf, parentesco)
                VALUES (?, ?, ?, ?)
            """, (colaborador_id, dep["nome"], dep.get("cpf", ""), dep["parentesco"]))
        
        # Registro inicial no histórico de auditoria (CA-06)
        cursor.execute("""
            INSERT INTO historico_alteracoes (
                colaborador_id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            colaborador_id,
            agora,
            "Criação de Cadastro",
            None,
            f"Colaborador {sanitizado['nome_completo']} admitido com matrícula {sanitizado['matricula']}.",
            usuario
        ))
        
        conn.commit()
        conn.close()
        
        return self.obter_por_id(colaborador_id)

    def listar(self, termo: str = None, situacao: str = None, setor: str = None) -> list[dict]:
        """Lista colaboradores com filtros opcionais por termo (nome/cpf/matrícula), situação e setor."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        sql = """
            SELECT c.*, COUNT(d.id) AS total_dependentes
            FROM colaboradores c
            LEFT JOIN dependentes d ON d.colaborador_id = c.id
            WHERE 1=1
        """
        params = []
        
        if situacao and situacao.lower() in ["ativo", "inativo"]:
            sql += " AND c.situacao = ?"
            params.append(situacao.lower())
        
        if setor and setor.strip():
            sql += " AND LOWER(c.setor) = LOWER(?)"
            params.append(setor.strip())
        
        if termo and termo.strip():
            termo_limpo = termo.strip()
            cpf_digitos = normalizar_cpf(termo_limpo)
            sql += """ AND (
                LOWER(c.nome_completo) LIKE LOWER(?) OR
                c.matricula LIKE ? OR
                c.cpf LIKE ? OR
                (? != '' AND REPLACE(REPLACE(c.cpf, '.', ''), '-', '') LIKE ?)
            )"""
            padrao = f"%{termo_limpo}%"
            padrao_cpf = f"%{cpf_digitos}%" if cpf_digitos else ""
            params.extend([padrao, padrao, padrao, cpf_digitos, padrao_cpf])
        
        sql += " GROUP BY c.id ORDER BY c.nome_completo ASC"
        
        cursor.execute(sql, params)
        linhas = cursor.fetchall()
        resultado = [dict(linha) for linha in linhas]
        conn.close()
        return resultado

    def obter_por_id(self, colaborador_id: int) -> dict:
        """Retorna os dados completos do colaborador, seus dependentes e histórico."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM colaboradores WHERE id = ?", (colaborador_id,))
        colab = cursor.fetchone()
        if not colab:
            conn.close()
            raise RecursoNaoEncontradoException(f"Colaborador com ID {colaborador_id} não encontrado.")
        
        colab_dict = dict(colab)
        
        # Buscar dependentes
        cursor.execute("SELECT id, nome, cpf, parentesco FROM dependentes WHERE colaborador_id = ?", (colaborador_id,))
        colab_dict["dependentes"] = [dict(d) for d in cursor.fetchall()]
        
        # Buscar histórico de alterações
        cursor.execute("""
            SELECT id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel
            FROM historico_alteracoes
            WHERE colaborador_id = ?
            ORDER BY id DESC
        """, (colaborador_id,))
        colab_dict["historico"] = [dict(h) for h in cursor.fetchall()]
        
        conn.close()
        return colab_dict

    def atualizar(self, colaborador_id: int, dados: dict, usuario: str = "Sistema/Administrador") -> dict:
        """Atualiza dados do colaborador preservando o ID e auditando alterações (CA-05, CA-06)."""
        atual = self.obter_por_id(colaborador_id)
        
        is_valido, erros, sanitizado = validar_formulario_colaborador(dados, is_edicao=True)
        if not is_valido:
            raise ValidacaoException(erros)
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Checar unicidade de CPF desconsiderando o próprio registro
        cursor.execute("SELECT id FROM colaboradores WHERE cpf = ? AND id != ?", (sanitizado["cpf"], colaborador_id))
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"cpf": f"O CPF {sanitizado['cpf']} já pertence a outro colaborador."})
        
        # Checar unicidade de Matrícula desconsiderando o próprio registro
        cursor.execute("SELECT id FROM colaboradores WHERE matricula = ? AND id != ?", (sanitizado["matricula"], colaborador_id))
        if cursor.fetchone():
            conn.close()
            raise ValidacaoException({"matricula": f"A matrícula {sanitizado['matricula']} já pertence a outro colaborador."})
        
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Identificar e auditar alterações campo a campo
        alteracoes = []
        for campo_bd, rotulo in CAMPOS_COMPARAVEIS:
            val_antigo = atual.get(campo_bd)
            val_novo = sanitizado.get(campo_bd)
            
            # Normalização para comparação justa
            str_antigo = "" if val_antigo is None else str(val_antigo).strip()
            str_novo = "" if val_novo is None else str(val_novo).strip()
            
            if campo_bd == "salario_base" and val_antigo is not None and val_novo is not None:
                if abs(float(val_antigo) - float(val_novo)) > 0.001:
                    alteracoes.append((rotulo, f"R$ {float(val_antigo):.2f}", f"R$ {float(val_novo):.2f}"))
            elif str_antigo != str_novo:
                alteracoes.append((rotulo, str_antigo, str_novo))
        
        # Atualizar tabela principal
        cursor.execute("""
            UPDATE colaboradores SET
                matricula = ?,
                nome_completo = ?,
                cpf = ?,
                rg = ?,
                data_nascimento = ?,
                telefone = ?,
                email = ?,
                logradouro = ?,
                numero = ?,
                bairro = ?,
                cidade = ?,
                uf = ?,
                cep = ?,
                data_admissao = ?,
                cargo = ?,
                setor = ?,
                salario_base = ?,
                situacao = ?,
                atualizado_em = ?
            WHERE id = ?
        """, (
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
            sanitizado.get("situacao", atual["situacao"]),
            agora,
            colaborador_id
        ))
        
        # Atualizar dependentes e auditar alterações em dependentes se houver
        deps_antigos = atual.get("dependentes", [])
        deps_novos = sanitizado.get("dependentes", [])
        
        cursor.execute("DELETE FROM dependentes WHERE colaborador_id = ?", (colaborador_id,))
        for dep in deps_novos:
            cursor.execute("""
                INSERT INTO dependentes (colaborador_id, nome, cpf, parentesco)
                VALUES (?, ?, ?, ?)
            """, (colaborador_id, dep["nome"], dep.get("cpf", ""), dep["parentesco"]))
        
        if len(deps_antigos) != len(deps_novos) or json.dumps(deps_antigos, sort_keys=True) != json.dumps(deps_novos, sort_keys=True):
            alteracoes.append((
                "Dependentes",
                f"{len(deps_antigos)} dependente(s)",
                f"{len(deps_novos)} dependente(s)"
            ))
        
        # Gravar entradas no histórico de alterações
        for campo, antigo, novo in alteracoes:
            cursor.execute("""
                INSERT INTO historico_alteracoes (
                    colaborador_id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (colaborador_id, agora, campo, antigo, novo, usuario))
        
        conn.commit()
        conn.close()
        
        return self.obter_por_id(colaborador_id)

    def inativar(self, colaborador_id: int, motivo: str = None, usuario: str = "Sistema/Administrador") -> dict:
        """Inativação lógica do colaborador sem excluir histórico ou dados (CA-07)."""
        atual = self.obter_por_id(colaborador_id)
        if atual["situacao"] == "inativo":
            return atual
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE colaboradores
            SET situacao = 'inativo', atualizado_em = ?
            WHERE id = ?
        """, (agora, colaborador_id))
        
        desc_motivo = f" (Motivo: {motivo})" if motivo and motivo.strip() else ""
        cursor.execute("""
            INSERT INTO historico_alteracoes (
                colaborador_id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            colaborador_id,
            agora,
            "Situação do Vínculo",
            "ativo",
            f"inativo{desc_motivo}",
            usuario
        ))
        
        conn.commit()
        conn.close()
        return self.obter_por_id(colaborador_id)

    def reativar(self, colaborador_id: int, usuario: str = "Sistema/Administrador") -> dict:
        """Reativação lógica do colaborador com auditoria."""
        atual = self.obter_por_id(colaborador_id)
        if atual["situacao"] == "ativo":
            return atual
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE colaboradores
            SET situacao = 'ativo', atualizado_em = ?
            WHERE id = ?
        """, (agora, colaborador_id))
        
        cursor.execute("""
            INSERT INTO historico_alteracoes (
                colaborador_id, data_hora, campo_alterado, valor_anterior, valor_novo, usuario_responsavel
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            colaborador_id,
            agora,
            "Situação do Vínculo",
            "inativo",
            "ativo",
            usuario
        ))
        
        conn.commit()
        conn.close()
        return self.obter_por_id(colaborador_id)
