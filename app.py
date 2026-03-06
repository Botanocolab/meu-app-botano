import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(page_title="Botano+ nas bets", layout="wide")

# =====================================
# CSS CUSTOMIZADO
# =====================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #111111 0%, #191919 100%);
        color: #ffffff;
    }
    h1, h2, h3 {
        color: #ff5a2a !important;
        font-weight: 800 !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #ff5a2a 0%, #ff7a1a 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        width: 100% !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
    }
    .botano-card {
        background: #202020;
        border: 1px solid #333333;
        border-left: 4px solid #ff5a2a;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.22);
    }
    .botano-metric { font-size: 0.95rem; color: #d0d0d0; margin-bottom: 4px; }
    .botano-strong { color: #ffffff; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# =====================================
# TÍTULO E SUPABASE
# =====================================
st.title("📊 Botano+ nas bets")

SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ligas = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Champions League": "soccer_uefa_champs_league",
    "Premier League": "soccer_epl"
}

# =====================================
# FUNÇÕES
# =====================================
@st.cache_data(ttl=60)
def buscar_odds(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    if not api_key:
        return pd.DataFrame(), "Chave da API não encontrada."

    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json()), None
        return pd.DataFrame(), f"Erro API {r.status_code}: {r.text}"
    except Exception as e:
        return pd.DataFrame(), f"Erro: {str(e)}"

def registrar_aposta(evento, selecao, odd, valor):
    supabase.table("apostas_simuladas").insert({
        "evento": evento, 
        "selecao": selecao, 
        "valor_apostado": float(valor),
        "odd": float(odd), 
        "status": "pendente"
    }).execute()

# =====================================
# INTERFACE
# =====================================
liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))
df, erro = buscar_odds(ligas[liga_nome])

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Jogos Disponíveis")
    if erro:
        st.error(erro)
    elif not df.empty:
        st.dataframe(df[['home_team', 'away_team', 'commence_time']])
    else:
        st.info("Nenhum dado retornado no momento.")

with col2:
    st.subheader("🎯 Simulador")
    with st.form("sim_form"):
        if not df.empty and "home_team" in df.columns:
            jogos = [f"{r['home_team']} x {r['away_team']}" for _, r in df.iterrows()]
            evento = st.selectbox("Jogo:", jogos)
            valor = st.number_input("Valor (R$):", value=10.0)
            odd = st.number_input("Odd:", value=1.5)
            
            if st.form_submit_button("Registrar Aposta"):
                registrar_aposta(evento, "manual", odd, valor)
                st.success("Aposta registrada!")
        else:
            st.write("Aguardando dados da API.")
            st.form_submit_button("Registrar Aposta", disabled=True)
