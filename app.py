import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. CONFIGURAÇÃO PREMIUM
st.set_page_config(page_title="Botano+ | Engine", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0f0f0f; color: white; }
    h1 { font-weight: 900; letter-spacing: -1px; }
    .botano-card {
        background: #1e1e1e; border-radius: 18px; padding: 20px; 
        margin-bottom: 16px; border-left: 5px solid #ff5a2a;
        box-shadow: 0 8px 25px rgba(0,0,0,0.45);
    }
    .botano-metric { font-size: 14px; color: #c9c9c9; }
    .botano-strong { font-weight: 800; color: #ff5a2a; font-size: 1.1em; }
    div.stButton > button { background: linear-gradient(135deg,#ff5a2a,#ff7a1a); 
    border-radius: 12px; border: none; color: white; font-weight: 700; width: 100%; }
</style>
""", unsafe_allow_html=True)

# 2. HEADER E SUPABASE
st.markdown("""
<h1 style='display:flex;align-items:center;gap:10px'>
⚡ <span style="color:#ff5a2a">BOTANO+</span>
<span style="font-size:18px;color:#c9c9c9;font-weight:400">Smart Betting Engine</span>
</h1>
""", unsafe_allow_html=True)

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# 3. MOTOR DE CÁLCULO
def calcular_ev_e_score(odd, fair_prob):
    # EV = (Probabilidade Justa * Odd) - 1
    ev = (fair_prob * odd) - 1
    # Score Botano baseado na fórmula: 
    # $Score = (EV \% \times 8) + (FairProb \times 100 \times 0.3) - (Odd \times 1.2)$
    score = (ev * 100 * 8) + (fair_prob * 100 * 0.3) - (odd * 1.2)
    return round(ev * 100, 2), round(score, 1)

def buscar_odds(liga):
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {"apiKey": st.secrets["ODDS_API_KEY"], "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200: return pd.DataFrame(r.json()), None
        return pd.DataFrame(), f"Erro API {r.status_code}"
    except Exception as e: return pd.DataFrame(), str(e)

# 4. INTERFACE V3
ligas = {"Brasileirão Série A": "soccer_brazil_campeonato", "Premier League": "soccer_epl"}
liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))
df, erro = buscar_odds(ligas[liga_nome])

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Oportunidades com Valor")
    if erro: st.error(erro)
    elif not df.empty:
        for _, row in df.head(10).iterrows():
            # Simplificação de fair probability baseada na casa principal
            # Nota: Em V4, integraremos média de todos os bookmakers
            best_odd = 2.05 # Mocked para demonstração
            fair_prob = 0.52 
            ev_pct, score = calcular_ev_e_score(best_odd, fair_prob)
            confianca = "Alta" if ev_pct > 6 else "Média"
            
            st.markdown(f"""
            <div class="botano-card">
                <div class="botano-strong">{row['home_team']} x {row['away_team']}</div>
                <div class="botano-metric">
                    Seleção: {row['home_team']} | Odd: {best_odd} | 
                    EV: <span style="color:#ff5a2a">{ev_pct}%</span> | 
                    Score: {score} | Confiança: {confianca}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Apostar {row['home_team']}", key=row['id']):
                st.success("Aposta registrada!")
    else: st.info("Buscando dados...")

with col_right:
    st.subheader("🎯 Simulador & Gestão")
    with st.form("sim"):
        val = st.number_input("Valor (R$):", 10.0)
        odd = st.number_input("Odd:", 1.5)
        st.form_submit_button("Registrar Aposta")
    st.metric("ROI Estimado", "+12.4%")
    st.metric("Win Rate", "58%")
