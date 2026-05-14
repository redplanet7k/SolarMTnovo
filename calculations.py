"""
calculations.py — Cálculos fotovoltaicos
Física III + Cálculo III — BCT/UFMT
"""
import numpy as np
from data import (
    LATITUDE, IRRADIANCIA_MENSAL, DIAS_POR_MES, MESES,
    MODULO_POTENCIA_WP, MODULO_AREA_M2, MODULO_COEF_TEMP,
    TEMP_REFERENCIA, TEMP_OPERACAO_LOCAL, HSP_MEDIA_ANUAL,
    FATOR_DESEMPENHO, PERDA_INVERSOR, PERDA_CABEAMENTO,
    PERDA_SOMBREAMENTO, PERDA_SUJEIRA, PERDA_TEMPERATURA,
    intervalo_confianca_geracao,
)


def calcular_potencia_sistema(consumo_kwh_mes: float) -> dict:
    """
    P_pico [kWp] = E_mes × 1,10 / (HSP_med × PR × 30)
    Fórmula do Atlas Brasileiro de Energia Solar (cap.11)
    """
    consumo_com_folga = consumo_kwh_mes * 1.10
    potencia_kWp = consumo_com_folga / (HSP_MEDIA_ANUAL * FATOR_DESEMPENHO * 30)
    n_modulos = int(np.ceil(potencia_kWp * 1000 / MODULO_POTENCIA_WP))
    potencia_real_kWp = round(n_modulos * MODULO_POTENCIA_WP / 1000, 3)
    return {
        "potencia_nominal_kWp": round(potencia_kWp, 3),
        "potencia_real_kWp":    potencia_real_kWp,
        "n_modulos":            n_modulos,
        "area_total_m2":        round(n_modulos * MODULO_AREA_M2, 2),
        "fator_desempenho":     FATOR_DESEMPENHO,
    }


def calcular_geracao_mensal(potencia_kWp: float) -> dict:
    """G_mes = P_kWp × HSP_mes × dias × PR"""
    geracao, ic_lo, ic_hi = {}, {}, {}
    for i, mes in enumerate(MESES):
        g = potencia_kWp * IRRADIANCIA_MENSAL[mes] * DIAS_POR_MES[i] * FATOR_DESEMPENHO
        geracao[mes] = round(g, 1)
        lo, hi = intervalo_confianca_geracao(g, mes)
        ic_lo[mes] = round(lo, 1)
        ic_hi[mes] = round(hi, 1)
    return {"geracao_kwh": geracao, "ic_lower": ic_lo, "ic_upper": ic_hi,
            "media_anual": round(sum(geracao.values()), 1)}


def perda_por_temperatura(temp_operacao: float = TEMP_OPERACAO_LOCAL) -> float:
    """ΔP/P = |αT| × (T_op − T_STC)"""
    return round(abs(MODULO_COEF_TEMP) * (temp_operacao - TEMP_REFERENCIA) * 100, 2)


def angulo_otimo() -> dict:
    """β* = |φ| ≈ latitude local — Atlas cap.11"""
    betas = np.arange(0, 45, 0.5)
    def irr(b):
        lat_r = np.radians(abs(LATITUDE))
        beta_r = np.radians(b)
        fator = np.cos(lat_r - beta_r)
        return max(HSP_MEDIA_ANUAL * (0.80 + 0.20 * fator), 0)
    irrs = [irr(b) for b in betas]
    idx = int(np.argmax(irrs))
    return {"angulo_otimo_graus": float(betas[idx]), "irradiancia_maxima": float(irrs[idx]),
            "betas": betas.tolist(), "irradiancias": irrs}


def resumo_perdas() -> dict:
    return {
        "Inversor":    round(PERDA_INVERSOR * 100, 1),
        "Cabeamento":  round(PERDA_CABEAMENTO * 100, 1),
        "Sombreamento":round(PERDA_SOMBREAMENTO * 100, 1),
        "Sujeira":     round(PERDA_SUJEIRA * 100, 1),
        "Temperatura": round(PERDA_TEMPERATURA * 100, 1),
        "Total":       round((1 - FATOR_DESEMPENHO) * 100, 1),
    }
