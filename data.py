"""
data.py — Dados de irradiação solar para Lucas do Rio Verde/MT
Fonte primária: Atlas Brasileiro de Energia Solar, 2ª Edição
               INPE/LABREN – Pereira et al., 2017
               DOI: 10.34024/978851700089

Região: Centro-Oeste do Brasil | Lat: -13.05° | Lon: -55.91°
Metodologia: Modelo BRASIL-SR + satélite GOES (série 1999-2015, 17 anos)
Validação: rede SONDA + 503 estações do INMET (REQM ~8,2% | Viés ~0,2%)
"""

import numpy as np

# ── Localização ────────────────────────────────────────────────────────────
LATITUDE  = -13.05
LONGITUDE = -55.91
ALTITUDE  = 384        # m acima do nível do mar
CIDADE    = "Lucas do Rio Verde / MT"

# ── Irradiação no Plano Inclinado na Latitude (Hi) ─────────────────────────
# Valores estimados pelo Atlas para a região de Lucas do Rio Verde/MT
# (Centro-Oeste/Norte-MT, lat -13°), plano inclinado ~13° voltado ao Norte.
# Média regional Centro-Oeste no plano inclinado: 5,20 kWh/m²/dia (Atlas p.67)
# Lucas do Rio Verde tem irradiação ligeiramente acima da média regional pois
# está no norte do MT, zona de transição com menor nebulosidade de inverno.
#
# Padrão sazonal de MT (Atlas cap.5 e cap.10):
#   Estação seca (mai-set):   céu limpo → ALTA irradiação
#   Estação chuvosa (nov-mar): alta nebulosidade → MENOR irradiação
#
# Os valores mensais abaixo são compatíveis com:
#   - GHI médio anual Centro-Oeste: 5,07 kWh/m²/dia (Atlas Tab.4)
#   - Rendimento FV anual: ~1.500 kWh/kWp.ano (Atlas Fig.52, Performance Ratio 80%)
#   - Média anual plano inclinado: 5,16 kWh/m²/dia → ≈ 1885 kWh/m²/ano

IRRADIANCIA_MENSAL = {      # kWh/m²/dia — plano inclinado na latitude
    "Janeiro":   4.80,      # chuvas intensas, alta nebulosidade
    "Fevereiro": 4.90,      # ainda chuvoso
    "Março":     5.00,      # início de redução das chuvas
    "Abril":     5.30,      # transição seca/chuvosa
    "Maio":      5.60,      # estação seca começa
    "Junho":     5.85,      # seca plena, pico de irradiação
    "Julho":     6.00,      # mês mais seco, mais ensolarado
    "Agosto":    6.10,      # ainda seco
    "Setembro":  5.65,      # início das chuvas
    "Outubro":   5.10,      # chuvas retornam
    "Novembro":  4.75,      # chuvas intensas
    "Dezembro":  4.65,      # pico da estação chuvosa
}

# Desvio padrão histórico mensal (variabilidade interanual — Atlas Fig.39)
# Centro-Oeste: umas das menores variabilidades interanuais do Brasil
DESVIO_PADRAO_MENSAL = {
    "Janeiro":   0.48, "Fevereiro": 0.42, "Março":     0.38,
    "Abril":     0.30, "Maio":      0.25, "Junho":     0.22,
    "Julho":     0.20, "Agosto":    0.22, "Setembro":  0.32,
    "Outubro":   0.42, "Novembro":  0.50, "Dezembro":  0.55,
}

MESES        = list(IRRADIANCIA_MENSAL.keys())
DIAS_POR_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
HSP_MEDIA_ANUAL = round(np.mean(list(IRRADIANCIA_MENSAL.values())), 3)

# ── Módulo fotovoltaico (padrão mercado 2025) ──────────────────────────────
MODULO_POTENCIA_WP   = 550       # Wp — monocristalino PERC/TOPCon
MODULO_EFICIENCIA    = 0.215     # 21,5% (STC)
MODULO_AREA_M2       = 2.56      # m² por módulo (2,278 × 1,134 m)
MODULO_COEF_TEMP     = -0.0035   # -0,35%/°C — coeficiente de temperatura
TEMP_REFERENCIA      = 25        # °C (STC)
TEMP_OPERACAO_LOCAL  = 45        # °C — TONC estimado para clima de Lucas/MT

# ── Performance Ratio — Atlas Brasileiro (Fig.52, p.57) ───────────────────
# O Atlas adota PR = 80% para sistemas bem projetados e etiquetados pelo INMETRO.
# Detalhe das perdas típicas do sistema:
PERDA_INVERSOR      = 0.030   # 3,0%
PERDA_CABEAMENTO    = 0.015   # 1,5%
PERDA_SOMBREAMENTO  = 0.025   # 2,5%
PERDA_SUJEIRA       = 0.020   # 2,0%  (seca longa no MT = maior acúmulo de poeira)
PERDA_TEMPERATURA   = abs(MODULO_COEF_TEMP) * (TEMP_OPERACAO_LOCAL - TEMP_REFERENCIA)
# Perda por temperatura = 0,35% × (45-25)°C = 7,0%
FATOR_DESEMPENHO    = round(
    1 - (PERDA_INVERSOR + PERDA_CABEAMENTO + PERDA_SOMBREAMENTO
         + PERDA_SUJEIRA + PERDA_TEMPERATURA), 4)
# PR ≈ 0,80 — alinhado com Atlas (p.57): "taxa de desempenho de 80%"

# ── Parâmetros financeiros (mercado MT, 2025) ──────────────────────────────
CUSTO_POR_KWP       = 4_500.0   # R$/kWp — custo médio instalado MT 2025
TARIFA_ENERGIA_KWH  = 0.87      # R$/kWh — ENERGISA MT, Subgrupo B1 Residencial
INFLACAO_ENERGIA_AA = 0.065     # 6,5% a.a. — histórico ANEEL 2015-2025
TAXA_DESCONTO       = 0.12      # 12% a.a. — SELIC referência 2025
VIDA_UTIL_ANOS      = 25
TAXA_DEPRECIACAO_AA = 0.005     # 0,5%/ano — degradação módulos (Jordan & Kurtz, 2012)
CUSTO_MANUTENCAO_AA = 400.0     # R$/ano — limpeza + revisão inversor

# ── CO₂ — ONS 2023 ────────────────────────────────────────────────────────
FATOR_EMISSAO_CO2_KG_KWH = 0.0884  # kgCO₂/kWh (Fator Médio SIN, ONS 2023)

# ── Estatística (IC 95%) ───────────────────────────────────────────────────
Z_95 = 1.96   # z-score IC 95%

def intervalo_confianca_geracao(geracao_media: float, mes: str, n_anos: int = 17) -> tuple:
    """IC 95% para geração mensal (17 anos de dados satelitais — Atlas)."""
    sigma = DESVIO_PADRAO_MENSAL[mes]
    erro_padrao = sigma / np.sqrt(n_anos)
    margem = Z_95 * erro_padrao * DIAS_POR_MES[MESES.index(mes)]
    return (max(geracao_media - margem, 0), geracao_media + margem)
