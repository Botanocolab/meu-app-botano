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

# 2. Carregar Dados com Integração API e Cálculo de Valor
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
            
            # CÁLCULO DE VALOR (Value Bet)
            if not df.empty:
                # Calcula a média das odds por evento
                df['odd_media'] = df.groupby('evento')['odd_casa'].transform('mean')
                # O "Valor" é quanto essa casa está pagando a mais que a média do mercado
                df['valor_aposta'] = df['odd_casa'] - df['odd_media']
                # Ordena pelas melhores oportunidades
                df = df.sort_values(by='valor_aposta', ascending=False)
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

# 3. Tabela de Jogos com Destaque de Valor
st.subheader("Jogos Disponíveis (Foco em Valor)")
if not df.empty:
    # Filtro de casas
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro_casa = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro_casa] if filtro_casa != "Todas" else df
    
    # Exibe com cores condicionais no valor (valores positivos em verde)
    st.dataframe(df_exibir.style.background_gradient(subset=['valor_aposta'], cmap='RdYlGn'), use_container_width=True)
else:
    st.info("Nenhum jogo disponível no momento.")

# 4. Simulador (Mantido)
st.divider()
st.subheader("🎯 Simulador de Apostas")
with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique() if not df.empty else ["Nenhum jogo"])
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    resultado = st.selectbox("Resultado da Aposta:", ["pendente", "ganha", "perdida"])
    if st.form_submit_button("Registrar Aposta"):
        supabase.table("apostas_simuladas").insert({
            "evento": str(evento_escolhido), "valor_apostado": float(valor), 
            "odd": float(odd), "status": resultado
        }).execute()
        st.success("Aposta registrada!")
        st.rerun()
