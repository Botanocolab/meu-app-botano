import streamlit as st
import pandas as pd
import requests
from supabase import create_client

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets - VERSÃO NOVA")

# Supabase
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ligas = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Champions League": "soccer_uefa_champs_league",
    "Premier League": "soccer_epl"
}

@st.cache_data(ttl=60)
def carregar_dados(liga):
    api_key = st.secrets.get("ODDS_API_KEY")

    if not api_key:
        return pd.DataFrame(), "ODDS_API_KEY não encontrada no secrets."

    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url_api, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                return pd.DataFrame(data), None
            return pd.DataFrame(), "A API respondeu com sucesso, mas não retornou jogos para essa liga."

        try:
            erro_api = r.json()
        except Exception:
            erro_api = r.text

        return pd.DataFrame(), f"Erro {r.status_code} na API: {erro_api}"

    except requests.exceptions.RequestException as e:
        return pd.DataFrame(), f"Erro de conexão: {str(e)}"

liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))
liga = ligas[liga_nome]

df, erro = carregar_dados(liga)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📜 Jogos Disponíveis")

    if erro:
        st.error(erro)

    if not df.empty:
        colunas_visiveis = [c for c in ["home_team", "away_team", "commence_time"] if c in df.columns]
        if colunas_visiveis:
            st.dataframe(df[colunas_visiveis], use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum jogo encontrado no momento.")

with col2:
    st.subheader("🎯 Simulador")

    with st.form("sim_form"):
        if not df.empty and "home_team" in df.columns and "away_team" in df.columns:
            opcoes_jogos = [
                f"{row['home_team']} x {row['away_team']}"
                for _, row in df.iterrows()
            ]

            evento = st.selectbox("Jogo:", opcoes_jogos)
            valor = st.number_input("Valor (R$):", value=10.0, min_value=0.0)
            odd = st.number_input("Odd:", value=1.5, min_value=1.01)
            submit = st.form_submit_button("Registrar Aposta")

            if submit:
                supabase.table("apostas_simuladas").insert({
                    "evento": evento,
                    "valor_apostado": float(valor),
                    "odd": float(odd),
                    "status": "pendente"
                }).execute()
                st.success("Aposta registrada!")
        else:
            st.write("Aguardando dados para simular.")
            st.form_submit_button("Registrar Aposta", disabled=True)
