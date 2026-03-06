import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. Configuração
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# 2. Carregar Dados com Integração API (Agora com suporte a ligas)
def carregar_tudo(liga="soccer_brazil_serie_a"):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jogos_list = []
            for jogo in data:
                if 'bookmakers' in jogo:
                    for bookie in jogo['bookmakers']:
                        jogos_list.append({
                            'evento': f"{jogo['home_team']} vs {jogo['away_team']}",
                            'time_casa': bookie['title'],
                            'odd_casa': bookie['markets'][0]['outcomes'][0]['price']
                        })
            df = pd.DataFrame(jogos_list)
        else:
            df = pd.DataFrame(supabase.table("apostas").select("*").execute().data)
    except:
        df = pd.DataFrame(supabase.table("apostas").select("*").execute().data)

    historico = pd.DataFrame(supabase.table("apostas_simuladas").select("*").execute().data)
    return df, historico

# Seleção de Liga
liga_escolhida = st.selectbox("Escolha a Liga para monitorar:", [
    "soccer_brazil_serie_a", 
    "soccer_uefa_champs_league", 
    "soccer_epl" # Premier League
])

df, df_historico = carregar_tudo(liga_escolhida)

# Diagnóstico de Casas
if st.checkbox("🔍 Ver casas disponíveis nesta liga"):
    if not df.empty:
        st.write(f"Casas detectadas: {sorted(df['time_casa'].unique().tolist())}")

# 3. Tabela de Jogos com Filtro
st.subheader("Jogos Disponíveis")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro_casa = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro_casa] if filtro_casa != "Todas" else df
    st.dataframe(df_exibir, use_container_width=True)

# 4. Simulador (Mantido)
# ... (seu código do simulador continua igual)
