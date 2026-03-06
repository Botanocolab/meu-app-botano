import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# Configurações
st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# Conexão Supabase
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Função de busca protegida
@st.cache_data(ttl=60)
def carregar_dados(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    try:
        r = requests.get(url_api, timeout=5)
        if r.status_code == 200:
            data = r.json()
            lista = []
            for j in data:
                for b in j.get('bookmakers', []):
                    lista.append({
                        'evento': f"{j['home_team']} vs {j['away_team']}",
                        'casa': b['title'],
                        'odd': b['markets'][0]['outcomes'][0]['price']
                    })
            return pd.DataFrame(lista)
    except:
        pass
    return pd.DataFrame()

# Lógica de interface
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados(liga)

# Área de Jogos e Simulador lado a lado
if not df.empty:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📜 Jogos Disponíveis")
        st.dataframe(df, use_container_width=True)
    with col2:
        st.subheader("🎯 Simulador")
        with st.form("sim_form"):
            evento = st.selectbox("Jogo:", df['evento'].unique())
            valor = st.number_input("Valor (R$):", value=10.0)
            odd = st.number_input("Odd:", value=1.5)
            if st.form_submit_button("Registrar"):
                supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": float(valor), "odd": float(odd), "status": "pendente"}).execute()
                st.success("Registrado!")
else:
    st.warning("⚠️ Nenhuma partida encontrada na API para esta liga neste momento.")
