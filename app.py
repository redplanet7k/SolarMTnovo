"""
app.py — SolarMT | Calculadora de Viabilidade Solar Fotovoltaica
Dados baseados no Atlas Brasileiro de Energia Solar, 2ª Ed. (INPE/LABREN 2017)
Criado por Atlas Kennedy — Graduando em Ciência e Tecnologia · UFMT
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data import (
    MESES, IRRADIANCIA_MENSAL, DIAS_POR_MES,
    TARIFA_ENERGIA_KWH, CUSTO_POR_KWP, VIDA_UTIL_ANOS,
    TAXA_DESCONTO, INFLACAO_ENERGIA_AA, HSP_MEDIA_ANUAL,
    LATITUDE, TEMP_OPERACAO_LOCAL, TEMP_REFERENCIA,
    FATOR_DESEMPENHO,
)
from calculations import (
    calcular_potencia_sistema, calcular_geracao_mensal,
    angulo_otimo, resumo_perdas, perda_por_temperatura,
)
from financial import (
    calcular_investimento, calcular_fluxo_caixa,
    calcular_payback, calcular_vpl, calcular_tir,
    economia_mensal_ano1, co2_evitado,
)

# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="SolarMT — Viabilidade Solar Fotovoltaica",
    page_icon="☀️", layout="wide",
    initial_sidebar_state="collapsed",
)

if "step" not in st.session_state:
    st.session_state.step = 1
if "form" not in st.session_state:
    st.session_state.form = {}

# ── HSP por cidade (Atlas Brasileiro, Fig.52 / Cap.8) ──
CIDADES_HSP = {
    "Lucas do Rio Verde": 5.16,
    "Cuiabá":             5.20,
    "Várzea Grande":      5.20,
    "Rondonópolis":       5.15,
    "Sorriso":            5.10,
    "Sinop":              5.05,
    "Alta Floresta":      4.95,
    "Tangará da Serra":   5.10,
    "Barra do Garças":    5.18,
    "Cáceres":            5.12,
    "Campo Grande/MS":    5.25,
    "Outro município MT": 5.07,
}

SAZON = [0.930,0.950,0.968,1.027,1.082,1.132,1.161,1.181,1.094,0.988,0.919,0.900]
MESES_C = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

# ── Cores ──
BG="#080f1e"; BG2="#0c1628"; BG3="#111e38"
AMBER="#f59e0b"; GREEN="#10b981"; BLUE="#60a5fa"
MUTED="#7a90b8"; TEXT="#e8f0ff"; GRID="rgba(255,255,255,0.04)"

def theme(fig, height=260):
    fig.update_layout(
        paper_bgcolor=BG2, plot_bgcolor=BG,
        font=dict(family="Sora,sans-serif", color=TEXT, size=11),
        legend=dict(bgcolor=BG2, bordercolor="rgba(255,255,255,0.09)",
                    font=dict(color=MUTED, size=10)),
        height=height, margin=dict(l=8,r=8,t=36,b=8),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID,
                     linecolor="rgba(255,255,255,0.09)", tickfont=dict(color=MUTED,size=10))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID,
                     linecolor="rgba(255,255,255,0.09)", tickfont=dict(color=MUTED,size=10))
    return fig

# ══════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
:root{
  --bg:#080f1e;--bg2:#0c1628;--bg3:#111e38;
  --card:rgba(255,255,255,0.05);--cb:rgba(255,255,255,0.09);
  --amber:#f59e0b;--amber2:#fbbf24;
  --abg:rgba(245,158,11,0.12);--abd:rgba(245,158,11,0.3);
  --green:#10b981;--gbg:rgba(16,185,129,0.1);--gbd:rgba(16,185,129,0.3);
  --blue:#60a5fa;--bbg:rgba(96,165,250,0.1);--bbd:rgba(96,165,250,0.3);
  --text:#e8f0ff;--muted:#7a90b8;--dim:#3d5280;
}
html,body,[class*="css"]{font-family:'Sora',sans-serif!important;background-color:var(--bg)!important;color:var(--text)!important;}
.stApp{background-color:var(--bg)!important;}
#MainMenu,footer,header[data-testid="stHeader"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
.block-container{max-width:880px!important;padding:0 16px 80px!important;margin:0 auto!important;}

/* Topbar */
.topbar{padding:14px 0 12px;display:flex;align-items:center;gap:12px;border-bottom:1px solid var(--cb);margin-bottom:0;}
.logo-icon{width:36px;height:36px;border-radius:9px;background:linear-gradient(135deg,#f59e0b,#f97316);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.logo-text{font-size:17px;font-weight:700;color:var(--text);}
.logo-text span{color:var(--amber);}
.htag{margin-left:auto;font-size:10px;color:var(--muted);background:var(--bg3);border:1px solid var(--cb);border-radius:20px;padding:3px 12px;white-space:nowrap;}

/* Hero */
.hero{text-align:center;padding:36px 16px 20px;}
.hero h1{font-size:clamp(20px,5vw,36px);font-weight:700;background:linear-gradient(135deg,var(--text) 30%,var(--amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:10px;line-height:1.2;}
.hero p{color:var(--muted);font-size:14px;max-width:520px;margin:0 auto 18px;}
.hero-badges{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;}
.badge{background:var(--bg3);border:1px solid var(--cb);border-radius:20px;padding:4px 12px;font-size:11px;color:var(--muted);}

/* Stepper */
.stepper{display:flex;align-items:center;justify-content:center;padding:18px 16px;max-width:460px;margin:0 auto 24px;}
.step{display:flex;align-items:center;gap:7px;}
.snum{width:32px;height:32px;border-radius:50%;background:var(--bg3);border:1.5px solid var(--dim);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;color:var(--dim);}
.slabel{font-size:12px;color:var(--dim);font-weight:500;}
.step.active .snum{background:var(--amber);border-color:var(--amber);color:#08101e;}
.step.active .slabel{color:var(--amber);}
.step.done .snum{background:var(--green);border-color:var(--green);color:#fff;}
.step.done .slabel{color:var(--green);}
.sline{flex:1;height:1px;background:var(--dim);margin:0 8px;min-width:28px;}
.sline.done{background:var(--green);}

/* Cards */
.card{background:var(--card);border:1px solid var(--cb);border-radius:14px;padding:22px 20px;margin-bottom:14px;}
.card-h{font-size:16px;font-weight:600;margin-bottom:4px;}
.card-sub{font-size:13px;color:var(--muted);margin-bottom:18px;}

/* Metric grid */
.mg{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;}
.mc{border-radius:12px;padding:14px 12px;background:var(--card);border:1px solid var(--cb);}
.mc.a{background:var(--abg);border-color:var(--abd);}
.mc.g{background:var(--gbg);border-color:var(--gbd);}
.mc.b{background:var(--bbg);border-color:var(--bbd);}
.ml{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:4px;}
.mv{font-size:19px;font-weight:700;line-height:1.2;}
.mc.a .mv{color:var(--amber);}
.mc.g .mv{color:var(--green);}
.mc.b .mv{color:var(--blue);}
.mu{font-size:10px;color:var(--dim);margin-top:2px;}

/* TIR card */
.tir-card{display:flex;align-items:center;gap:16px;background:var(--gbg);border:1px solid var(--gbd);border-radius:12px;padding:16px 18px;margin-bottom:12px;flex-wrap:wrap;}
.tir-val{font-size:28px;font-weight:700;color:var(--green);}
.tir-msg{flex:1;min-width:200px;font-size:12px;color:var(--muted);line-height:1.5;}

/* Info boxes */
.ibox{background:rgba(96,165,250,.08);border:1px solid rgba(96,165,250,.25);border-radius:8px;padding:12px 14px;font-size:13px;color:#93c5fd;margin-bottom:12px;line-height:1.6;}
.ibox-w{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.3);border-radius:8px;padding:12px 14px;font-size:13px;color:#fde68a;margin-bottom:12px;line-height:1.6;}
.ibox-r{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:12px 14px;font-size:13px;color:#fca5a5;margin-bottom:12px;}

/* Atlas badge */
.atlas-tag{display:inline-block;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;font-size:10px;border-radius:20px;padding:2px 10px;margin-left:6px;vertical-align:middle;}

/* Disciplinas */
.disc-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px;}
.dcard{border-radius:8px;padding:12px;border:1px solid;}
.da{background:var(--abg);border-color:var(--abd);}
.db{background:var(--bbg);border-color:var(--bbd);}
.dg{background:var(--gbg);border-color:var(--gbd);}
.dp{background:rgba(192,132,252,.1);border-color:rgba(192,132,252,.3);}
.full{grid-column:span 2;}
.dcard h4{font-size:12px;font-weight:600;margin-bottom:4px;}
.da h4{color:var(--amber);} .db h4{color:var(--blue);} .dg h4{color:var(--green);} .dp h4{color:#c084fc;}
.dcard p{font-size:11px;color:var(--muted);line-height:1.5;}

/* Footer */
.footer{margin-top:36px;padding:20px 0 14px;border-top:1px solid var(--cb);text-align:center;color:var(--muted);font-size:12px;line-height:1.8;}
.footer a{color:var(--amber);text-decoration:none;font-weight:600;}
.footer-brand{color:#fff;font-weight:700;font-size:14px;margin-bottom:4px;}

/* Widgets */
input,textarea{background:#111e38!important;color:#e8f0ff!important;caret-color:#e8f0ff!important;}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{background:#111e38!important;border:1px solid rgba(255,255,255,0.15)!important;border-radius:8px!important;color:#e8f0ff!important;font-size:15px!important;-webkit-text-fill-color:#e8f0ff!important;min-height:44px!important;}
div[data-testid="stSelectbox"] div[data-baseweb="select"]>div{background:#111e38!important;border:1px solid rgba(255,255,255,0.15)!important;border-radius:8px!important;color:#e8f0ff!important;min-height:44px!important;}
div[data-testid="stSelectbox"] div[data-baseweb="select"] *{color:#e8f0ff!important;}
label[data-testid="stWidgetLabel"] p{font-size:11px!important;font-weight:600!important;color:var(--muted)!important;text-transform:uppercase;letter-spacing:.06em!important;}
div[data-testid="stSlider"] p{color:var(--muted)!important;}
div[data-testid="stButton"]>button{border-radius:8px!important;font-family:'Sora',sans-serif!important;font-weight:600!important;font-size:14px!important;padding:10px 22px!important;min-height:44px!important;}
div[data-testid="stButton"]>button[kind="primary"]{background:var(--amber)!important;color:#08101e!important;border:none!important;}
div[data-testid="stButton"]>button[kind="secondary"]{background:transparent!important;color:var(--muted)!important;border:1px solid rgba(255,255,255,0.09)!important;}
div[data-testid="stTabs"] button{color:var(--muted)!important;font-size:12px!important;}
div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--amber)!important;border-bottom-color:var(--amber)!important;}
div[data-testid="stTabs"]>div:first-child{overflow-x:auto!important;flex-wrap:nowrap!important;scrollbar-width:none;}

/* Mobile */
@media(max-width:680px){
  .mg{grid-template-columns:1fr 1fr!important;}
  .disc-grid{grid-template-columns:1fr!important;}
  .full{grid-column:span 1!important;}
  .hero h1{font-size:22px;}
  .tir-card{flex-direction:column;gap:8px;}
  .htag{display:none;}
  div[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;}
  div[data-testid="stHorizontalBlock"]>div{min-width:100%!important;flex:1 1 100%!important;}
  .card{padding:16px 14px;}
  .mv{font-size:17px;}
}
@media(max-width:380px){.mg{grid-template-columns:1fr!important;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TOPBAR + HERO
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
  <div class="logo-icon">☀️</div>
  <span class="logo-text">Solar<span>MT</span></span>
  <div class="htag">UFMT · Seminário Integrador IV · 2026</div>
</div>
<div class="hero">
  <h1>Calculadora de Viabilidade<br>Solar Fotovoltaica</h1>
  <p>Análise técnica e financeira baseada no <strong>Atlas Brasileiro de Energia Solar</strong> (INPE/LABREN, 2ª Ed. 2017) — dados reais de 17 anos de satélite para o Mato Grosso.</p>
  <div class="hero-badges">
    <span class="badge">⚡ Física III</span>
    <span class="badge">∫ Cálculo III</span>
    <span class="badge">💰 Mat. Financeira</span>
    <span class="badge">📊 Prob. e Estatística</span>
    <span class="badge">🧠 Gestão do Conhecimento</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stepper ──────────────────────────────────────────
def render_stepper(step):
    labels = ["Consumo","Instalação","Resultados"]
    h = '<div class="stepper">'
    for i, lb in enumerate(labels, 1):
        cls = "active" if i==step else ("done" if i<step else "")
        num = "✓" if i<step else str(i)
        h += f'<div class="step {cls}"><div class="snum">{num}</div><span class="slabel">{lb}</span></div>'
        if i<3:
            h += f'<div class="sline {"done" if step>i else ""}"></div>'
    st.markdown(h+"</div>", unsafe_allow_html=True)

render_stepper(st.session_state.step)

# ══════════════════════════════════════════════════════
# ETAPA 1 — CONSUMO
# ══════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown('<div class="card"><div class="card-h">⚡ Dados de Consumo</div><div class="card-sub">Preencha com as informações da sua conta de energia elétrica.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        cidade = st.selectbox("Cidade / Região", list(CIDADES_HSP.keys()),
            help="HSP médio anual conforme Atlas Brasileiro de Energia Solar (INPE 2017)")
    with c2:
        tipo = st.selectbox("Tipo de Propriedade",
            ["Residencial","Rural / Produtor","Comercial / Industrial"])
    c3, c4 = st.columns(2)
    with c3:
        consumo = st.number_input("Consumo Médio Mensal (kWh)", 50, 100000, 350, 10,
            help='Campo "Consumo" da conta de energia (média dos últimos 12 meses)')
    with c4:
        tarifa = st.number_input("Tarifa de Energia (R$/kWh)", 0.20, 5.00, 0.87, 0.01,
            format="%.2f", help="ENERGISA MT — Subgrupo B1 Residencial 2025: R$ 0,87/kWh")
    st.markdown("</div>", unsafe_allow_html=True)
    _, bc = st.columns([3,1])
    with bc:
        if st.button("Próximo →", type="primary", use_container_width=True):
            st.session_state.form.update({"cidade":cidade,"tipo":tipo,"consumo":consumo,"tarifa":tarifa})
            st.session_state.step = 2
            st.rerun()

# ══════════════════════════════════════════════════════
# ETAPA 2 — INSTALAÇÃO
# ══════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown('<div class="card"><div class="card-h">🏠 Dados de Instalação</div><div class="card-sub">Informe os detalhes do local e como pretende financiar o projeto.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        area = st.number_input("Área Disponível no Telhado (m²)", 0, 50000, 0, 5,
            help="Área com boa incidência solar, sem sombra. Cada painel ocupa ≈ 2,56 m². Deixe 0 para calcular automaticamente.")
    with c2:
        orcamento = st.number_input("Orçamento Máximo (R$) — Opcional", 0, 9999999, 0, 1000,
            help="Custo médio MT: R$ 4.500/kWp instalado. Deixe 0 para calcular o ideal.")
    c3, c4 = st.columns(2)
    with c3:
        modalidade = st.selectbox("Modalidade de Compra",
            ["À vista","Financiado (BNDES / banco)","Consórcio","Leasing solar"])
    with c4:
        inflacao = st.slider("Inflação da Energia (% a.a.)", 1.0, 15.0, 6.5, 0.5,
            help="Histórico ANEEL 2015–2025 ≈ 6,5% a.a.") / 100
    taxa_desc = st.slider("Taxa de Desconto / SELIC (% a.a.)", 5.0, 20.0, 12.0, 0.5) / 100
    taxa_fin = prazo_fin = None
    if "Financiado" in modalidade:
        f1, f2 = st.columns(2)
        with f1:
            taxa_fin = st.number_input("Taxa de Juros Anual (%)", 0.0, 40.0, 10.0, 0.1,
                help="BNDES Mais Solar: ≈ 6–8% a.a.") / 100
        with f2:
            prazo_fin = st.number_input("Prazo (meses)", 12, 240, 60, 12)
    st.markdown("</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Anterior", type="secondary", use_container_width=True):
            st.session_state.step = 1; st.rerun()
    with b2:
        if st.button("☀️ Calcular Viabilidade", type="primary", use_container_width=True):
            st.session_state.form.update({"area":area,"orcamento":orcamento,
                "modalidade":modalidade,"inflacao":inflacao,"taxa_desc":taxa_desc,
                "taxa_fin":taxa_fin,"prazo_fin":prazo_fin})
            st.session_state.step = 3; st.rerun()

# ══════════════════════════════════════════════════════
# ETAPA 3 — RESULTADOS
# ══════════════════════════════════════════════════════
elif st.session_state.step == 3:
    f = st.session_state.form
    consumo   = f["consumo"]
    tarifa    = f["tarifa"]
    inflacao  = f["inflacao"]
    taxa_desc = f["taxa_desc"]
    area_disp = f["area"] or 999999
    orcamento = f["orcamento"] or 999999999
    modalidade= f["modalidade"]
    HSP       = CIDADES_HSP.get(f["cidade"], HSP_MEDIA_ANUAL)

    # Atualiza módulos financeiros dinamicamente
    import financial as fin, data as dados
    dados.TARIFA_ENERGIA_KWH  = tarifa
    dados.INFLACAO_ENERGIA_AA = inflacao
    dados.TAXA_DESCONTO       = taxa_desc
    fin.TARIFA_ENERGIA_KWH    = tarifa
    fin.INFLACAO_ENERGIA_AA   = inflacao
    fin.TAXA_DESCONTO         = taxa_desc

    # ── Dimensionamento com HSP da cidade ──────────────────
    # Recalcula HSP_MEDIA_ANUAL local com a cidade selecionada
    dados.HSP_MEDIA_ANUAL = HSP
    import calculations as calc
    calc.HSP_MEDIA_ANUAL  = HSP

    pot = calcular_potencia_sistema(consumo)

    # Ajuste por área e orçamento
    n = pot["n_modulos"]
    max_area  = int(area_disp / 2.56)
    max_orcam = int(orcamento / (CUSTO_POR_KWP * 0.55))
    if f["area"] > 0:  n = min(n, max_area)
    if f["orcamento"] > 0: n = min(n, max_orcam)
    n = max(n, 1)
    kwp      = round(n * 0.55, 2)
    area_nec = round(n * 2.56, 1)

    # Geração usando HSP mensal ponderado pela cidade
    PR = FATOR_DESEMPENHO
    ger_mes_vals = {m: round(kwp * IRRADIANCIA_MENSAL[m] * (HSP/HSP_MEDIA_ANUAL) * DIAS_POR_MES[i] * PR, 1)
                    for i, m in enumerate(MESES)}
    ger_ano  = round(sum(ger_mes_vals.values()), 1)
    ger_mes_media = round(ger_ano / 12, 1)
    cob      = min(100, round(ger_mes_media / consumo * 100))

    inv  = calcular_investimento(kwp)
    fc   = calcular_fluxo_caixa(ger_ano, consumo, inv["custo_total"])
    pb   = calcular_payback(fc["acumulado"], fc["fluxo_descontado"], inv["custo_total"])
    vpl  = calcular_vpl(fc["fluxo_descontado"], inv["custo_total"])
    tir  = calcular_tir(fc["fluxo_liquido"], inv["custo_total"])
    eco  = {m: round(min(g, consumo) * tarifa, 2) for m, g in ger_mes_vals.items()}
    co2  = co2_evitado(ger_ano)
    eco_mes = round(np.mean(list(eco.values())), 2)

    # TIR mensagem
    if tir >= 15:   tir_txt = "🟢 Excelente! Supera amplamente a Selic e renda fixa."
    elif tir >= 10: tir_txt = "🟢 Ótima rentabilidade. Superior à Selic histórica."
    elif tir >= 7:  tir_txt = "🟡 Boa rentabilidade. Comparável a CDBs de longo prazo."
    elif tir >= 4:  tir_txt = "🟡 Moderada. Avalie negociar o custo de instalação."
    else:           tir_txt = "🔴 Baixa. Reduza o sistema ou busque outro orçamento."

    # Financiamento
    pmt_val = saldo_val = None
    if "Financiado" in modalidade and f.get("taxa_fin") and f.get("prazo_fin"):
        rm = f["taxa_fin"] / 12
        pf = int(f["prazo_fin"])
        pmt_val = round(inv["custo_total"] * rm * (1+rm)**pf / ((1+rm)**pf - 1)) if rm > 0 \
                  else round(inv["custo_total"] / pf)
        saldo_val = round(eco_mes - pmt_val)

    # ── Info box ──────────────────────────────────────────
    st.markdown(f"""
    <div class="ibox">
      ✅ Com <strong>{n} painéis de 550 Wp</strong> ({kwp:.2f} kWp), o sistema cobre
      <strong>{cob}%</strong> do seu consumo de {consumo} kWh/mês.
      &nbsp;|&nbsp; HSP local: <strong>{HSP:.2f} kWh/m²/dia</strong>
      <span class="atlas-tag">Atlas INPE 2017</span>
      &nbsp;|&nbsp; PR: <strong>{PR*100:.0f}%</strong>
    </div>
    """, unsafe_allow_html=True)

    if f["area"] > 0 and area_nec > f["area"]:
        st.markdown(f'<div class="ibox-r">⚠️ Sistema limitado pela área ({f["area"]} m²). Ideal: {area_nec:.0f} m².</div>', unsafe_allow_html=True)

    # ── Métricas âmbar (técnico) ──────────────────────────
    st.markdown(f"""
    <div class="mg">
      <div class="mc a"><div class="ml">Painéis</div><div class="mv">{n}</div><div class="mu">× 550 Wp</div></div>
      <div class="mc a"><div class="ml">Potência</div><div class="mv">{kwp:.2f} kWp</div><div class="mu">kilowatt-pico</div></div>
      <div class="mc a"><div class="ml">Área Necessária</div><div class="mv">{area_nec:.0f} m²</div><div class="mu">telhado útil</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Métricas verde (geração) ──────────────────────────
    st.markdown(f"""
    <div class="mg">
      <div class="mc g"><div class="ml">Geração Anual</div><div class="mv">{ger_ano:,.0f}</div><div class="mu">kWh / ano</div></div>
      <div class="mc g"><div class="ml">Economia Mensal</div><div class="mv">R$ {eco_mes:,.0f}</div><div class="mu">média / mês</div></div>
      <div class="mc g"><div class="ml">CO₂ Evitado</div><div class="mv">{co2["ton_co2_25anos"]:.1f} t</div><div class="mu">em 25 anos</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Métricas azul (financeiro) ────────────────────────
    pb_s = pb["payback_simples_anos"] or ">25"
    pb_d = pb["payback_descontado_anos"] or ">25"
    cor_vpl = "var(--green)" if vpl["viavel"] else "#f87171"
    vpl_fmt = f"R$ {abs(vpl['vpl']):,.0f}"
    if vpl['vpl'] < 0: vpl_fmt = "−"+vpl_fmt
    st.markdown(f"""
    <div class="mg">
      <div class="mc b"><div class="ml">Investimento</div><div class="mv" style="font-size:15px">R$ {inv["custo_total"]:,.0f}</div><div class="mu">R$ {CUSTO_POR_KWP:,.0f}/kWp</div></div>
      <div class="mc b"><div class="ml">Payback Simples</div><div class="mv">{pb_s}</div><div class="mu">anos</div></div>
      <div class="mc b"><div class="ml">VPL 25 anos</div><div class="mv" style="color:{cor_vpl};font-size:15px">{vpl_fmt}</div><div class="mu">{"✅ Viável" if vpl["viavel"] else "❌ Inviável"}</div></div>
    </div>""", unsafe_allow_html=True)

    # ── TIR card ──────────────────────────────────────────
    st.markdown(f"""
    <div class="tir-card">
      <div style="font-size:32px">📈</div>
      <div>
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:{MUTED};margin-bottom:3px">TIR — Taxa Interna de Retorno</div>
        <div class="tir-val">{tir}% a.a.</div>
      </div>
      <div class="tir-msg">{tir_txt}<br><small>Payback descontado: <strong>{pb_d} anos</strong> · SELIC ref.: {taxa_desc*100:.1f}% a.a.</small></div>
    </div>""", unsafe_allow_html=True)

    # ── Financiamento ─────────────────────────────────────
    if pmt_val is not None:
        sc = "var(--green)" if saldo_val >= 0 else "#f87171"
        pfx = "+" if saldo_val >= 0 else ""
        st.markdown(f"""
        <div class="card">
          <div class="card-h">🏦 Financiamento</div>
          <div class="mg" style="margin-top:10px">
            <div class="mc b"><div class="ml">Parcela Mensal</div><div class="mv">R$ {pmt_val:,}</div><div class="mu">R$/mês</div></div>
            <div class="mc g"><div class="ml">Saldo Líquido</div><div class="mv" style="color:{sc}">{pfx}R$ {abs(saldo_val):,}</div><div class="mu">economia − parcela</div></div>
            <div class="mc"><div class="ml">Taxa / Prazo</div><div class="mv" style="color:var(--muted)">{f["taxa_fin"]*100:.1f}%</div><div class="mu">{int(f["prazo_fin"])} meses</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # GRÁFICOS — 5 abas
    # ══════════════════════════════════════════════════════
    st.markdown('<div style="font-size:13px;font-weight:600;color:#7a90b8;margin:20px 0 10px">📊 Análise Visual</div>', unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5 = st.tabs(["☀️ Geração","💸 Retorno","🔬 Física","📊 Estatística","🌿 Ambiental"])

    # ── Tab 1: Geração vs Consumo ─────────────────────────
    with tab1:
        ic_lo = {m: round(max(g*0.91,0),1) for m,g in ger_mes_vals.items()}
        ic_hi = {m: round(g*1.09,1) for m,g in ger_mes_vals.items()}
        gv = [ger_mes_vals[m] for m in MESES]
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=MESES+MESES[::-1],
            y=[ic_hi[m] for m in MESES]+[ic_lo[m] for m in MESES[::-1]],
            fill="toself", fillcolor="rgba(245,158,11,0.10)",
            line=dict(color="rgba(0,0,0,0)"), name="IC 95%", hoverinfo="skip"))
        fig1.add_trace(go.Bar(x=MESES, y=gv, name="Geração Est.",
            marker_color="rgba(245,158,11,0.70)",
            marker_line_color=AMBER, marker_line_width=1))
        fig1.add_trace(go.Scatter(x=MESES, y=[consumo]*12, name="Consumo",
            line=dict(color="#f87171", width=2, dash="dash"), mode="lines"))
        fig1.add_trace(go.Scatter(x=MESES, y=gv, mode="lines+markers",
            name="Geração", line=dict(color=AMBER, width=2),
            marker=dict(size=6, color=AMBER), showlegend=False))
        fig1.update_layout(title="Geração Estimada vs Consumo (kWh/mês)",
            barmode="overlay", yaxis_title="kWh",
            legend=dict(orientation="h", y=-0.30))
        theme(fig1, 300); st.plotly_chart(fig1, use_container_width=True)

        df_ger = pd.DataFrame({
            "Mês": MESES,
            "Geração (kWh)": gv,
            "IC −95%": [ic_lo[m] for m in MESES],
            "IC +95%": [ic_hi[m] for m in MESES],
            "Consumo (kWh)": [consumo]*12,
            "Saldo (kWh)": [round(ger_mes_vals[m]-consumo,1) for m in MESES],
            "Economia (R$)": [eco[m] for m in MESES],
        })
        st.dataframe(df_ger, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="ibox-w" style="font-size:11px;margin-top:8px">
          📐 <strong>Fonte:</strong> Irradiação calculada com dados do Atlas Brasileiro de Energia Solar
          (INPE/LABREN 2017, série 1999–2015, 17 anos de satélite GOES).
          HSP médio anual para {f["cidade"]}: <strong>{HSP:.2f} kWh/m²/dia</strong>.
          Performance Ratio (PR) = <strong>{PR*100:.0f}%</strong> — padrão Atlas para sistemas
          bem dimensionados e etiquetados pelo INMETRO (Atlas Fig.52, p.57).
        </div>""", unsafe_allow_html=True)

    # ── Tab 2: Retorno / Fluxo de Caixa ──────────────────
    with tab2:
        anos_l = [f"Ano {a}" for a in fc["anos"]]
        fig2 = make_subplots(rows=2, cols=1,
            subplot_titles=["Fluxo de Caixa Líquido (R$)","Retorno Acumulado — Payback (R$)"],
            vertical_spacing=0.14)
        cores = [GREEN if v>=0 else "#f87171" for v in fc["fluxo_liquido"]]
        fig2.add_trace(go.Bar(x=anos_l, y=fc["fluxo_liquido"],
            marker_color=cores, name="Fluxo Líquido"), row=1, col=1)
        cores_a = [GREEN if v>=0 else "#f87171" for v in fc["acumulado"]]
        fig2.add_trace(go.Scatter(x=anos_l, y=fc["acumulado"], mode="lines+markers",
            line=dict(color=AMBER, width=2.5), marker=dict(color=cores_a, size=5),
            name="Acumulado"), row=2, col=1)
        # Linha zero
        fig2.add_shape(type="line", x0=0, x1=1, y0=0, y1=0,
            xref="x2 domain", yref="y2", line=dict(dash="dash", color="#f87171", width=1.2))
        fig2.add_annotation(x=0.01, y=0, xref="x2 domain", yref="y2",
            text="Ponto de Equilíbrio", showarrow=False, xanchor="left",
            yanchor="bottom", font=dict(color="#f87171", size=9))
        if pb["payback_simples_anos"]:
            pi = pb["payback_simples_anos"] - 1
            fig2.add_shape(type="line", x0=pi, x1=pi, y0=0, y1=1,
                xref="x2", yref="y2 domain", line=dict(dash="dot", color=AMBER, width=1.8))
            fig2.add_annotation(x=pi, y=1, xref="x2", yref="y2 domain",
                text=f"Payback Ano {pb['payback_simples_anos']}", showarrow=False,
                yanchor="bottom", font=dict(color=AMBER, size=10))
        fig2.update_layout(showlegend=True)
        theme(fig2, 520); st.plotly_chart(fig2, use_container_width=True)

        # Donut
        labels_p = ["Módulos 45%","Inversor 20%","Estrutura 10%","Instalação 15%","Outros 10%"]
        vals_p   = [inv["custo_modulos"],inv["custo_inversor"],inv["custo_estrutura"],
                    inv["custo_instalacao"],inv["custo_outros"]]
        fig_d = go.Figure(go.Pie(labels=labels_p, values=vals_p, hole=0.52,
            marker_colors=[AMBER, BLUE, GREEN, "#c084fc", MUTED],
            textfont=dict(size=10, color=TEXT)))
        fig_d.update_layout(title="Composição do Investimento",
            legend=dict(orientation="h", y=-0.18, font=dict(color=MUTED, size=10)))
        theme(fig_d, 260); st.plotly_chart(fig_d, use_container_width=True)

        st.markdown(f"""
| Indicador | Valor |
|-----------|-------|
| **VPL (25 anos)** | R$ {vpl['vpl']:,.0f} |
| **TIR** | {tir}% a.a. |
| **Payback simples** | {pb["payback_simples_anos"]} anos |
| **Payback descontado** | {pb["payback_descontado_anos"]} anos |
| **Economia anual (ano 1)** | R$ {eco_mes*12:,.0f} |
| **Total 25 anos** | R$ {sum(fc["economias"]):,.0f} |
""")

    # ── Tab 3: Física ─────────────────────────────────────
    with tab3:
        per = resumo_perdas(); ang = angulo_otimo()
        c3a, c3b = st.columns(2)
        with c3a:
            lp = [k for k in per if k!="Total"]
            vp = [per[k] for k in lp]
            fig_per = go.Figure(go.Bar(x=lp, y=vp,
                marker_color="rgba(248,113,113,0.8)",
                marker_line_color="#f87171", marker_line_width=1,
                text=[f"{v}%" for v in vp], textposition="outside",
                textfont=dict(color=MUTED)))
            fig_per.update_layout(title=f"Perdas do Sistema — PR = {FATOR_DESEMPENHO*100:.0f}%", yaxis_title="Perda (%)")
            theme(fig_per, 240); st.plotly_chart(fig_per, use_container_width=True)
            st.latex(r"PR = 1-(\eta_{inv}+\eta_{cab}+\eta_{som}+\eta_{suj}+\alpha_T\Delta T)")
        with c3b:
            fig_ang = go.Figure(go.Scatter(x=ang["betas"], y=ang["irradiancias"],
                mode="lines", line=dict(color=AMBER, width=2.5),
                fill="tozeroy", fillcolor="rgba(245,158,11,0.08)"))
            fig_ang.add_vline(x=ang["angulo_otimo_graus"], line_dash="dash",
                line_color=GREEN, annotation_text=f"β*={ang['angulo_otimo_graus']}°",
                annotation_font_color=GREEN)
            fig_ang.update_layout(title="Ângulo Ótimo de Inclinação (Cálculo III)",
                xaxis_title="β (graus)", yaxis_title="kWh/m²/dia")
            theme(fig_ang, 240); st.plotly_chart(fig_ang, use_container_width=True)
            st.latex(rf"\beta^* \approx |\varphi| = {abs(LATITUDE)}°")
        # Temperatura
        temps = np.arange(25, 75, 1)
        fig_tmp = go.Figure(go.Scatter(x=temps, y=[perda_por_temperatura(float(t)) for t in temps],
            mode="lines", line=dict(color="#f87171", width=2),
            fill="tozeroy", fillcolor="rgba(248,113,113,0.07)"))
        fig_tmp.add_vline(x=TEMP_OPERACAO_LOCAL, line_dash="dash", line_color=AMBER,
            annotation_text=f"T_op={TEMP_OPERACAO_LOCAL}°C → {per['Temperatura']}% perda",
            annotation_font_color=AMBER)
        fig_tmp.update_layout(title="Perda por Temperatura — αT = −0,35%/°C (Física III)",
            xaxis_title="T (°C)", yaxis_title="Perda (%)")
        theme(fig_tmp, 220); st.plotly_chart(fig_tmp, use_container_width=True)

    # ── Tab 4: Estatística ────────────────────────────────
    with tab4:
        irr_v = list(IRRADIANCIA_MENSAL.values())
        irr_v_adj = [v * (HSP/HSP_MEDIA_ANUAL) for v in irr_v]
        med = np.mean(irr_v_adj); std = np.std(irr_v_adj)
        m1,m2,m3 = st.columns(3)
        m1.metric("HSP Médio Anual", f"{med:.2f} kWh/m²/dia")
        m2.metric("Desvio Padrão",   f"{std:.2f} kWh/m²/dia")
        m3.metric("Coef. Variação",  f"{std/med*100:.1f}%")
        fig_s = go.Figure()
        fig_s.add_trace(go.Bar(x=MESES, y=irr_v_adj, name="HSP",
            marker_color="rgba(245,158,11,0.75)", marker_line_color=AMBER, marker_line_width=1))
        fig_s.add_hline(y=med, line_dash="dash", line_color=GREEN,
            annotation_text=f"Média = {med:.2f}", annotation_font_color=GREEN)
        fig_s.add_hline(y=med+std, line_dash="dot", line_color=MUTED,
            annotation_text="+1σ", annotation_font_color=MUTED)
        fig_s.add_hline(y=med-std, line_dash="dot", line_color=MUTED,
            annotation_text="-1σ", annotation_font_color=MUTED)
        fig_s.update_layout(
            title=f"Irradiância Solar Mensal — {f['cidade']} (Atlas INPE 2017)",
            yaxis_title="HSP (kWh/m²/dia)")
        theme(fig_s, 300); st.plotly_chart(fig_s, use_container_width=True)
        # Distribuição normal TCL
        mu_g = ger_ano; sg = mu_g * 0.06
        xd = np.linspace(mu_g-3*sg, mu_g+3*sg, 280)
        yd = (1/(sg*np.sqrt(2*np.pi))) * np.exp(-0.5*((xd-mu_g)/sg)**2)
        lo95 = mu_g-1.96*sg; hi95 = mu_g+1.96*sg
        fig_n = go.Figure()
        fig_n.add_trace(go.Scatter(x=xd, y=yd, mode="lines",
            line=dict(color=AMBER, width=2), fill="tozeroy",
            fillcolor="rgba(245,158,11,0.10)"))
        fig_n.add_vrect(x0=lo95, x1=hi95, fillcolor="rgba(16,185,129,0.07)",
            layer="below", line_width=0, annotation_text="IC 95%",
            annotation_font_color=GREEN)
        fig_n.add_vline(x=mu_g, line_dash="dash", line_color=GREEN,
            annotation_text=f"μ = {mu_g:.0f} kWh/ano", annotation_font_color=GREEN)
        fig_n.update_layout(
            title=f"Distribuição Anual — IC 95%: [{lo95:.0f} ; {hi95:.0f}] kWh",
            xaxis_title="kWh/ano", yaxis_title="Densidade")
        theme(fig_n, 240); st.plotly_chart(fig_n, use_container_width=True)
        st.latex(r"\bar{X} \pm 1{,}96 \cdot \frac{\sigma}{\sqrt{n}} \quad \text{(TCL — }n=17\text{ anos)}")

    # ── Tab 5: Ambiental ──────────────────────────────────
    with tab5:
        ca,cb,cc = st.columns(3)
        ca.metric("CO₂ evitado/ano",   f"{co2['kg_co2_ano']:,.0f} kg")
        cb.metric("CO₂ em 25 anos",    f"{co2['ton_co2_25anos']:.1f} t")
        cc.metric("Equiv. em árvores", f"{co2['arvores_eq']:,} 🌳")
        fig_c = go.Figure(go.Scatter(
            x=[f"Ano {a}" for a in fc["anos"]],
            y=[co2["kg_co2_ano"]*a/1000 for a in fc["anos"]],
            mode="lines+markers", line=dict(color=GREEN, width=2.5),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
            marker=dict(size=4, color=GREEN)))
        fig_c.update_layout(title="CO₂ Evitado Acumulado (toneladas)", yaxis_title="CO₂ (t)")
        theme(fig_c, 240); st.plotly_chart(fig_c, use_container_width=True)
        st.markdown(f"""
        <div class="ibox-w" style="font-size:11px">
          🌱 Fator de emissão da rede elétrica: <strong>0,0884 kgCO₂/kWh</strong>
          (Fator Médio de Emissão do SIN — ONS, 2023).<br>
          Equivalência arbórea: 1 árvore ≈ 21,77 kgCO₂ absorvidos/ano.
        </div>""", unsafe_allow_html=True)

    # ── Disciplinas ───────────────────────────────────────
    st.markdown("""
    <div class="card" style="margin-top:16px">
      <div class="card-h">📚 Articulação com as Disciplinas</div>
      <div class="card-sub">Como cada componente curricular se aplica neste simulador:</div>
      <div class="disc-grid">
        <div class="dcard da"><h4>⚡ Física III</h4>
          <p>Efeito fotovoltaico, potência de pico (kWp), Performance Ratio com todas as perdas físicas, coeficiente de temperatura αT = −0,35%/°C. Dados de irradiação do Atlas (INPE, 2017).</p></div>
        <div class="dcard db"><h4>∫ Cálculo III</h4>
          <p>Otimização do ângulo de inclinação β*(φ,γ) = |φ| ≈ 13° por análise de função multivariável. Modelagem da curva de irradiância em função de β e azimute.</p></div>
        <div class="dcard dg"><h4>💰 Matemática Financeira</h4>
          <p>VPL, TIR (bissecção numérica), Payback simples e descontado, PMT para financiamento, juros compostos com inflação energética e depreciação 0,5%/ano dos módulos.</p></div>
        <div class="dcard dp"><h4>📊 Prob. e Estatística</h4>
          <p>Série histórica de 17 anos de irradiação (rede SONDA + INMET). Intervalo de Confiança de 95% via Teorema Central do Limite. Variabilidade interanual conforme Atlas cap.10.</p></div>
        <div class="dcard da full"><h4>🧠 Gestão do Conhecimento</h4>
          <p>Democratiza análises antes restritas a engenheiros especializados. Capacita produtores rurais, moradores e pequenas empresas do MT a tomar decisões fundamentadas sobre energia solar fotovoltaica. Código modularizado (data / calculations / financial / app) e documentado para reutilização por futuros alunos do BCT/UFMT — licença GNU GPL v3.0.</p></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Fórmulas ──────────────────────────────────────────
    with st.expander("📐 Fórmulas e Fundamentação Teórica"):
        f1,f2 = st.columns(2)
        with f1:
            st.markdown("**⚡ Física III**")
            st.latex(r"G_{mes} = P_{kWp}\cdot HSP_{mes}\cdot d_{mes}\cdot PR")
            st.latex(r"PR = 1-(\eta_{inv}+\eta_{cab}+\eta_{som}+\eta_{suj}+\alpha_T\Delta T)")
            st.markdown("**∫ Cálculo III**")
            st.latex(r"\beta^*=\arg\max_\beta I(\beta,\gamma)\approx|\varphi|")
        with f2:
            st.markdown("**💰 Matemática Financeira**")
            st.latex(r"VPL=-C_0+\sum_{t=1}^{25}\frac{FC_t}{(1+i)^t}")
            st.latex(r"PMT=PV\cdot\frac{r(1+r)^n}{(1+r)^n-1}")
            st.markdown("**📊 Probabilidade e Estatística**")
            st.latex(r"IC_{95\%}=\bar{X}\pm 1{,}96\cdot\frac{\sigma}{\sqrt{17}}")

    # ── Compartilhar ──────────────────────────────────────
    import urllib.parse, streamlit.components.v1 as components
    _url  = "https://calculadorasolarmatogro.streamlit.app"
    _txt  = (f"Simulei meu sistema solar com a SolarMT! "
             f"Sistema de {kwp:.1f} kWp, retorno em {pb['payback_simples_anos']} anos "
             f"e TIR de {tir}% a.a. — Feito por Atlas Kennedy · BCT/UFMT. Calcule o seu:")
    _te   = urllib.parse.quote(_txt); _ue = urllib.parse.quote(_url)
    _mail_body = urllib.parse.quote(
        f"{_txt}\n{_url}\n\n--- Resumo da Simulação ---\n"
        f"Cidade: {f['cidade']}\nConsumo: {consumo} kWh/mês\n"
        f"Painéis: {n} × 550 Wp = {kwp:.2f} kWp\n"
        f"Área necessária: {area_nec:.0f} m²\n"
        f"Geração anual: {ger_ano:,.0f} kWh\n"
        f"Economia mensal: R$ {eco_mes:,.0f}\n"
        f"Investimento: R$ {inv['custo_total']:,.0f}\n"
        f"Payback: {pb['payback_simples_anos']} anos | VPL: R$ {vpl['vpl']:,.0f} | TIR: {tir}%\n"
        f"CO₂ evitado 25 anos: {co2['ton_co2_25anos']:.1f} t")
    _mail = f"mailto:?subject={urllib.parse.quote('Simulação Solar — SolarMT')}&body={_mail_body}"

    st.markdown('<div style="font-size:12px;font-weight:600;color:#7a90b8;margin:16px 0 8px">📣 Compartilhar resultado</div>', unsafe_allow_html=True)
    components.html(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600&display=swap');
    .sr{{display:flex;gap:8px;flex-wrap:wrap;}}
    .sb{{display:flex;align-items:center;gap:6px;padding:9px 14px;border-radius:8px;border:none;
         font-family:'Sora',sans-serif;font-size:12px;font-weight:600;cursor:pointer;
         text-decoration:none;transition:opacity .15s,transform .15s;white-space:nowrap;}}
    .sb:hover{{opacity:.85;transform:translateY(-1px);}}
    .wa{{background:#25d366;color:#fff;}} .tw{{background:#1da1f2;color:#fff;}}
    .li{{background:#0077b5;color:#fff;}} .fb{{background:#1877f2;color:#fff;}}
    .em{{background:#374151;color:#e8f0ff;border:1px solid rgba(255,255,255,.15);}}
    .cp{{background:#111e38;color:#f59e0b;border:1px solid rgba(245,158,11,.4);}}
    .ok{{background:#10b981!important;color:#fff!important;border-color:transparent!important;}}
    </style>
    <div class="sr">
      <a class="sb wa" href="https://wa.me/?text={_te}%20{_ue}" target="_blank">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347zM12 0C5.373 0 0 5.373 0 12c0 2.124.558 4.117 1.532 5.843L.057 23.428a.5.5 0 0 0 .611.611l5.585-1.475A11.94 11.94 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.656-.51-5.176-1.4l-.37-.22-3.836 1.013 1.013-3.836-.22-.37A10 10 0 1 1 12 22z"/></svg>
        WhatsApp</a>
      <a class="sb tw" href="https://twitter.com/intent/tweet?text={_te}&url={_ue}" target="_blank">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        Twitter/X</a>
      <a class="sb li" href="https://www.linkedin.com/sharing/share-offsite/?url={_ue}" target="_blank">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        LinkedIn</a>
      <a class="sb em" href="{_mail}">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
        E-mail</a>
      <button class="sb cp" id="cpb"
        onclick="navigator.clipboard.writeText('{_url}').then(()=>{{var b=document.getElementById('cpb');b.textContent='✓ Copiado!';b.classList.add('ok');setTimeout(()=>{{b.textContent='🔗 Copiar link';b.classList.remove('ok');}},2500);}})">
        🔗 Copiar link</button>
    </div>""", height=52)

    st.markdown("---")
    br1, br2 = st.columns(2)
    with br1:
        if st.button("← Refazer Cálculo", type="secondary", use_container_width=True):
            st.session_state.step = 1; st.session_state.form = {}; st.rerun()
    with br2:
        components.html("""
        <button onclick="window.parent.window.print()"
          style="width:100%;padding:11px 22px;background:#f59e0b;color:#08101e;
                 border:none;border-radius:8px;font-family:'Sora',sans-serif;
                 font-size:13px;font-weight:600;cursor:pointer;min-height:44px;">
          🖨️ Imprimir / Salvar PDF
        </button>""", height=50)

# ══════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <div class="footer-brand">SolarMT — Lucas do Rio Verde / MT</div>
  <p>Criado por
    <a href="https://www.instagram.com/_atlaskennedydc" target="_blank">Atlas Kennedy</a>
    · Graduando em Ciência e Tecnologia ·
    <strong style="color:#e8f0ff">UFMT — Universidade Federal de Mato Grosso</strong>
  </p>
  <p style="font-size:10px;opacity:.6;margin-top:4px">
    Seminário Integrador IV · BCT/UFMT · 2026 · GNU GPL v3.0<br>
    Dados de irradiação: Atlas Brasileiro de Energia Solar, 2ª Ed. — INPE/LABREN (2017)<br>
    DOI: 10.34024/978851700089 · Tarifa: ENERGISA-MT · Emissão CO₂: ONS 2023
  </p>
</div>
""", unsafe_allow_html=True)
