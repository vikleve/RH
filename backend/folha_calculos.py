"""
Camada de Cálculos da Folha de Pagamento — RH / DP
Módulo desacoplado, testável e estritamente parametrizado.
Atende a RF de Cálculos Trabalhistas:
- Proporcionalidade de salário por dias ou horas
- Valor da hora normal
- Horas extras (50%, 100% ou percentuais arbitrários)
- Adicional noturno com jornada normal ou ficta reduzida
- Descontos de faltas e atrasos
- DSR sobre variáveis (configurável)
- Encargos legais parametrizados (INSS e IRRF por faixas vigentes e dependentes)
- Totalização precisa com arredondamento monetário (ROUND_HALF_UP)
- Memória de cálculo detalhada para conferência por profissional de RH
"""
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple


def _to_decimal(val: Any) -> Decimal:
    """Converte com segurança qualquer valor numérico ou string para Decimal."""
    if val is None or val == "":
        return Decimal("0.00")
    if isinstance(val, Decimal):
        return val
    try:
        # Trata formato brasileiro com vírgula se necessário
        str_val = str(val).strip().replace("R$", "").strip()
        if "," in str_val and "." not in str_val:
            str_val = str_val.replace(",", ".")
        elif "," in str_val and "." in str_val:
            # ex: 1.234,56
            str_val = str_val.replace(".", "").replace(",", ".")
        return Decimal(str_val)
    except Exception:
        return Decimal("0.00")


def arredondar_moeda(val: Any) -> Decimal:
    """Arredonda para 2 casas decimais no padrão financeiro (ROUND_HALF_UP)."""
    d = _to_decimal(val)
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def formatar_moeda(val: Any) -> str:
    """Formata Decimal como string monetária R$ 0.000,00."""
    d = arredondar_moeda(val)
    # Formata com separador de milhar e decimal
    val_str = f"{d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {val_str}"


# ─────────────────────────────────────────────────────────────────────────────
# Parâmetros Padrão Configuráveis (Vigência 2026 / CLT Parametrizada)
# Sinalizados para validação do profissional responsável pela folha.
# ─────────────────────────────────────────────────────────────────────────────

TABELA_INSS_PADRAO_2026 = [
    # (faixa_min, faixa_max, aliquota_percentual)
    (Decimal("0.00"), Decimal("1518.00"), Decimal("7.5")),
    (Decimal("1518.01"), Decimal("2793.88"), Decimal("9.0")),
    (Decimal("2793.89"), Decimal("4190.83"), Decimal("12.0")),
    (Decimal("4190.84"), Decimal("8157.41"), Decimal("14.0")),
]
TETO_INSS_PADRAO_2026 = Decimal("8157.41")

TABELA_IRRF_PADRAO_2026 = [
    # (faixa_min, faixa_max, aliquota_percentual, parcela_a_deduzir)
    (Decimal("0.00"), Decimal("2259.20"), Decimal("0.0"), Decimal("0.00")),
    (Decimal("2259.21"), Decimal("2826.65"), Decimal("7.5"), Decimal("169.44")),
    (Decimal("2826.66"), Decimal("3751.05"), Decimal("15.0"), Decimal("381.44")),
    (Decimal("3751.06"), Decimal("4664.68"), Decimal("22.5"), Decimal("662.77")),
    (Decimal("4664.69"), None, Decimal("27.5"), Decimal("896.00")),
]
DEDUCAO_DEPENDENTE_IRRF_PADRAO = Decimal("189.59")
ALIQUOTA_FGTS_PADRAO = Decimal("8.0")  # Informativo


# ─────────────────────────────────────────────────────────────────────────────
# 1. Salário-Base Proporcional
# ─────────────────────────────────────────────────────────────────────────────

def calcular_salario_proporcional(
    salario_base: Any,
    dias_trabalhados: Any = 30,
    dias_mes: int = 30
) -> Tuple[Decimal, str]:
    """
    Calcula o salário-base proporcional aos dias trabalhados no mês comercial ou civil.
    Fórmula: (salário_base / dias_mes) * dias_trabalhados
    """
    sb = _to_decimal(salario_base)
    dt = _to_decimal(dias_trabalhados)
    dm = Decimal(str(dias_mes if dias_mes > 0 else 30))

    if sb <= Decimal("0.00") or dt <= Decimal("0.00"):
        return Decimal("0.00"), f"Salário ou dias zerados: R$ {sb} / {dm} x {dt} dias"

    if dt >= dm:
        valor = arredondar_moeda(sb)
        memoria = f"Salário integral: R$ {sb:,.2f} ({dm}/{dm} dias)".replace(".", ",")
        return valor, memoria

    valor_dia = sb / dm
    total = arredondar_moeda(valor_dia * dt)
    memoria = (
        f"R$ {sb:,.2f} / {dm} dias = R$ {valor_dia:,.4f}/dia x {dt} dias = R$ {total:,.2f}"
    ).replace(".", ",")
    return total, memoria


# ─────────────────────────────────────────────────────────────────────────────
# 2. Valor da Hora Normal
# ─────────────────────────────────────────────────────────────────────────────

def calcular_valor_hora_normal(
    salario_base: Any,
    divisor_horas: Any = 220.0
) -> Tuple[Decimal, str]:
    """
    Calcula o valor da hora normal do colaborador com base no salário e divisor mensal.
    Fórmula: salário_base / divisor_horas
    """
    sb = _to_decimal(salario_base)
    div = _to_decimal(divisor_horas)
    if div <= Decimal("0.00"):
        div = Decimal("220.0")

    if sb <= Decimal("0.00"):
        return Decimal("0.00"), f"Salário base zerado / divisor {div}h"

    # Hora normal com 4 casas internas para precisão dos cálculos de hora extra
    vh = (sb / div).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    memoria = f"R$ {sb:,.2f} / {div}h = R$ {vh:,.4f}/hora".replace(".", ",")
    return vh, memoria


# ─────────────────────────────────────────────────────────────────────────────
# 3. Horas Extras com Percentuais Arbitrários (50%, 100%, etc.)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_horas_extras(
    valor_hora_normal: Any,
    quantidade_horas: Any,
    percentual_adicional: Any = 50.0
) -> Tuple[Decimal, Decimal, str]:
    """
    Calcula o total de horas extras com percentual configurável.
    Fórmula: valor_hora_normal * (1 + percentual / 100) * quantidade_horas
    Retorna: (total_arredondado, valor_hora_extra_unitaria, memoria_calculo)
    """
    vh = _to_decimal(valor_hora_normal)
    qtd = _to_decimal(quantidade_horas)
    perc = _to_decimal(percentual_adicional)

    if vh <= Decimal("0.00") or qtd <= Decimal("0.00"):
        return Decimal("0.00"), Decimal("0.00"), "0 hora(s) extra(s) lançada(s)"

    fator = Decimal("1.00") + (perc / Decimal("100.00"))
    vh_extra = (vh * fator).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    total = arredondar_moeda(vh_extra * qtd)

    memoria = (
        f"{qtd}h x R$ {vh_extra:,.2f} (Hora normal R$ {vh:,.2f} + {perc}%): total R$ {total:,.2f}"
    ).replace(".", ",")
    return total, arredondar_moeda(vh_extra), memoria


# ─────────────────────────────────────────────────────────────────────────────
# 4. Adicional Noturno com Percentual e Horário Configuráveis
# ─────────────────────────────────────────────────────────────────────────────

def calcular_adicional_noturno(
    valor_hora_normal: Any,
    quantidade_horas: Any,
    percentual_adicional: Any = 20.0,
    aplicar_reducao_ficta: bool = False,
    fator_reducao: Any = 1.142857
) -> Tuple[Decimal, Decimal, str]:
    """
    Calcula o adicional noturno.
    Fórmula padrão: valor_hora_normal * (percentual / 100) * horas_computadas
    Se aplicar_reducao_ficta=True: horas_computadas = quantidade_horas * fator_reducao (CLT 52m30s: 60/52.5 = 1.142857)
    Retorna: (total_arredondado, valor_adicional_hora, memoria_calculo)
    """
    vh = _to_decimal(valor_hora_normal)
    qtd = _to_decimal(quantidade_horas)
    perc = _to_decimal(percentual_adicional)
    fator = _to_decimal(fator_reducao) if aplicar_reducao_ficta else Decimal("1.0")

    if vh <= Decimal("0.00") or qtd <= Decimal("0.00"):
        return Decimal("0.00"), Decimal("0.00"), "0 hora(s) noturna(s) lançada(s)"

    horas_computadas = qtd * fator
    valor_adic_hora = (vh * (perc / Decimal("100.00"))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    total = arredondar_moeda(valor_adic_hora * horas_computadas)

    obs_reducao = f" (com redução ficta x {fator:.4f} = {horas_computadas:.2f}h)" if aplicar_reducao_ficta else ""
    memoria = (
        f"{qtd}h{obs_reducao} x R$ {valor_adic_hora:,.2f} (Adicional {perc}% de R$ {vh:,.2f}): total R$ {total:,.2f}"
    ).replace(".", ",")

    return total, arredondar_moeda(valor_adic_hora), memoria


# ─────────────────────────────────────────────────────────────────────────────
# 5. Desconto de Faltas e Atrasos
# ─────────────────────────────────────────────────────────────────────────────

def calcular_desconto_faltas(
    salario_base: Any,
    dias_falta: Any,
    dias_mes: int = 30
) -> Tuple[Decimal, str]:
    """
    Calcula desconto de faltas integrais em dias.
    Fórmula: (salário_base / dias_mes) * dias_falta
    """
    sb = _to_decimal(salario_base)
    dias = _to_decimal(dias_falta)
    dm = Decimal(str(dias_mes if dias_mes > 0 else 30))

    if sb <= Decimal("0.00") or dias <= Decimal("0.00"):
        return Decimal("0.00"), "Sem faltas a descontar"

    valor_dia = sb / dm
    total = arredondar_moeda(valor_dia * dias)
    memoria = (
        f"{dias} dia(s) de falta x R$ {valor_dia:,.2f}/dia (R$ {sb:,.2f} / {dm}): total R$ {total:,.2f}"
    ).replace(".", ",")
    return total, memoria


def calcular_desconto_atrasos(
    valor_hora_normal: Any,
    horas_atraso: Any
) -> Tuple[Decimal, str]:
    """
    Calcula o desconto de atrasos ou saídas antecipadas em horas decimais.
    Fórmula: valor_hora_normal * horas_atraso
    """
    vh = _to_decimal(valor_hora_normal)
    horas = _to_decimal(horas_atraso)

    if vh <= Decimal("0.00") or horas <= Decimal("0.00"):
        return Decimal("0.00"), "Sem atrasos a descontar"

    total = arredondar_moeda(vh * horas)
    memoria = (
        f"{horas}h de atraso x R$ {vh:,.2f}/hora normal: total R$ {total:,.2f}"
    ).replace(".", ",")
    return total, memoria


def calcular_dsr_sobre_variaveis(
    total_variaveis: Any,
    dias_uteis: int,
    domingos_feriados: int
) -> Tuple[Decimal, str]:
    """
    Calcula o Descanso Semanal Remunerado (DSR) sobre variáveis (Horas Extras, Adicional Noturno).
    Fórmula: (total_variaveis / dias_uteis) * domingos_feriados
    Parametrizado conforme o mês da competência.
    """
    tv = _to_decimal(total_variaveis)
    if tv <= Decimal("0.00") or dias_uteis <= 0 or domingos_feriados <= 0:
        return Decimal("0.00"), "DSR não incidente ou variáveis zeradas"

    du = Decimal(str(dias_uteis))
    df = Decimal(str(domingos_feriados))
    valor_dsr = arredondar_moeda((tv / du) * df)

    memoria = (
        f"DSR: (R$ {tv:,.2f} / {du} dias úteis) x {df} domingos/feriados = R$ {valor_dsr:,.2f}"
    ).replace(".", ",")
    return valor_dsr, memoria


# ─────────────────────────────────────────────────────────────────────────────
# 6. Descontos Previdenciários e Fiscais Parametrizados (INSS e IRRF)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_inss_progressivo(
    base_inss: Any,
    tabela_faixas: Optional[List[Tuple[Decimal, Decimal, Decimal]]] = None,
    teto_maximo: Optional[Decimal] = None
) -> Tuple[Decimal, Decimal, str, List[Dict[str, Any]]]:
    """
    Calcula o INSS progressivo faixa a faixa (Emenda Constitucional 103/2019).
    Totalmente parametrizado, sem hardcode rígido não validado.
    Retorna: (total_inss, aliquota_efetiva_percentual, memoria_calculo, detalhes_faixas)
    """
    base = _to_decimal(base_inss)
    if base <= Decimal("0.00"):
        return Decimal("0.00"), Decimal("0.00"), "Base de INSS zerada", []

    faixas = tabela_faixas if tabela_faixas is not None else TABELA_INSS_PADRAO_2026
    teto = teto_maximo if teto_maximo is not None else TETO_INSS_PADRAO_2026

    base_tributavel = min(base, teto)
    total_inss = Decimal("0.00")
    detalhes = []
    linhas_memoria = []

    for idx, (f_min, f_max, aliq) in enumerate(faixas, start=1):
        if base_tributavel < f_min:
            break

        limite_superior = min(base_tributavel, f_max)
        valor_tributavel_faixa = limite_superior - f_min
        if idx == 1:
            valor_tributavel_faixa = limite_superior  # Primeira faixa parte de 0

        if valor_tributavel_faixa > Decimal("0.00"):
            desc_faixa = arredondar_moeda(valor_tributavel_faixa * (aliq / Decimal("100.00")))
            total_inss += desc_faixa
            detalhes.append({
                "faixa": idx,
                "de": float(f_min),
                "ate": float(limite_superior),
                "base_faixa": float(valor_tributavel_faixa),
                "aliquota": float(aliq),
                "desconto": float(desc_faixa)
            })
            linhas_memoria.append(
                f"Faixa {idx} ({aliq}% sobre R$ {valor_tributavel_faixa:,.2f}) = R$ {desc_faixa:,.2f}"
            )

    total_inss = arredondar_moeda(total_inss)
    aliq_efetiva = Decimal("0.00")
    if base > Decimal("0.00"):
        aliq_efetiva = ((total_inss / base) * Decimal("100.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    memoria = " | ".join(linhas_memoria) + f" | Total INSS: R$ {total_inss:,.2f} (Efetiva: {aliq_efetiva}%)"
    memoria = memoria.replace(".", ",")
    return total_inss, aliq_efetiva, memoria, detalhes


def calcular_irrf_progressivo(
    base_bruta_irrf: Any,
    desconto_inss: Any,
    numero_dependentes: int = 0,
    deducao_por_dependente: Optional[Decimal] = None,
    outras_deducoes: Any = 0,
    tabela_faixas: Optional[List[Tuple[Decimal, Optional[Decimal], Decimal, Decimal]]] = None
) -> Tuple[Decimal, Decimal, str]:
    """
    Calcula o IRRF (Imposto de Renda Retido na Fonte) conforme faixas vigentes e dependentes.
    Fórmula: Base Tributável = Base Bruta - INSS - (Dependentes * Dedução) - Outras Deduções
             IRRF = (Base Tributável * Alíquota) - Parcela a Deduzir
    Retorna: (total_irrf, base_tributavel, memoria_calculo)
    """
    bruta = _to_decimal(base_bruta_irrf)
    inss = _to_decimal(desconto_inss)
    deducao_dep_unit = deducao_por_dependente if deducao_por_dependente is not None else DEDUCAO_DEPENDENTE_IRRF_PADRAO
    total_deducao_dep = Decimal(str(max(0, numero_dependentes))) * deducao_dep_unit
    outras = _to_decimal(outras_deducoes)

    base_tributavel = bruta - inss - total_deducao_dep - outras
    if base_tributavel <= Decimal("0.00"):
        return Decimal("0.00"), Decimal("0.00"), "Base de IRRF isenta ou zerada após deduções legais"

    faixas = tabela_faixas if tabela_faixas is not None else TABELA_IRRF_PADRAO_2026
    aliq_aplicada = Decimal("0.00")
    parcela_deduzir = Decimal("0.00")

    for f_min, f_max, aliq, deduc in faixas:
        if f_max is None or base_tributavel <= f_max:
            aliq_aplicada = aliq
            parcela_deduzir = deduc
            break

    if aliq_aplicada == Decimal("0.00"):
        memoria = f"Base R$ {base_tributavel:,.2f} na faixa de isenção (0%)".replace(".", ",")
        return Decimal("0.00"), arredondar_moeda(base_tributavel), memoria

    imposto_bruto = base_tributavel * (aliq_aplicada / Decimal("100.00"))
    total_irrf = arredondar_moeda(imposto_bruto - parcela_deduzir)
    if total_irrf < Decimal("0.00"):
        total_irrf = Decimal("0.00")

    memoria = (
        f"Base IRRF R$ {base_tributavel:,.2f} [Bruto R$ {bruta:,.2f} - INSS R$ {inss:,.2f} "
        f"- {numero_dependentes} dep. R$ {total_deducao_dep:,.2f}] x {aliq_aplicada}% "
        f"- Parcela a deduzir R$ {parcela_deduzir:,.2f} = R$ {total_irrf:,.2f}"
    ).replace(".", ",")

    return total_irrf, arredondar_moeda(base_tributavel), memoria


# ─────────────────────────────────────────────────────────────────────────────
# 7. Motor de Consolidação de Eventos da Folha
# ─────────────────────────────────────────────────────────────────────────────

def processar_calculo_folha(
    salario_base: Any,
    dias_trabalhados: Any = 30,
    dias_mes: int = 30,
    divisor_horas: Any = 220.0,
    eventos_informados: Optional[List[Dict[str, Any]]] = None,
    numero_dependentes: int = 0,
    parametros_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Processa a folha de pagamento completa garantindo:
    1. Separação de cálculo e totalização estrita
    2. Não duplicidade de rubricas automáticas
    3. Exibição detalhada de memória de cálculo com valores intermediários
    4. Proventos, Descontos, e Salário Líquido = Proventos - Descontos
    """
    params = parametros_config or {}
    sb = _to_decimal(salario_base)
    dm = int(dias_mes) if int(dias_mes) > 0 else 30
    dt = _to_decimal(dias_trabalhados) if dias_trabalhados is not None else Decimal(str(dm))
    div_h = _to_decimal(divisor_horas) if divisor_horas else Decimal("220.0")

    # 1. Salário-Base Proporcional e Valor da Hora Normal
    salario_prop, mem_salario_prop = calcular_salario_proporcional(sb, dt, dm)
    vh_normal, mem_vh = calcular_valor_hora_normal(sb, div_h)

    itens_consolidados: List[Dict[str, Any]] = []
    codigos_processados = set()

    def adicionar_item(codigo: str, descricao: str, tipo: str, referencia: Any,
                       unidade: str, valor_unit: Any, valor_total: Any,
                       memoria: str, origem: str = "sistema"):
        """Adiciona item assegurando que não haja duplicidade de evento idêntico."""
        chave = (codigo, tipo)
        if chave in codigos_processados:
            raise ValueError(f"Evento duplicado na mesma folha: {codigo} ({descricao}). Não é permitido duplicar rubricas.")
        codigos_processados.add(chave)

        val_total_dec = arredondar_moeda(valor_total)
        itens_consolidados.append({
            "codigo_evento": codigo,
            "descricao": descricao,
            "tipo": tipo,  # 'provento', 'desconto', 'informativo'
            "referencia": float(_to_decimal(referencia)),
            "unidade_referencia": unidade,
            "valor_unitario": float(arredondar_moeda(valor_unit)),
            "valor_total": float(val_total_dec),
            "origem": origem,
            "memoria_calculo": memoria
        })

    # Item principal obrigatório: Salário-base proporcional
    adicionar_item(
        codigo="001",
        descricao="Salário Base Mensal",
        tipo="provento",
        referencia=dt,
        unidade="dias",
        valor_unit=sb / Decimal(str(dm)),
        valor_total=salario_prop,
        memoria=mem_salario_prop,
        origem="sistema"
    )

    # Processar eventos informados
    eventos = eventos_informados or []
    total_horas_extras = Decimal("0.00")
    total_adic_noturno = Decimal("0.00")

    for ev in eventos:
        cod = str(ev.get("codigo", "") or ev.get("codigo_evento", "")).strip().upper()
        tipo = str(ev.get("tipo", "provento")).strip().lower()
        desc = ev.get("descricao", f"Evento {cod}")
        qtd = _to_decimal(ev.get("quantidade") or ev.get("referencia") or 0)
        perc = _to_decimal(ev.get("percentual") or 0)
        val_manual = _to_decimal(ev.get("valor_total") or 0)

        # Tratar tipos especiais conhecidos
        if cod in ("HE50", "HE_50", "101"):
            p = perc if perc > Decimal("0.00") else Decimal("50.0")
            tot_he, vh_extra, mem_he = calcular_horas_extras(vh_normal, qtd, p)
            adicionar_item("101", f"Horas Extras {p}%", "provento", qtd, "horas", vh_extra, tot_he, mem_he, "calculado")
            total_horas_extras += tot_he

        elif cod in ("HE100", "HE_100", "102"):
            p = perc if perc > Decimal("0.00") else Decimal("100.0")
            tot_he, vh_extra, mem_he = calcular_horas_extras(vh_normal, qtd, p)
            adicionar_item("102", f"Horas Extras {p}%", "provento", qtd, "horas", vh_extra, tot_he, mem_he, "calculado")
            total_horas_extras += tot_he

        elif cod in ("NOTURNO", "ADIC_NOTURNO", "103"):
            p = perc if perc > Decimal("0.00") else Decimal(str(params.get("percentual_noturno", 20.0)))
            reducao = bool(params.get("aplicar_reducao_noturna", False))
            fator_red = params.get("fator_reducao_noturna", 1.142857)
            tot_not, vh_not, mem_not = calcular_adicional_noturno(vh_normal, qtd, p, reducao, fator_red)
            adicionar_item("103", f"Adicional Noturno {p}%", "provento", qtd, "horas", vh_not, tot_not, mem_not, "calculado")
            total_adic_noturno += tot_not

        elif cod in ("FALTA", "FALTA_DIAS", "201"):
            tot_falta, mem_falta = calcular_desconto_faltas(sb, qtd, dm)
            adicionar_item("201", "Faltas Integrais", "desconto", qtd, "dias", sb / Decimal(str(dm)), tot_falta, mem_falta, "calculado")

        elif cod in ("ATRASO", "ATRASO_HORAS", "202"):
            tot_atraso, mem_atraso = calcular_desconto_atrasos(vh_normal, qtd)
            adicionar_item("202", "Atrasos / Saídas", "desconto", qtd, "horas", vh_normal, tot_atraso, mem_atraso, "calculado")

        else:
            # Proventos ou Descontos genéricos informados pelo usuário
            unit = _to_decimal(ev.get("valor_unitario") or (val_manual / qtd if qtd > 0 else val_manual))
            unid_ref = ev.get("unidade_referencia") or ("horas" if "HORA" in desc.upper() else "un")
            mem = ev.get("memoria_calculo") or f"Lançamento {tipo}: {desc} = R$ {val_manual:,.2f}".replace(".", ",")
            adicionar_item(
                codigo=cod or f"EV_{len(itens_consolidados)+1}",
                descricao=desc,
                tipo=tipo if tipo in ("provento", "desconto", "informativo") else "provento",
                referencia=qtd,
                unidade=unid_ref,
                valor_unit=unit,
                valor_total=val_manual,
                memoria=mem,
                origem="manual"
            )

    # DSR sobre variáveis (se configurado pelo usuário nos parâmetros)
    dias_uteis = int(params.get("dias_uteis", 0))
    domingos_feriados = int(params.get("domingos_feriados", 0))
    if dias_uteis > 0 and domingos_feriados > 0 and (total_horas_extras + total_adic_noturno) > Decimal("0.00"):
        val_dsr, mem_dsr = calcular_dsr_sobre_variaveis(
            total_horas_extras + total_adic_noturno, dias_uteis, domingos_feriados
        )
        if val_dsr > Decimal("0.00"):
            adicionar_item("105", "DSR sobre Variáveis", "provento", domingos_feriados, "dias", val_dsr / Decimal(str(domingos_feriados)), val_dsr, mem_dsr, "calculado")

    # ─────────────────────────────────────────────────────────────────────────
    # Subtotal de Proventos e Bases de Encargos
    # ─────────────────────────────────────────────────────────────────────────
    total_proventos_brutos = Decimal("0.00")
    for it in itens_consolidados:
        if it["tipo"] == "provento":
            total_proventos_brutos += _to_decimal(it["valor_total"])

    # Base de INSS (Proventos que incidem INSS - Faltas descontadas da base)
    # Deduz faltas da base de cálculo previdenciária
    desconto_faltas = Decimal("0.00")
    for it in itens_consolidados:
        if it["codigo_evento"] in ("201", "202") and it["tipo"] == "desconto":
            desconto_faltas += _to_decimal(it["valor_total"])

    base_inss = max(Decimal("0.00"), total_proventos_brutos - desconto_faltas)

    # Cálculo do INSS
    tabela_inss = params.get("tabela_inss")
    teto_inss = _to_decimal(params.get("teto_inss")) if params.get("teto_inss") else None
    val_inss, aliq_inss, mem_inss, _ = calcular_inss_progressivo(base_inss, tabela_inss, teto_inss)

    if val_inss > Decimal("0.00") and params.get("aplicar_inss", True):
        adicionar_item("501", "INSS Retido", "desconto", aliq_inss, "%", base_inss, val_inss, mem_inss, "calculado")

    # Cálculo do IRRF
    tabela_irrf = params.get("tabela_irrf")
    deducao_dep = _to_decimal(params.get("deducao_dependente_irrf")) if params.get("deducao_dependente_irrf") else None
    val_irrf, base_irrf, mem_irrf = calcular_irrf_progressivo(
        base_bruta_irrf=base_inss,
        desconto_inss=val_inss if params.get("aplicar_inss", True) else Decimal("0.00"),
        numero_dependentes=numero_dependentes,
        deducao_por_dependente=deducao_dep,
        outras_deducoes=Decimal("0.00"),
        tabela_faixas=tabela_irrf
    )

    if val_irrf > Decimal("0.00") and params.get("aplicar_irrf", True):
        adicionar_item("502", "IRRF Retido na Fonte", "desconto", numero_dependentes, "dep", base_irrf, val_irrf, mem_irrf, "calculado")

    # Item Informativo: FGTS do Mês
    aliquota_fgts = _to_decimal(params.get("aliquota_fgts", ALIQUOTA_FGTS_PADRAO))
    valor_fgts = arredondar_moeda(base_inss * (aliquota_fgts / Decimal("100.00")))
    adicionar_item(
        codigo="901",
        descricao="FGTS do Mês (Depósito da Empresa)",
        tipo="informativo",
        referencia=aliquota_fgts,
        unidade="%",
        valor_unit=base_inss,
        valor_total=valor_fgts,
        memoria=f"Base FGTS R$ {base_inss:,.2f} x {aliquota_fgts}% = R$ {valor_fgts:,.2f} (não descontado do colaborador)".replace(".", ","),
        origem="calculado"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Totalização Final
    # ─────────────────────────────────────────────────────────────────────────
    total_proventos = Decimal("0.00")
    total_descontos = Decimal("0.00")

    for it in itens_consolidados:
        if it["tipo"] == "provento":
            total_proventos += _to_decimal(it["valor_total"])
        elif it["tipo"] == "desconto":
            total_descontos += _to_decimal(it["valor_total"])

    total_proventos = arredondar_moeda(total_proventos)
    total_descontos = arredondar_moeda(total_descontos)
    salario_liquido = arredondar_moeda(total_proventos - total_descontos)

    return {
        "resumo": {
            "salario_base_contratual": float(arredondar_moeda(sb)),
            "salario_base_proporcional": float(salario_prop),
            "valor_hora_normal": float(arredondar_moeda(vh_normal)),
            "dias_trabalhados": float(dt),
            "dias_mes": dm,
            "divisor_horas": float(div_h),
            "total_proventos": float(total_proventos),
            "total_descontos": float(total_descontos),
            "salario_liquido": float(salario_liquido),
            "base_inss": float(arredondar_moeda(base_inss)),
            "base_fgts": float(arredondar_moeda(base_inss)),
            "valor_fgts_informativo": float(valor_fgts),
            "base_irrf": float(base_irrf),
            "numero_dependentes": numero_dependentes
        },
        "itens": itens_consolidados,
        "validacoes": [
            "Os percentuais e faixas de INSS/IRRF devem ser validados pelo responsável da folha conforme a tabela da competência.",
            "Não aplique descontos duplicados ou eventos com o mesmo código."
        ]
    }

