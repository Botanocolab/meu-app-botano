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
def carregar_tudo():
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_serie_a/odds/?apiKey={api_key}&regions=br&markets=h2h"
    
    try:
        response = requests.get(url_api, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jogos_list = []
            for jogo in data:
                if 'bookmakers' in jogo and len(jogo['bookmakers']) > 0:
                    bookmaker = jogo['bookmakers'][0]['title']
                    price = jogo['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                    jogos_list.append({
                        'evento': f"{jogo['home_team']} vs {jogo['away_team']}",
                        'time_casa': bookmaker,
                        'odd_casa': price
                    })
            df = pd.DataFrame(jogos_list)
        else:
            jogos = supabase.table("apostas").select("*").execute()
            df = pd.DataFrame(jogos.data)
    except:
        jogos = supabase.table("apostas").select("*").execute()
        df = pd.DataFrame(jogos.data)

    historico = supabase.table("apostas_simuladas").select("*").execute()
    return df, pd.DataFrame(historico.data)

df, df_historico = carregar_tudo()

# 3. Tabela de Jogos com Filtro
st.subheader("Jogos Disponíveis")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro_casa = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro_casa] if filtro_casa != "Todas" else df
    st.dataframe(df_exibir, use_container_width=True)
else:
    st.info("Nenhum jogo disponível no momento.")

# 4. Simulador
st.divider()
st.subheader("🎯 Simulador de Apostas")
with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique() if not df.empty else ["Nenhum jogo"])
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    resultado = st.selectbox("Resultado da Aposta:", ["pendente", "ganha", "perdida"])
    
    if st.form_submit_button("Registrar Aposta"):
        supabase.table("apostas_simuladas").insert({
            "evento": str(evento_escolhido), 
            "valor_apostado": float(valor), 
            "odd": float(odd), 
            "status": resultado
        }).execute()
        st.success("Aposta registrada com sucesso!")
        st.rerun()

# 5. Histórico e Gráfico
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("📜 Histórico de Simulações")
    if not df_historico.empty:
        st.dataframe(df_historico, use_container_width=True)
with col2:
    st.subheader("📈 Evolução do seu Lucro")
    if not df_historico.empty and 'status' in df_historico.columns:
        df_final = df_historico[df_historico['status'].isin(['ganha', 'perdida'])].copy()
        if not df_final.empty:
            df_final['lucro'] = df_final.apply(lambda x: (x['odd'] * x['valor_apostado']) - x['valor_apostado'] if x['status'] == 'ganha' else -x['valor_apostado'], axis=1)
            df_final['acumulado'] = df_final['lucro'].cumsum()
            st.line_chart(df_final['acumulado'])
        else:
            st.info("Aguardando apostas finalizadas para gerar o gráfico.")

if st.button('Recarregar Tudo'):
    st.rerun()
