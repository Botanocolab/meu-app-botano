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

# 2. Carregar Dados
def carregar_tudo(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            jogos_list = []
            for jogo in response.json():
                for bookie in jogo.get('bookmakers', []):
                    jogos_list.append({
                        'evento': f"{jogo['home_team']} vs {jogo['away_team']}",
                        'time_casa': bookie['title'],
                        'odd_casa': bookie['markets'][0]['outcomes'][0]['price']
                    })
            df = pd.DataFrame(jogos_list)
            df['odd_media'] = df.groupby('evento')['odd_casa'].transform('mean')
            df['valor_aposta'] = df['odd_casa'] - df['odd_media']
            return df
    except:
        return pd.DataFrame(supabase.table("apostas").select("*").execute().data)
    return pd.DataFrame()

# Liga e Filtro
liga_escolhida = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_tudo(liga_escolhida)

# 3. Painel Sugestivo (Aprovação Rápida)
st.subheader("🎯 Sugestões do Dia (Alta Probabilidade)")
if not df.empty and 'valor_aposta' in df.columns:
    sugestoes = df[df['valor_aposta'] > 0.20].sort_values(by='valor_aposta', ascending=False).head(3)
    for i, row in sugestoes.iterrows():
        col1, col2 = st.columns([4, 1])
        col1.info(f"Oportunidade: **{row['evento']}** | Casa: {row['time_casa']} | Odd: {row['odd_casa']} (Valor: +{row['valor_aposta']:.2f})")
        if col2.button(f"Aprovar Aposta", key=f"sug_{i}"):
            supabase.table("apostas_simuladas").insert({"evento": row['evento'], "valor_apostado": 10.0, "odd": float(row['odd_casa']), "status": "pendente"}).execute()
            st.success("Aposta registrada!")
            st.rerun()
else:
    st.info("Nenhuma sugestão no momento. Analisando mercado...")

# 4. Tabela com Filtro de Casas
st.subheader("📜 Jogos Disponíveis")
casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist()) if not df.empty else ["Todas"]
filtro = st.selectbox("Filtrar por Casa de Aposta:", casas)
df_exibir = df[df['time_casa'] == filtro] if filtro != "Todas" else df
st.dataframe(df_exibir, use_container_width=True)

# 5. Simulador
with st.form("simulador_form"):
    evento = st.selectbox("Jogo:", df['evento'].unique() if not df.empty else [])
    valor = st.number_input("Valor (R$):", value=10.0)
    odd = st.number_input("Odd:", value=1.5)
    if st.form_submit_button("Registrar Manualmente"):
        supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": valor, "odd": odd, "status": "pendente"}).execute()
        st.rerun()

# 6. Histórico
st.subheader("📈 Histórico")
df_hist = pd.DataFrame(supabase.table("apostas_simuladas").select("*").execute().data)
if not df_hist.empty:
    st.dataframe(df_hist)
