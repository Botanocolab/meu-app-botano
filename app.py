import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# Configurações
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# Função de busca segura
def buscar_dados(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    try:
        resp = requests.get(url_api, timeout=5)
        if resp.status_code == 200:
            dados = resp.json()
            # Processa os dados de forma simples
            lista = []
            for j in dados:
                for b in j.get('bookmakers', []):
                    lista.append({
                        'evento': f"{j['home_team']} vs {j['away_team']}",
                        'time_casa': b['title'],
                        'odd': b['markets'][0]['outcomes'][0]['price']
                    })
            return pd.DataFrame(lista)
    except:
        return pd.DataFrame() # Retorna dataframe vazio se der erro
    return pd.DataFrame()

# Execução
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = buscar_dados(liga)

# Interface sempre presente
st.subheader("🎯 Sugestões do Dia")
if not df.empty:
    st.write("Dados carregados com sucesso!")
    # Aqui você pode filtrar suas sugestões
else:
    st.info("Aguardando dados da API ou API indisponível no momento.")

st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Tabela vazia: verifique se a liga escolhida possui jogos ativos.")

st.subheader("🎯 Simulador")
with st.form("sim"):
    if not df.empty:
        jogo = st.selectbox("Jogo:", df['evento'].unique())
        valor = st.number_input("Valor:", value=10.0)
        if st.form_submit_button("Registrar"):
            st.success("Aposta registrada!")
    else:
        st.write("Sem jogos para simular.")
