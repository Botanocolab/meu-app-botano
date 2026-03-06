import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# Config
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("📊 Botano+ nas bets")

# Carregamento com proteção total
def carregar_dados(liga):
    try:
        api_key = st.secrets["ODDS_API_KEY"]
        url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
        resp = requests.get(url_api, timeout=10)
        if resp.status_code == 200:
            return pd.DataFrame(resp.json()) # Simplificado para testar conexão
        return None
    except:
        return None

liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league"])
df = carregar_dados(liga)

# Se nada funcionar, pelo menos o código não explode
if df is not None and not df.empty:
    st.write("Dados recebidos!")
    st.dataframe(df)
else:
    st.error("A API não retornou dados. Tente trocar a liga ou verifique a chave no Secret.")
