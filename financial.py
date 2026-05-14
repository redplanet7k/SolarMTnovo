"""
financial.py — Matemática Financeira — BCT/UFMT
VPL, TIR, Payback, Juros Compostos, Depreciação
"""
import numpy as np
from data import (
    CUSTO_POR_KWP, TARIFA_ENERGIA_KWH, INFLACAO_ENERGIA_AA,
    TAXA_DESCONTO, VIDA_UTIL_ANOS, TAXA_DEPRECIACAO_AA,
    CUSTO_MANUTENCAO_AA, FATOR_EMISSAO_CO2_KG_KWH,
)


def calcular_investimento(potencia_kWp: float) -> dict:
    c = potencia_kWp * CUSTO_POR_KWP
    return {
        "custo_total":      round(c, 2),
        "custo_modulos":    round(c * 0.45, 2),
        "custo_inversor":   round(c * 0.20, 2),
        "custo_estrutura":  round(c * 0.10, 2),
        "custo_instalacao": round(c * 0.15, 2),
        "custo_outros":     round(c * 0.10, 2),
    }


def calcular_fluxo_caixa(geracao_anual_kwh, consumo_mensal_kwh, custo_total) -> dict:
    """Fluxo de caixa anual com juros compostos e depreciação."""
    consumo_anual = consumo_mensal_kwh * 12
    ger_util = min(geracao_anual_kwh, consumo_anual)
    anos, fl_liq, fl_desc, acum, ecos, manuts = [], [], [], [], [], []
    acumulado = -custo_total
    for t in range(1, VIDA_UTIL_ANOS + 1):
        tarifa_t  = TARIFA_ENERGIA_KWH * (1 + INFLACAO_ENERGIA_AA) ** t
        geracao_t = ger_util * (1 - TAXA_DEPRECIACAO_AA) ** t
        eco       = geracao_t * tarifa_t
        manu      = CUSTO_MANUTENCAO_AA * (1 + 0.045) ** t
        fl        = eco - manu
        fd        = fl / (1 + TAXA_DESCONTO) ** t
        acumulado += fl
        anos.append(t); fl_liq.append(round(fl, 2)); fl_desc.append(round(fd, 2))
        acum.append(round(acumulado, 2)); ecos.append(round(eco, 2)); manuts.append(round(manu, 2))
    return {"anos": anos, "fluxo_liquido": fl_liq, "fluxo_descontado": fl_desc,
            "acumulado": acum, "economias": ecos, "manutencoes": manuts}


def calcular_payback(acumulado, fluxo_descontado, custo_total) -> dict:
    pb_s = next((i+1 for i, v in enumerate(acumulado) if v >= 0), None)
    acc = -custo_total
    pb_d = None
    for i, fd in enumerate(fluxo_descontado):
        acc += fd
        if acc >= 0:
            pb_d = i + 1; break
    return {"payback_simples_anos": pb_s, "payback_descontado_anos": pb_d}


def calcular_vpl(fluxo_descontado, custo_total) -> dict:
    vpl = -custo_total + sum(fluxo_descontado)
    return {"vpl": round(vpl, 2), "viavel": vpl > 0}


def calcular_tir(fluxo_liquido, custo_total) -> float:
    fluxos = [-custo_total] + fluxo_liquido
    def _vpl(r):
        return sum(c / (1+r)**t for t, c in enumerate(fluxos))
    lo, hi = 0.001, 5.0
    for _ in range(500):
        mid = (lo + hi) / 2
        if _vpl(mid) > 0: lo = mid
        else: hi = mid
    return round(mid * 100, 1)


def economia_mensal_ano1(geracao_mensal_kwh, consumo_mensal_kwh) -> dict:
    return {mes: round(min(g, consumo_mensal_kwh) * TARIFA_ENERGIA_KWH, 2)
            for mes, g in geracao_mensal_kwh.items()}


def co2_evitado(geracao_anual_kwh) -> dict:
    kg_ano = geracao_anual_kwh * FATOR_EMISSAO_CO2_KG_KWH
    ton_25 = kg_ano * VIDA_UTIL_ANOS / 1000
    return {
        "kg_co2_ano":     round(kg_ano, 1),
        "ton_co2_25anos": round(ton_25, 1),
        "arvores_eq":     round(ton_25 * 1000 / 21.77),
    }
