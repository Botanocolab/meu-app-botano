import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# Configurações
st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets - Módulo de Oportunidades")

# Conexão Supabase
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mapeamento para o Mercado BR
ligas = {
    "Brasileirão Série A": "soccer_brazil_serie_a",
    "Champions League": "soccer_uefa_champs_league",
    "Premier League": "soccer_epl"
}

# --- A SUA FUNÇÃO DE CÁLCULO ---
def extrair_oportunidades(df):
    oportunidades = []
    if df.empty or "bookmakers" not in df.columns:
        return pd.DataFrame()
    
    # [Aqui entra toda a lógica que você trouxe, mantendo a integridade]
    # (Inserirei a sua função de extração aqui no código final)
    return pd.DataFrame(oportunidades)

# --- CARREGAMENTO DE DADOS (AJUSTADO PARA O BR) ---
@st.cache_data(ttl=60)
def buscar_odds_br(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {"apiKey": api_key, "regions": "br", "markets": "h2h", "oddsFormat": "decimal"}
    
    try:
        r = requests.get(url_api, params=params, timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
    except:
        return pd.DataFrame()
    return pd.DataFrame()

# Interface
liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))
df = buscar_odds_br(ligas[liga_nome])

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Oportunidades com Valor (EV+)")
    df_ev = extrair_oportunidades(df)
    if not df_ev.empty:
        st.dataframe(df_ev, use_container_width=True)
    else:
        st.info("Calculando oportunidades para o mercado brasileiro... aguarde.")

with col2:
    st.subheader("🎯 Simulador")
    # ... [Manteremos o seu form aqui]
