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

# 2. Carregar Dados (Função única e corrigida)
def carregar_dados_esportivos(liga):
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
        return pd.DataFrame()
    return pd.DataFrame()

# 3. Interface - Chamada direta e segura
liga = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados_esportivos(liga)

# 4. Painel Sugestivo
st.subheader("🎯 Sugestões do Dia (Alta Probabilidade)")
if not df.empty and 'valor_aposta' in df.columns:
    sugestoes = df[df['valor_aposta'] > 0.05].sort_values(by='valor_aposta', ascending=False).head(3)
    if not sugestoes.empty:
        for i, row in sugestoes.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.info(f"Oportunidade: {row['evento']} | {row['time_casa']} | Valor: +{row['valor_aposta']:.2f}")
            if col2.button(f"Aprovar #{i}", key=f"btn_{i}"):
                supabase.table("apostas_simuladas").insert({"evento": row['evento'], "valor_apostado": 10.0, "odd": float(row['odd_casa']), "status": "pendente"}).execute()
                st.rerun()
    else:
        st.write("Sem sugestões no momento.")
else:
    st.write("Dados em processamento...")

# 5. Tabela Principal
st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].unique().tolist())
    filtro = st.selectbox("Filtrar por Casa:", casas)
    exibir = df[df['time_casa'] == filtro] if filtro != "Todas" else df
    st.dataframe(exibir, use_container_width=True)
else:
    st.warning("Nenhum dado retornado da API.")

# 6. Simulador
st.subheader("🎯 Simulador")
with st.form("sim"):
    evento = st.selectbox("Jogo:", df['evento'].unique() if not df.empty else [])
    valor = st.number_input("Valor:", value=10.0)
    odd = st.number_input("Odd:", value=1.5)
    if st.form_submit_button("Registrar"):
        supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": valor, "odd": odd, "status": "pendente"}).execute()
        st.rerun()
