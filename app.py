import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. Configuração inicial sem falhas
st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# Conexão (Verifique se as chaves no Streamlit Cloud estão exatas)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. Busca protegida (Se der erro, ele retorna um DF vazio, não o erro)
@st.cache_data(ttl=60)
def carregar_dados(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    try:
        r = requests.get(url_api, timeout=5)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
    except:
        return pd.DataFrame()
    return pd.DataFrame()

# 3. Interface com travas de segurança
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados(liga)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📜 Jogos Disponíveis")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum jogo encontrado no momento. A API pode estar indisponível.")

with col2:
    st.subheader("🎯 Simulador")
    with st.form("sim_form"):
        # Se o DF estiver vazio, desabilita a seleção para evitar erro
        if not df.empty:
            evento = st.selectbox("Jogo:", df['home_team'].tolist())
            valor = st.number_input("Valor (R$):", value=10.0)
            odd = st.number_input("Odd:", value=1.5)
            submit = st.form_submit_button("Registrar Aposta")
            if submit:
                supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": float(valor), "odd": float(odd), "status": "pendente"}).execute()
                st.success("Aposta registrada!")
        else:
            st.write("Aguardando dados para simular.")
            st.form_submit_button("Registrar Aposta", disabled=True)
