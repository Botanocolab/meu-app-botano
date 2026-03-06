import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# Configuração
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# 1. Carregamento de Dados Robusto
@st.cache_data(ttl=60)
def carregar_tudo(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    
    try:
        response = requests.get(url_api, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jogos = []
            for jogo in data:
                for bookie in jogo.get('bookmakers', []):
                    jogos.append({
                        'evento': f"{jogo['home_team']} vs {jogo['away_team']}",
                        'time_casa': bookie['title'],
                        'odd_casa': bookie['markets'][0]['outcomes'][0]['price']
                    })
            df = pd.DataFrame(jogos)
            if not df.empty:
                df['odd_media'] = df.groupby('evento')['odd_casa'].transform('mean')
                df['valor_aposta'] = df['odd_casa'] - df['odd_media']
            return df
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return pd.DataFrame()
    return pd.DataFrame()

# 2. Interface Principal
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados(liga)

# 3. Painel Sugestivo
st.subheader("🎯 Sugestões do Dia (Alta Probabilidade)")
if not df.empty and 'valor_aposta' in df.columns:
    sugestoes = df[df['valor_aposta'] > 0.1].sort_values(by='valor_aposta', ascending=False).head(3)
    if not sugestoes.empty:
        for i, row in sugestoes.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.info(f"Oportunidade: **{row['evento']}** | Casa: {row['time_casa']} | Valor: +{row['valor_aposta']:.2f}")
            if col2.button(f"Aprovar Aposta", key=f"sug_{i}"):
                supabase.table("apostas_simuladas").insert({"evento": row['evento'], "valor_apostado": 10.0, "odd": float(row['odd_casa']), "status": "pendente"}).execute()
                st.success("Registrado!")
                st.rerun()
    else:
        st.write("Nenhuma sugestão no momento.")
else:
    st.write("Analisando mercado...")

# 4. Tabela de Jogos + Filtro
st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro] if filtro != "Todas" else df
    st.dataframe(df_exibir, use_container_width=True)
else:
    st.warning("Dados não carregados.")

# 5. Simulador
st.divider()
st.subheader("🎯 Simulador")
with st.form("sim_form"):
    evento = st.selectbox("Jogo:", df['evento'].unique() if not df.empty else ["Nenhum dado"])
    valor = st.number_input("Valor (R$):", value=10.0)
    odd = st.number_input("Odd:", value=1.5)
    if st.form_submit_button("Registrar Aposta"):
        supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": valor, "odd": odd, "status": "pendente"}).execute()
        st.success("Aposta salva!")
        st.rerun()
