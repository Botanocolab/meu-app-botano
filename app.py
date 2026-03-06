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

# 2. Carregar Dados de forma segura
def carregar_dados(liga):
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
            # Cálculo de valor apenas se houver dados
            if not df.empty:
                df['odd_media'] = df.groupby('evento')['odd_casa'].transform('mean')
                df['valor_aposta'] = df['odd_casa'] - df['odd_media']
            return df
    except:
        return pd.DataFrame(supabase.table("apostas").select("*").execute().data)
    return pd.DataFrame()

# Liga e Filtro
liga_escolhida = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados(liga_escolhida)
df_historico = pd.DataFrame(supabase.table("apostas_simuladas").select("*").execute().data)

# 3. Jogos Disponíveis (Prioridade: deve aparecer sempre)
st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro] if filtro != "Todas" else df
    st.dataframe(df_exibir, use_container_width=True)
else:
    st.info("Nenhum jogo encontrado no momento.")

# 4. Painel Sugestivo (Aparece se houver cálculo de valor)
if not df.empty and 'valor_aposta' in df.columns:
    st.subheader("🎯 Sugestões do Dia (Alta Probabilidade)")
    sugestoes = df[df['valor_aposta'] > 0.1].sort_values(by='valor_aposta', ascending=False).head(3)
    if not sugestoes.empty:
        for i, row in sugestoes.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.info(f"Oportunidade: **{row['evento']}** | Casa: {row['time_casa']} | Odd: {row['odd_casa']} (Valor: +{row['valor_aposta']:.2f})")
            if col2.button(f"Aprovar Aposta", key=f"sug_{i}"):
                supabase.table("apostas_simuladas").insert({"evento": row['evento'], "valor_apostado": 10.0, "odd": float(row['odd_casa']), "status": "pendente"}).execute()
                st.rerun()
    else:
        st.write("Nenhuma sugestão de valor alto no momento.")

# 5. Simulador
st.divider()
st.subheader("🎯 Simulador")
with st.form("sim_form"):
    evento = st.selectbox("Jogo:", df['evento'].unique() if not df.empty else [])
    valor = st.number_input("Valor (R$):", value=10.0)
    odd = st.number_input("Odd:", value=1.5)
    if st.form_submit_button("Registrar"):
        supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": float(valor), "odd": float(odd), "status": "pendente"}).execute()
        st.rerun()
