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
@st.cache_data(ttl=60)
def carregar_tudo():
    jogos = supabase.table("apostas").select("*").execute()
    historico = supabase.table("apostas_simuladas").select("*").execute()
    return pd.DataFrame(jogos.data), pd.DataFrame(historico.data)

df, df_historico = carregar_tudo()

# 3. Tabela de Jogos
if not df.empty:
    st.subheader("Jogos Disponíveis")
    st.dataframe(df[['evento', 'time_casa', 'odd_casa', 'created_at']], use_container_width=True)

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

# 5. Histórico e Gráfico de Performance
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📜 Histórico de Simulações")
    if not df_historico.empty:
        st.dataframe(df_historico, use_container_width=True)

with col2:
    st.subheader("📈 Evolução do seu Lucro")
    if not df_historico.empty:
        # Filtra apenas as apostas finalizadas (ganhas ou perdidas)
        df_final = df_historico[df_historico['status'].isin(['ganha', 'perdida'])].copy()
        
        if not df_final.empty:
            # Cálculo: Se ganha, lucro é (odd*valor)-valor. Se perdida, perde o valor.
            df_final['lucro'] = df_final.apply(
                lambda x: (x['odd'] * x['valor_apostado']) - x['valor_apostado'] if x['status'] == 'ganha' else -x['valor_apostado'], 
                axis=1
            )
            df_final['acumulado'] = df_final['lucro'].cumsum()
            st.line_chart(df_final['acumulado'])
        else:
            st.info("Aguardando apostas finalizadas para gerar o gráfico.")

if st.button('Recarregar Tudo'):
    st.cache_data.clear()
    st.rerun()
