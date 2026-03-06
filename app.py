import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Configuração
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# 2. Carregar Dados
def carregar_tudo():
    # Buscamos a tabela de apostas e a de simuladas
    jogos = supabase.table("apostas").select("*").execute()
    historico = supabase.table("apostas_simuladas").select("*").execute()
    return pd.DataFrame(jogos.data), pd.DataFrame(historico.data)

df, df_historico = carregar_tudo()

# 3. Tabela de Jogos com Filtro Corrigido
st.subheader("Jogos Disponíveis")

if not df.empty:
    # AQUI ESTÁ A CORREÇÃO: Usando 'time_casa' que é onde os nomes das casas estão no seu banco
    casas_disponiveis = df['time_casa'].dropna().unique().tolist()
    casas = ["Todas"] + sorted([str(c) for c in casas_disponiveis])
    
    filtro_casa = st.selectbox("Filtrar por Casa de Aposta:", casas)
    
    if filtro_casa != "Todas":
        df_exibir = df[df['time_casa'] == filtro_casa]
    else:
        df_exibir = df
        
    # Exibe a tabela filtrada
    st.dataframe(df_exibir[['evento', 'time_casa', 'odd_casa', 'created_at']], use_container_width=True)
else:
    st.info("Nenhum jogo disponível.")

# 4. Simulador
st.divider()
st.subheader("🎯 Simulador de Apostas")
with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique() if not df.empty else ["Nenhum jogo"])
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    resultado = st.selectbox("Resultado da Aposta:", ["pendente", "ganha", "perdida"])
    
    btn_enviar = st.form_submit_button("Registrar Aposta")
    if btn_enviar:
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
            df_final['lucro'] = df_final.apply(
                lambda x: (x['odd'] * x['valor_apostado']) - x['valor_apostado'] if x['status'] == 'ganha' else -x['valor_apostado'], 
                axis=1
            )
            df_final['acumulado'] = df_final['lucro'].cumsum()
            st.line_chart(df_final['acumulado'])
        else:
            st.info("Aguardando apostas finalizadas.")

if st.button('Recarregar Tudo'):
    st.rerun()
