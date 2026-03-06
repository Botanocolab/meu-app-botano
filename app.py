import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Configuração
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# 2. Carregar Dados de Jogos
@st.cache_data(ttl=60)
def carregar_jogos():
    response = supabase.table("apostas").select("*").execute()
    return pd.DataFrame(response.data)

# 3. Carregar Histórico de Simulações
@st.cache_data(ttl=60)
def carregar_historico():
    response = supabase.table("apostas_simuladas").select("*").execute()
    return pd.DataFrame(response.data)

df = carregar_jogos()
df_historico = carregar_historico()

# Exibir Tabela de Jogos
if not df.empty:
    st.subheader("Jogos Disponíveis")
    def destacar_odds(val):
        try:
            return 'background-color: #d4edda' if float(val) >= 2.00 else ''
        except:
            return ''
    tabela_estilizada = df[['evento', 'time_casa', 'odd_casa', 'created_at']].style.map(
        destacar_odds, subset=['odd_casa']
    )
    st.dataframe(tabela_estilizada, use_container_width=True)

# 4. Formulário de Simulação
st.divider()
st.subheader("🎯 Simulador de Apostas")
with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique() if not df.empty else ["Nenhum jogo"])
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    btn_enviar = st.form_submit_button("Simular Aposta")
    if btn_enviar:
        supabase.table("apostas_simuladas").insert({
            "evento": str(evento_escolhido), "valor_apostado": float(valor), "odd": float(odd), "status": "pendente"
        }).execute()
        st.success("Simulação registrada!")
        st.rerun()

# 5. Exibir Histórico de Simulações
st.divider()
st.subheader("📜 Histórico de Simulações")
if not df_historico.empty:
    # Mostra o histórico
    st.dataframe(df_historico, use_container_width=True)
else:
    st.info("Nenhuma aposta simulada ainda.")

if st.button('Recarregar Tudo'):
    st.cache_data.clear()
    st.rerun()
