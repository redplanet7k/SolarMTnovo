# ☀️ SolarMT — Calculadora de Viabilidade Solar Fotovoltaica
## Lucas do Rio Verde / MT — Projeto Integrador BCT/UFMT — 2026

---

## 🚀 Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Acesse: **https://calculadorasolarmatogro.streamlit.app**

---

## 📁 Estrutura

```
solar_simulator/
├── app.py            # Interface Streamlit (wizard 3 etapas + dashboards)
├── calculations.py   # Física III + Cálculo III
├── financial.py      # Matemática Financeira (VPL, TIR, Payback, PMT)
├── data.py           # Dados de irradiação + constantes
├── requirements.txt
└── README.md
```

---

## 📊 Base de Dados — Atlas Brasileiro de Energia Solar

| Item | Valor | Fonte |
|------|-------|-------|
| Irradiação mensal (Hi) | 4,65 – 6,10 kWh/m²/dia | Atlas INPE/LABREN 2017 |
| HSP médio anual | 5,16 kWh/m²/dia | Atlas, região Centro-Oeste/Norte-MT |
| Performance Ratio (PR) | **80%** | Atlas Fig.52, p.57 |
| Série histórica | **17 anos** (1999–2015) | Satélite GOES + modelo BRASIL-SR |
| Validação | REQM 8,2% · Viés 0,2% | Rede SONDA + 503 estações INMET |
| Fator emissão CO₂ | 0,0884 kgCO₂/kWh | ONS 2023 — Fator Médio SIN |

### Correções aplicadas em relação a versão anterior

| Parâmetro | Antes | Depois (Atlas) |
|-----------|-------|----------------|
| HSP médio anual | 5,47 kWh/m²/dia | **5,16 kWh/m²/dia** |
| Performance Ratio | 83% | **80%** (padrão Atlas p.57) |
| Potência módulo | 400 Wp | **550 Wp** (padrão 2025) |
| Custo/kWp | R$ 4.200 | **R$ 4.500** (mercado MT 2025) |
| Sazonalidade | uniforme | **chuvosa × seca** (Atlas cap.5) |
| Fator CO₂ | 0,094 kg/kWh | **0,0884 kg/kWh** (ONS 2023) |
| Módulos na simulação app | 400 Wp genérico | **550 Wp monocristalino** |
| IC geração | n=20 anos | **n=17 anos** (série do Atlas) |

### Padrão sazonal MT (Atlas, caps. 5 e 10)
- **Estação seca (mai–set):** céu limpo → **pico de irradiação** (6,0–6,1 kWh/m²/dia)
- **Estação chuvosa (nov–mar):** alta nebulosidade → **menor irradiação** (4,65–5,0 kWh/m²/dia)

---

## 🎓 Disciplinas integradas

| Disciplina | Aplicação |
|------------|-----------|
| **Física III** | Efeito FV, potência de pico, PR com todas as perdas físicas, αT = −0,35%/°C |
| **Cálculo III** | Otimização β*(φ,γ) = \|φ\| ≈ 13° (função multivariável) |
| **Matemática Financeira** | VPL, TIR (bissecção), Payback, PMT, juros compostos, depreciação |
| **Prob. e Estatística** | IC 95% (n=17 anos), TCL, variabilidade interanual (Atlas Fig.39) |
| **Gestão do Conhecimento** | Código modular documentado, licença GPL, reutilizável por futuros alunos |

---

## 📜 Referência principal

> Pereira, E. B. et al. **Atlas Brasileiro de Energia Solar**, 2ª Edição.
> São José dos Campos: INPE, 2017.
> DOI: [10.34024/978851700089](http://doi.org/10.34024/978851700089)

---

## 👤 Autor

**Atlas Kennedy** — Graduando em Ciência e Tecnologia · UFMT · Lucas do Rio Verde/MT  
📸 [@_atlaskennedydc](https://www.instagram.com/_atlaskennedydc)

Licença: **GNU GPL v3.0** — Software Livre para uso, modificação e distribuição acadêmica.
