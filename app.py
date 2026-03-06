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

# 1. Carregamento dos Dados
def carregar_dados(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jogos_list = []
            for jogo in data:
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
        pass
    
    # Fallback: Se API falhar ou der erro, busca Supabase
    return pd.DataFrame(supabase.table("apostas").select("*").execute().data)

# Interface
liga_escolhida = st.selectbox("Escolha a Liga:", ["soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"])
df = carregar_dados(liga_escolhida)
df_historico = pd.DataFrame(supabase.table("apostas_simuladas").select("*").execute().data)

# 2. Painel Sugestivo (Só aparece se houver dados de valor)
if 'valor_aposta' in df.columns:
    st.subheader("💡 Sugestões de Valor")
    sugestoes = df[df['valor_aposta'] > 0.1].sort_values(by='valor_aposta', ascending=False).head(3)
    if not sugestoes.empty:
        for i, row in sugestoes.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.info(f"Oportunidade: {row['evento']} | Casa: {row['time_casa']} | Odd: {row['odd_casa']} (Valor: +{row['valor_aposta']:.2f})")
            if col2.button(f"Aprovar #{i}", key=f"btn_{i}"):
                supabase.table("apostas_simuladas").insert({"evento": row['evento'], "valor_apostado": 10.0, "odd": float(row['odd_casa']), "status": "pendente"}).execute()
                st.rerun()

# 3. Tabela Principal
st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Nenhum dado disponível no momento.")

# 4. Simulador
st.divider()
st.subheader("🎯 Simulador")
with st.form("sim_form"):
    evento = st.selectbox("Jogo:", df['evento'].unique() if not df.empty else ["N/A"])
    valor = st.number_input("Valor (R$):", value=10.0)
    odd = st.number_input("Odd:", value=1.5)
    if st.form_submit_button("Registrar"):
        supabase.table("apostas_simuladas").insert({"evento": evento, "valor_apostado": float(valor), "odd": float(odd), "status": "pendente"}).execute()
        st.rerun()

# 5. Histórico e Gráfico
st.subheader("📈 Histórico")
if not df_historico.empty:
    st.dataframe(df_historico, use_container_width=True)
    if 'status' in df_historico.columns:
        df_historico['lucro'] = df_historico.apply(lambda x: (x['odd'] * x['valor_apostado']) - x['valor_apostado'] if x['status'] == 'ganha' else -x['valor_apostado'], axis=1)
        st.line_chart(df_historico['lucro'].cumsum())
