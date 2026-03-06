import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# Configurações iniciais
st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# Conexão (Segura)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Função simples de busca
def buscar_dados(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    try:
        resp = requests.get(url_api, timeout=5)
        if resp.status_code == 200:
            dados = resp.json()
            lista = []
            for j in dados:
                for b in j.get('bookmakers', []):
                    lista.append({
                        'evento': f"{j['home_team']} vs {j['away_team']}",
                        'casa': b['title'],
                        'odd': b['markets'][0]['outcomes'][0]['price']
                    })
            return pd.DataFrame(lista)
    except:
        return pd.DataFrame()
    return pd.DataFrame()

# Interface
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = buscar_dados(liga)

# Exibição
if not df.empty:
    st.subheader("📜 Jogos Disponíveis")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("🎯 Simulador")
    with st.form("sim"):
        evento = st.selectbox("Jogo:", df['evento'].unique())
        valor = st.number_input("Valor (R$):", value=10.0)
        odd = st.number_input("Odd:", value=1.5)
        if st.form_submit_button("Registrar Aposta"):
            supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": valor, "odd": odd, "status": "pendente"}).execute()
            st.success("Registrado!")
else:
    st.warning("Nenhum dado retornado. Verifique a chave da API ou tente outra liga.")
