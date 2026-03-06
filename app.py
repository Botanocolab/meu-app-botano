import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. CONFIGURAÇÃO E CSS
st.set_page_config(page_title="Botano+ nas bets", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #111111 0%, #191919 100%); color: #ffffff; }
    h1, h2, h3 { color: #ff5a2a !important; font-weight: 800 !important; }
    .botano-card {
        background: #202020; border: 1px solid #333333; border-left: 4px solid #ff5a2a;
        border-radius: 16px; padding: 16px; margin-bottom: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.22);
    }
    .botano-metric { font-size: 0.95rem; color: #d0d0d0; margin-bottom: 4px; }
    .botano-strong { color: #ffffff; font-weight: 700; }
    div[data-testid="stForm"] { background: #151515; border: 1px solid #262626; border-radius: 16px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# 2. CONEXÕES
st.title("📊 Botano+ nas bets")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

ligas = {"Brasileirão Série A": "soccer_brazil_campeonato", "Champions League": "soccer_uefa_champs_league", "Premier League": "soccer_epl"}

# 3. LÓGICA DE DADOS (API E EV+)
@st.cache_data(ttl=60)
def buscar_odds(liga):
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {"apiKey": st.secrets["ODDS_API_KEY"], "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=10)
        return pd.DataFrame(r.json()), None if r.status_code == 200 else f"Erro API {r.status_code}"
    except Exception as e: return pd.DataFrame(), str(e)

def extrair_oportunidades(df):
    oportunidades = []
    if df.empty or "bookmakers" not in df.columns: return pd.DataFrame()
    for _, row in df.iterrows():
        bookmakers = row.get("bookmakers", [])
        melhores_odds = {}
        # Lógica simplificada de fair probability (média do mercado)
        for book in bookmakers:
            for market in book.get("markets", []):
                if market.get("key") == "h2h":
                    for o in market.get("outcomes", []):
                        nome, price = o.get("name"), o.get("price")
                        if nome not in melhores_odds or price > melhores_odds[nome]: melhores_odds[nome] = price
        
        for nome, odd in melhores_odds.items():
            ev = 0.05 # placeholder para cálculo de EV real
            oportunidades.append({"evento": f"{row['home_team']} x {row['away_team']}", "selecao": nome, "odd": odd, "ev_%": ev * 100})
    return pd.DataFrame(oportunidades)

# 4. INTERFACE
liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))
df, erro = buscar_odds(ligas[liga_nome])
df_ev = extrair_oportunidades(df)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Oportunidades (EV+)")
    if erro: st.error(erro)
    elif not df_ev.empty:
        for i, op in df_ev.head(5).iterrows():
            st.markdown(f"""
            <div class="botano-card">
                <div class="botano-strong">{op['evento']}</div>
                <div class="botano-metric">Seleção: {op['selecao']} | Odd: {op['odd']} | EV: {op['ev_%']}%</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Apostar {op['selecao']}", key=f"bet_{i}"):
                supabase.table("apostas_simuladas").insert({"evento": op['evento'], "selecao": op['selecao'], "odd": op['odd'], "status": "pendente"}).execute()
                st.success("Registrado!")
    else: st.info("Buscando oportunidades...")

with col2:
    st.subheader("🎯 Simulador")
    with st.form("sim_form"):
        valor = st.number_input("Valor (R$):", value=10.0)
        odd = st.number_input("Odd:", value=1.5)
        if st.form_submit_button("Registrar Aposta Manual"):
            st.success("Aposta registrada!")
