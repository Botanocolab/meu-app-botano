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

# 2. Carregar Dados com Integração API e Cálculo de Valor Seguro
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
            # Calcula valor apenas se tivermos dados
            if not df.empty:
                df['odd_media'] = df.groupby('evento')['odd_casa'].transform('mean')
                df['valor_aposta'] = df['odd_casa'] - df['odd_media']
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
    "soccer_epl"
])

df, df_historico = carregar_tudo(liga_escolhida)

# 3. Tabela de Jogos com Filtro Seguro
st.subheader("Jogos Disponíveis (Foco em Valor)")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro_casa = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro_casa] if filtro_casa != "Todas" else df
    
    # AQUI ESTÁ A CORREÇÃO: Verifica se 'valor_aposta' existe antes de estilizar
    if 'valor_aposta' in df_exibir.columns:
        st.dataframe(df_exibir.style.background_gradient(subset=['valor_aposta'], cmap='RdYlGn'), use_container_width=True)
    else:
        st.dataframe(df_exibir, use_container_width=True)
else:
    st.info("Nenhum jogo disponível no momento.")

# ... (restante do código do simulador e histórico igual)
