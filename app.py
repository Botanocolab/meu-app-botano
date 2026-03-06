import streamlit as st
import pandas as pd
from supabase import create_client

# Conexão com Supabase
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# Função para carregar dados
@st.cache_data(ttl=60)
def carregar_dados():
    response = supabase.table("apostas").select("*").execute()
    return pd.DataFrame(response.data)

# Carrega o DataFrame
df = carregar_dados()

if not df.empty:
    st.metric("Total de Jogos", len(df))
    
    # Validação: Garante que só tentamos exibir o que realmente existe no DataFrame
    colunas_desejadas = ['evento', 'time_casa', 'odd_casa', 'created_at']
    # Filtra apenas colunas que existem no df para evitar erros
    df_exibir = df[[c for c in colunas_desejadas if c in df.columns]]
    
    # Formatação condicional (usando .map que é a sintaxe correta atual)
    def destacar_odds(val):
        try:
            return 'background-color: #d4edda' if float(val) >= 2.00 else ''
        except:
            return ''

    # Aplica o estilo se a coluna 'odd_casa' existir
    if 'odd_casa' in df_exibir.columns:
        tabela_estilizada = df_exibir.style.map(destacar_odds, subset=['odd_casa'])
        st.dataframe(tabela_estilizada, use_container_width=True)
    else:
        st.dataframe(df_exibir, use_container_width=True)
else:
    st.warning("A tabela 'apostas' está vazia ou inacessível no momento.")

if st.button('Recarregar Dados'):
    st.cache_data.clear()
    st.rerun()
