import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. Configurações e Conexão
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")

# Título
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 Botano+ nas bets</h1>", unsafe_allow_html=True)

# 2. Carregamento de Dados (Mais robusto)
@st.cache_data(ttl=60)
def carregar_dados_api(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jogos = []
            for j in data:
                for b in j.get('bookmakers', []):
                    jogos.append({
                        'evento': f"{j['home_team']} vs {j['away_team']}",
                        'casa': b['title'],
                        'odd': b['markets'][0]['outcomes'][0]['price']
                    })
            return pd.DataFrame(jogos)
    except Exception as e:
        return pd.DataFrame()
    return pd.DataFrame()

# 3. Interface Principal
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados_api(liga)

# Layout em colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📜 Jogos Disponíveis")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Dados não carregados. A API pode estar indisponível ou sem jogos para esta liga.")

with col2:
    st.subheader("🎯 Simulador")
    with st.form("simulador_form"):
        evento_selecionado = st.selectbox("Evento:", df['evento'].unique() if not df.empty else ["Aguardando dados..."])
        valor = st.number_input("Valor (R$):", value=10.0)
        odd_manual = st.number_input("Odd:", value=1.5)
        
        if st.form_submit_button("Registrar Aposta"):
            if not df.empty:
                supabase.table("apostas_simuladas").insert({
                    "evento": evento_selecionado, 
                    "valor_apostado": float(valor), 
                    "odd": float(odd_manual),
                    "status": "pendente"
                }).execute()
                st.success("Aposta registrada!")
            else:
                st.error("Erro: Nenhum dado disponível para registrar.")
