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
def carregar_dados():
    response = supabase.table("apostas").select("*").execute()
    return pd.DataFrame(response.data)

df = carregar_dados()

# 3. Exibir Tabela
if not df.empty:
    st.metric("Total de Jogos", len(df))
    
    def destacar_odds(val):
        try:
            return 'background-color: #d4edda' if float(val) >= 2.00 else ''
        except:
            return ''

    tabela_estilizada = df[['evento', 'time_casa', 'odd_casa', 'created_at']].style.map(
        destacar_odds, subset=['odd_casa']
    )
    st.dataframe(tabela_estilizada, use_container_width=True)
else:
    st.warning("Tabela 'apostas' vazia.")

# 4. Formulário de Simulação (O que você pediu)
st.divider()
st.subheader("🎯 Simulador de Apostas")

with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique() if not df.empty else ["Nenhum jogo"])
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    
    btn_enviar = st.form_submit_button("Simular Aposta")

    if btn_enviar:
        dados_simulacao = {
            "evento": str(evento_escolhido),
            "valor_apostado": float(valor),
            "odd": float(odd),
            "status": "pendente"
        }
        try:
            supabase.table("apostas_simuladas").insert(dados_simulacao).execute()
            st.success(f"Simulação registrada: {evento_escolhido} (Odd {odd})")
        except Exception as e:
            st.error(f"Erro ao salvar simulação: {e}")

if st.button('Recarregar Dados'):
    st.cache_data.clear()
    st.rerun()
