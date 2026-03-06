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

# 2. Carregar Dados com Integração API e Cálculo de Valor
def carregar_tudo(liga="soccer_brazil_serie_a"):
    api_key = st.secrets.get("ODDS_API_KEY")
    url_api = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=br&markets=h2h"
    
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
        else:
            df = pd.DataFrame(supabase.table("apostas").select("*").execute().data)
    except:
        df = pd.DataFrame(supabase.table("apostas").select("*").execute().data)

    historico = pd.DataFrame(supabase.table("apostas_simuladas").select("*").execute().data)
    return df, historico

# Seleção de Liga
liga_escolhida = st.selectbox("Escolha a Liga para monitorar:", [
    "soccer_brazil_serie_a", "soccer_uefa_champs_league", "soccer_epl"
])
df, df_historico = carregar_tudo(liga_escolhida)

# 3. Painel Sugestivo (O seu novo cérebro de decisões)
st.subheader("💡 Sugestões de Valor (Alta Confiança)")
if not df.empty and 'valor_aposta' in df.columns:
    sugestoes = df[df['valor_aposta'] > 0.2].sort_values(by='valor_aposta', ascending=False)
    if not sugestoes.empty:
        for i, row in sugestoes.head(3).iterrows():
            col_a, col_b = st.columns([3, 1])
            col_a.info(f"Oportunidade em **{row['evento']}** | Casa: {row['time_casa']} | Odd: {row['odd_casa']} (Valor: +{row['valor_aposta']:.2f})")
            if col_b.button(f"Aprovar Aposta #{i}"):
                supabase.table("apostas_simuladas").insert({
                    "evento": str(row['evento']),
                    "valor_apostado": 10.0,
                    "odd": float(row['odd_casa']),
                    "status": "pendente"
                }).execute()
                st.success("Aposta enviada!")
                st.rerun()
    else:
        st.info("Nenhuma oportunidade extrema encontrada no momento.")
else:
    st.info("Carregando dados...")

# 4. Tabela de Jogos
st.subheader("📜 Jogos Disponíveis")
if not df.empty:
    casas = ["Todas"] + sorted(df['time_casa'].dropna().unique().tolist())
    filtro_casa = st.selectbox("Filtrar por Casa de Aposta:", casas)
    df_exibir = df[df['time_casa'] == filtro_casa] if filtro_casa != "Todas" else df
    
    if 'valor_aposta' in df_exibir.columns:
        st.dataframe(df_exibir.style.background_gradient(subset=['valor_aposta'], cmap='RdYlGn'), use_container_width=True)
    else:
        st.dataframe(df_exibir, use_container_width=True)

# 5. Simulador
st.divider()
st.subheader("🎯 Simulador de Apostas")
with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique() if not df.empty else ["Nenhum jogo"])
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    resultado = st.selectbox("Resultado da Aposta:", ["pendente", "ganha", "perdida"])
    if st.form_submit_button("Registrar Aposta"):
        supabase.table("apostas_simuladas").insert({"evento": str(evento_escolhido), "valor_apostado": float(valor), "odd": float(odd), "status": resultado}).execute()
        st.rerun()

# 6. Histórico
st.divider()
st.subheader("📈 Evolução do seu Lucro")
if not df_historico.empty and 'status' in df_historico.columns:
    df_final = df_historico[df_historico['status'].isin(['ganha', 'perdida'])].copy()
    if not df_final.empty:
        df_final['lucro'] = df_final.apply(lambda x: (x['odd'] * x['valor_apostado']) - x['valor_apostado'] if x['status'] == 'ganha' else -x['valor_apostado'], axis=1)
        df_final['acumulado'] = df_final['lucro'].cumsum()
        st.line_chart(df_final['acumulado'])
