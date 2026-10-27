"""
Camada de Serviços da Folha de Pagamento — RH / DP
Regras de negócio, persistência relacional, validação de unicidade,
auditoria histórica, ciclo de vida da folha (Rascunho -> Calculada -> Fechada)
e integração com a camada de cálculos.
Funciona em modo dual: PostgreSQL (produção/Supabase) e SQLite (local/testes).
"""
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple

from .database import (
    get_connection, init_db, ph,
    fetchone_dict, fetchall_dict, insert_returning_id, _usar_postgres
)
from .folha_calculos import processar_calculo_folha, formatar_moeda


class FolhaValidacaoException(Exception):
    def __init__(self, erros: dict):
        super().__init__("Inconsistência nos dados da folha de pagamento.")
        self.erros = erros


class FolhaNaoEncontradaException(Exception):
    pass


class FolhaBloqueadaException(Exception):
    pass


class FolhaService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(self.db_path)

    # ──────────────────────────────────────────────────────────
    # DB Helpers
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
    # Parâmetros de Folha
    # ──────────────────────────────────────────────────────────

    def obter_parametro_vigente(self) -> Dict[str, Any]:
        """Retorna os parâmetros de folha ativos vigentes."""
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM folha_parametros WHERE ativo = 1 ORDER BY id DESC LIMIT 1;"
        )
        param = self._fetchone(cursor)
        conn.close()
        if not param:
            # Fallback seguro caso a tabela esteja vazia
            return {
                "id": 1,
                "codigo": "PADRAO_CLT_2026",
                "descricao": "Parâmetros Padrão CLT 2026",
                "horas_mensais_padrao": 220.0,
                "dias_mes_padrao": 30,
                "percentual_he_padrao": 50.0,
                "percentual_he_extra": 100.0,
                "percentual_adicional_noturno": 20.0,
                "aplicar_reducao_noturna": 0,
                "fator_reducao_noturna": 1.142857,
                "aplicar_inss": 1,
                "aplicar_irrf": 1,
                "aliquota_fgts": 8.0,
                "teto_inss": 8157.41,
                "deducao_dependente_irrf": 189.59,
                "ativo": 1,
                "validado_por_profissional": 1
            }
        return param

    def salvar_parametros(self, dados: Dict[str, Any], usuario: str = "Sistema/Administrador") -> Dict[str, Any]:
        """Cria ou atualiza parâmetros de cálculo."""
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        codigo = dados.get("codigo", "CONFIG_CUSTOM").strip().upper()
        desc = dados.get("descricao", "Parâmetros Customizados").strip()
        vig_ini = dados.get("vigencia_inicio", "2026-01-01").strip()
        vig_fim = dados.get("vigencia_fim") or None

        cursor.execute(f"SELECT id FROM folha_parametros WHERE codigo = {P}", (codigo,))
        existente = cursor.fetchone()

        params_values = (
            desc, vig_ini, vig_fim,
            float(dados.get("horas_mensais_padrao", 220.0)),
            int(dados.get("dias_mes_padrao", 30)),
            float(dados.get("percentual_he_padrao", 50.0)),
            float(dados.get("percentual_he_extra", 100.0)),
            float(dados.get("percentual_adicional_noturno", 20.0)),
            int(dados.get("aplicar_reducao_noturna", 0)),
            float(dados.get("fator_reducao_noturna", 1.142857)),
            int(dados.get("aplicar_inss", 1)),
            int(dados.get("aplicar_irrf", 1)),
            float(dados.get("aliquota_fgts", 8.0)),
            float(dados.get("teto_inss", 8157.41)),
            float(dados.get("deducao_dependente_irrf", 189.59)),
            int(dados.get("ativo", 1)),
            int(dados.get("validado_por_profissional", 0)),
            agora
        )

        if existente:
            param_id = existente[0]
            cursor.execute(f"""
                UPDATE folha_parametros SET
                    descricao = {P}, vigencia_inicio = {P}, vigencia_fim = {P},
                    horas_mensais_padrao = {P}, dias_mes_padrao = {P}, percentual_he_padrao = {P},
                    percentual_he_extra = {P}, percentual_adicional_noturno = {P}, aplicar_reducao_noturna = {P},
                    fator_reducao_noturna = {P}, aplicar_inss = {P}, aplicar_irrf = {P}, aliquota_fgts = {P},
                    teto_inss = {P}, deducao_dependente_irrf = {P}, ativo = {P}, validado_por_profissional = {P},
                    atualizado_em = {P}
                WHERE id = {param_id};
            """, params_values)
        else:
            sql_pg = f"""
                INSERT INTO folha_parametros (
                    descricao, vigencia_inicio, vigencia_fim,
                    horas_mensais_padrao, dias_mes_padrao, percentual_he_padrao,
                    percentual_he_extra, percentual_adicional_noturno, aplicar_reducao_noturna,
                    fator_reducao_noturna, aplicar_inss, aplicar_irrf, aliquota_fgts,
                    teto_inss, deducao_dependente_irrf, ativo, validado_por_profissional,
                    atualizado_em, codigo, criado_em
                ) VALUES ({P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P})
                RETURNING id;
            """
            sql_sqlite = f"""
                INSERT INTO folha_parametros (
                    descricao, vigencia_inicio, vigencia_fim,
                    horas_mensais_padrao, dias_mes_padrao, percentual_he_padrao,
                    percentual_he_extra, percentual_adicional_noturno, aplicar_reducao_noturna,
                    fator_reducao_noturna, aplicar_inss, aplicar_irrf, aliquota_fgts,
                    teto_inss, deducao_dependente_irrf, ativo, validado_por_profissional,
                    atualizado_em, codigo, criado_em
                ) VALUES ({P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P},{P});
            """
            param_id = self._insert_id(cursor, conn, sql_pg, sql_sqlite, params_values + (codigo, agora))

        conn.commit()
        cursor.execute(f"SELECT * FROM folha_parametros WHERE id = {P}", (param_id,))
        resultado = self._fetchone(cursor)
        conn.close()
        return resultado

    # ──────────────────────────────────────────────────────────
    # Dados Contratuais e Dependentes do Colaborador
    # ──────────────────────────────────────────────────────────

    def obter_dados_colaborador(self, colaborador_id: int) -> Dict[str, Any]:
        """Busca dados contratuais e dependentes para o cálculo da folha."""
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM colaboradores WHERE id = {P}", (colaborador_id,))
        colab = self._fetchone(cursor)
        if not colab:
            conn.close()
            raise FolhaNaoEncontradaException(f"Colaborador com ID {colaborador_id} não encontrado.")

        cursor.execute(f"SELECT COUNT(*) FROM dependentes WHERE colaborador_id = {P}", (colaborador_id,))
        total_dep = cursor.fetchone()[0]
        colab["total_dependentes"] = total_dep

        conn.close()
        return colab

    # ──────────────────────────────────────────────────────────
    # Ciclo de Vida da Folha de Pagamento
    # ──────────────────────────────────────────────────────────

    def criar_ou_atualizar_folha(
        self,
        colaborador_id: int,
        competencia: str,
        periodo_inicio: str,
        periodo_fim: str,
        data_pagamento: Optional[str] = None,
        dias_trabalhados: float = 30.0,
        dias_mes: int = 30,
        horas_divisor: float = 220.0,
        eventos: Optional[List[Dict[str, Any]]] = None,
        observacoes: str = "",
        usuario: str = "Sistema/Administrador",
        folha_id_existente: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cria nova folha ou atualiza existente.
        Bloqueia duplicidade de (colaborador_id, competencia).
        Calcula os valores intermediários e finais, persistindo os itens discriminados.
        """
        colab = self.obter_dados_colaborador(colaborador_id)
        salario_base = float(colab.get("salario_base", 0.0))
        num_dependentes = int(colab.get("total_dependentes", 0))

        # Validação da competência (AAAA-MM)
        comp = competencia.strip()
        partes_comp = comp.split("-")
        if len(partes_comp) != 2 or not (len(partes_comp[0]) == 4 and len(partes_comp[1]) == 2):
            raise FolhaValidacaoException({"competencia": "A competência deve estar no formato AAAA-MM (ex: 2026-10)."})

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        # Checagem de duplicidade
        if folha_id_existente:
            cursor.execute(
                f"SELECT id, situacao FROM folhas_pagamento WHERE colaborador_id = {P} AND competencia = {P} AND id != {P};",
                (colaborador_id, comp, folha_id_existente)
            )
        else:
            cursor.execute(
                f"SELECT id, situacao FROM folhas_pagamento WHERE colaborador_id = {P} AND competencia = {P};",
                (colaborador_id, comp)
            )
        dup = cursor.fetchone()
        if dup:
            conn.close()
            raise FolhaValidacaoException({
                "competencia": f"Já existe uma folha cadastrada para o colaborador {colab['nome_completo']} na competência {comp} (ID #{dup[0]})."
            })

        # Se estamos editando, checa se a folha existente está fechada
        if folha_id_existente:
            cursor.execute(f"SELECT situacao FROM folhas_pagamento WHERE id = {P};", (folha_id_existente,))
            folha_atual = cursor.fetchone()
            if folha_atual and folha_atual[0] == "fechada":
                conn.close()
                raise FolhaBloqueadaException("Esta folha de pagamento já está fechada e não pode ser alterada diretamente.")

        # Obter parâmetros vigentes
        param = self.obter_parametro_vigente()
        param_id = param.get("id")

        # Processar cálculos detalhados
        calc_result = processar_calculo_folha(
            salario_base=salario_base,
            dias_trabalhados=dias_trabalhados,
            dias_mes=dias_mes,
            divisor_horas=horas_divisor,
            eventos_informados=eventos or [],
            numero_dependentes=num_dependentes,
            parametros_config={
                "percentual_noturno": float(param.get("percentual_adicional_noturno", 20.0)),
                "aplicar_reducao_noturna": bool(param.get("aplicar_reducao_noturna", 0)),
                "fator_reducao_noturna": float(param.get("fator_reducao_noturna", 1.142857)),
                "aplicar_inss": bool(param.get("aplicar_inss", 1)),
                "aplicar_irrf": bool(param.get("aplicar_irrf", 1)),
                "aliquota_fgts": float(param.get("aliquota_fgts", 8.0)),
                "teto_inss": float(param.get("teto_inss", 8157.41)),
                "deducao_dependente_irrf": float(param.get("deducao_dependente_irrf", 189.59))
            }
        )

        resumo = calc_result["resumo"]
        itens = calc_result["itens"]
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Transação segura
        try:
            if folha_id_existente:
                folha_id = folha_id_existente
                cursor.execute(f"""
                    UPDATE folhas_pagamento SET
                        periodo_inicio = {P},
                        periodo_fim = {P},
                        data_pagamento = {P},
                        dias_trabalhados = {P},
                        dias_mes = {P},
                        horas_mensais_divisor = {P},
                        salario_base_contratual = {P},
                        salario_base_proporcional = {P},
                        total_proventos = {P},
                        total_descontos = {P},
                        salario_liquido = {P},
                        base_inss = {P},
                        base_fgts = {P},
                        valor_fgts_informativo = {P},
                        base_irrf = {P},
                        situacao = 'calculada',
                        observacoes = {P},
                        parametro_id = {P},
                        atualizado_por = {P},
                        atualizado_em = {P}
                    WHERE id = {P};
                """, (
                    periodo_inicio, periodo_fim, data_pagamento,
                    resumo["dias_trabalhados"], resumo["dias_mes"], resumo["divisor_horas"],
                    resumo["salario_base_contratual"], resumo["salario_base_proporcional"],
                    resumo["total_proventos"], resumo["total_descontos"], resumo["salario_liquido"],
                    resumo["base_inss"], resumo["base_fgts"], resumo["valor_fgts_informativo"],
                    resumo["base_irrf"], observacoes, param_id, usuario, agora,
                    folha_id
                ))
                # Remove itens anteriores para recriar
                cursor.execute(f"DELETE FROM folha_itens WHERE folha_id = {P};", (folha_id,))

                # Auditoria
                cursor.execute(f"""
                    INSERT INTO folha_historico (folha_id, data_hora, acao, descricao, usuario_responsavel)
                    VALUES ({P}, {P}, 'RECALCULO', 'Folha recalculada com novos lançamentos.', {P});
                """, (folha_id, agora, usuario))

            else:
                sql_pg = f"""
                    INSERT INTO folhas_pagamento (
                        colaborador_id, competencia, periodo_inicio, periodo_fim, data_pagamento,
                        dias_trabalhados, dias_mes, horas_mensais_divisor, salario_base_contratual,
                        salario_base_proporcional, total_proventos, total_descontos, salario_liquido,
                        base_inss, base_fgts, valor_fgts_informativo, base_irrf, situacao, observacoes,
                        parametro_id, criado_por, criado_em, atualizado_por, atualizado_em
                    ) VALUES (
                        {P},{P},{P},{P},{P},
                        {P},{P},{P},{P},
                        {P},{P},{P},{P},{P},
                        {P},{P},{P},'calculada',{P},
                        {P},{P},{P},{P},{P}
                    ) RETURNING id;
                """
                sql_sqlite = f"""
                    INSERT INTO folhas_pagamento (
                        colaborador_id, competencia, periodo_inicio, periodo_fim, data_pagamento,
                        dias_trabalhados, dias_mes, horas_mensais_divisor, salario_base_contratual,
                        salario_base_proporcional, total_proventos, total_descontos, salario_liquido,
                        base_inss, base_fgts, valor_fgts_informativo, base_irrf, situacao, observacoes,
                        parametro_id, criado_por, criado_em, atualizado_por, atualizado_em
                    ) VALUES (
                        {P},{P},{P},{P},{P},
                        {P},{P},{P},{P},
                        {P},{P},{P},{P},{P},
                        {P},{P},{P},'calculada',{P},
                        {P},{P},{P},{P},{P}
                    );
                """
                params_insert = (
                    colaborador_id, comp, periodo_inicio, periodo_fim, data_pagamento,
                    resumo["dias_trabalhados"], resumo["dias_mes"], resumo["divisor_horas"],
                    resumo["salario_base_contratual"], resumo["salario_base_proporcional"],
                    resumo["total_proventos"], resumo["total_descontos"], resumo["salario_liquido"],
                    resumo["base_inss"], resumo["base_fgts"], resumo["valor_fgts_informativo"],
                    resumo["base_irrf"], observacoes, param_id, usuario, agora, usuario, agora
                )
                folha_id = self._insert_id(cursor, conn, sql_pg, sql_sqlite, params_insert)

                # Auditoria
                cursor.execute(f"""
                    INSERT INTO folha_historico (folha_id, data_hora, acao, descricao, usuario_responsavel)
                    VALUES ({P}, {P}, 'CRIACAO', 'Folha de pagamento criada e calculada com sucesso.', {P});
                """, (folha_id, agora, usuario))

            # Inserir itens discriminados
            for it in itens:
                cursor.execute(f"""
                    INSERT INTO folha_itens (
                        folha_id, codigo_evento, descricao, tipo, referencia,
                        unidade_referencia, valor_unitario, valor_total, origem,
                        memoria_calculo, criado_em
                    ) VALUES ({P}, {P}, {P}, {P}, {P}, {P}, {P}, {P}, {P}, {P}, {P});
                """, (
                    folha_id, it["codigo_evento"], it["descricao"], it["tipo"],
                    it["referencia"], it["unidade_referencia"], it["valor_unitario"],
                    it["valor_total"], it["origem"], it["memoria_calculo"], agora
                ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

        conn.close()
        return self.obter_folha_por_id(folha_id)

    # ──────────────────────────────────────────────────────────
    # Consulta e Detalhamento da Folha
    # ──────────────────────────────────────────────────────────

    def obter_folha_por_id(self, folha_id: int) -> Dict[str, Any]:
        """Retorna a folha completa com colaborador, itens e histórico de auditoria."""
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT 
                f.*,
                c.nome_completo as colaborador_nome,
                c.matricula as colaborador_matricula,
                c.cpf as colaborador_cpf,
                c.cargo as colaborador_cargo,
                c.setor as colaborador_setor,
                c.data_admissao as colaborador_data_admissao,
                c.situacao as colaborador_situacao,
                p.descricao as parametro_descricao
            FROM folhas_pagamento f
            JOIN colaboradores c ON c.id = f.colaborador_id
            LEFT JOIN folha_parametros p ON p.id = f.parametro_id
            WHERE f.id = {P};
        """, (folha_id,))
        folha = self._fetchone(cursor)
        if not folha:
            conn.close()
            raise FolhaNaoEncontradaException(f"Folha de pagamento #{folha_id} não encontrada.")

        # Buscar itens da folha ordenados por tipo (provento primeiro, depois desconto, depois informativo)
        cursor.execute(f"""
            SELECT * FROM folha_itens 
            WHERE folha_id = {P}
            ORDER BY 
                CASE tipo 
                    WHEN 'provento' THEN 1 
                    WHEN 'desconto' THEN 2 
                    ELSE 3 
                END, codigo_evento ASC;
        """, (folha_id,))
        folha["itens"] = self._fetchall(cursor)

        # Buscar histórico de auditoria
        cursor.execute(f"""
            SELECT * FROM folha_historico 
            WHERE folha_id = {P}
            ORDER BY id ASC;
        """, (folha_id,))
        folha["historico"] = self._fetchall(cursor)

        conn.close()
        return folha

    def listar_folhas(
        self,
        competencia: Optional[str] = None,
        colaborador_id: Optional[int] = None,
        situacao: Optional[str] = None,
        setor: Optional[str] = None,
        termo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista as folhas de pagamento com filtros de competência, funcionário e situação."""
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        sql = """
            SELECT 
                f.id,
                f.colaborador_id,
                f.competencia,
                f.periodo_inicio,
                f.periodo_fim,
                f.data_pagamento,
                f.salario_base_contratual,
                f.salario_base_proporcional,
                f.total_proventos,
                f.total_descontos,
                f.salario_liquido,
                f.situacao,
                f.criado_por,
                f.criado_em,
                f.fechado_por,
                f.fechado_em,
                c.nome_completo as colaborador_nome,
                c.matricula as colaborador_matricula,
                c.cpf as colaborador_cpf,
                c.cargo as colaborador_cargo,
                c.setor as colaborador_setor
            FROM folhas_pagamento f
            JOIN colaboradores c ON c.id = f.colaborador_id
            WHERE 1=1
        """
        params = []

        if competencia:
            sql += f" AND f.competencia = {P}"
            params.append(competencia.strip())

        if colaborador_id:
            sql += f" AND f.colaborador_id = {P}"
            params.append(int(colaborador_id))

        if situacao and situacao != "todos":
            sql += f" AND f.situacao = {P}"
            params.append(situacao.strip())

        if setor:
            sql += f" AND c.setor = {P}"
            params.append(setor.strip())

        if termo:
            t = f"%{termo.strip()}%"
            sql += f" AND (c.nome_completo LIKE {P} OR c.cpf LIKE {P} OR c.matricula LIKE {P})"
            params.extend([t, t, t])

        sql += " ORDER BY f.competencia DESC, c.nome_completo ASC;"

        cursor.execute(sql, tuple(params))
        folhas = self._fetchall(cursor)
        conn.close()
        return folhas

    # ──────────────────────────────────────────────────────────
    # Fechamento e Reabertura de Folha (Auditoria e Controle)
    # ──────────────────────────────────────────────────────────

    def fechar_folha(self, folha_id: int, usuario: str = "Sistema/Administrador") -> Dict[str, Any]:
        """
        Fecha a folha de pagamento, impedindo modificações posteriores
        sem reabertura auditada.
        """
        folha = self.obter_folha_por_id(folha_id)
        if folha["situacao"] == "fechada":
            raise FolhaBloqueadaException("A folha de pagamento já se encontra fechada.")

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(f"""
            UPDATE folhas_pagamento SET
                situacao = 'fechada',
                fechado_por = {P},
                fechado_em = {P},
                atualizado_por = {P},
                atualizado_em = {P}
            WHERE id = {P};
        """, (usuario, agora, usuario, agora, folha_id))

        cursor.execute(f"""
            INSERT INTO folha_historico (folha_id, data_hora, acao, descricao, usuario_responsavel)
            VALUES ({P}, {P}, 'FECHAMENTO', 'Folha fechada e homologada para pagamento.', {P});
        """, (folha_id, agora, usuario))

        conn.commit()
        conn.close()
        return self.obter_folha_por_id(folha_id)

    def reabrir_folha(self, folha_id: int, motivo: str, usuario: str = "Sistema/Administrador") -> Dict[str, Any]:
        """
        Reabre uma folha fechada mediante registro obrigatório do motivo na auditoria.
        """
        if not motivo or len(motivo.strip()) < 5:
            raise FolhaValidacaoException({"motivo": "Informe um motivo detalhado para reabertura da folha."})

        folha = self.obter_folha_por_id(folha_id)
        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(f"""
            UPDATE folhas_pagamento SET
                situacao = 'calculada',
                atualizado_por = {P},
                atualizado_em = {P}
            WHERE id = {P};
        """, (usuario, agora, folha_id))

        desc = f"Folha reaberta pelo operador. Motivo informado: {motivo.strip()}"
        cursor.execute(f"""
            INSERT INTO folha_historico (folha_id, data_hora, acao, descricao, usuario_responsavel)
            VALUES ({P}, {P}, 'REABERTURA', {P}, {P});
        """, (folha_id, agora, desc, usuario))

        conn.commit()
        conn.close()
        return self.obter_folha_por_id(folha_id)

    def cancelar_folha(self, folha_id: int, usuario: str = "Sistema/Administrador") -> bool:
        """Exclui ou cancela folha se não estiver fechada."""
        folha = self.obter_folha_por_id(folha_id)
        if folha["situacao"] == "fechada":
            raise FolhaBloqueadaException("Folhas já fechadas não podem ser canceladas sem reabertura prévia.")

        P = self._ph()
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM folhas_pagamento WHERE id = {P};", (folha_id,))
        conn.commit()
        conn.close()
        return True

