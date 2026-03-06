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

# 2. Carregar Dados com Integração API
def carregar_tudo(liga="soccer_brazil_serie_a"):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    
    df = pd.DataFrame()
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jogos_list = []
            for jogo in data:
                if 'bookmakers' in jogo:
                    for bookie in jogo['bookmakers']:
                        jogos_list.append({
                            'evento': f"{jogo['home_team']} vs {jogo['away_team']}",
                            'time_casa': bookie['title'],
                            'odd_casa': bookie['markets'][0]['outcomes'][0]['price']
                        })
            df = pd.DataFrame(jogos_list)
            if not df.empty:
                df['odd_media'] = df.groupby('evento')['odd_casa'].transform('mean')
                df['valor_aposta'] = df['odd_casa'] - df['odd_media']
    except:
        # Fallback: tenta buscar do Supabase
        dados_db = supabase.table("apostas").select("*").execute().data
        df = pd.DataFrame(dados_db)

    historico = pd.DataFrame(supabase.table("apostas_simuladas").select("*").execute().data)
    return df, historico

# Seleção de Liga
liga_escolhida = st.selectbox("Escolha a Liga para monitorar:", [
    "soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"
])
df, df_historico = carregar_tudo(liga_escolhida)

# 3. Painel Sugestivo
st.subheader("💡 Sugestões de Valor")
if not df.empty and 'valor_aposta' in df.columns:
    sugestoes = df[df['valor_aposta'] > 0.1].sort_values(by='valor_aposta', ascending=False)
    if not sugestoes.empty:
        for i, row in sugestoes.head(3).iterrows():
            col1, col2 = st.columns([4, 1])
            col1.info(f"Oportunidade: **{row['evento']}** | Casa: {row['time_casa']} | Odd: {row['odd_casa']} (Valor: +{row['valor_aposta']:.2f})")
            if col2.button(f"Aprovar #{i}"):
                supabase.table("apostas_simuladas").insert({"evento": str(row['evento']), "valor_apostado": 10.0, "odd": float(row['odd_casa']), "status": "pendente"}).execute()
                st.rerun()
    else:
        st.write("Nenhuma sugestão de valor alto agora.")
else:
    st.write("Dados de mercado em processamento...")

# 4. Tabela e Simulador (Mantidos)
st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.error("Erro ao carregar dados da API ou do Banco.")

# ... (Simulador e Histórico permanecem iguais)
