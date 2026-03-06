import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração da conexão
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Botano+ nas bets", layout="wide")
st.title("📊 Botano+ nas bets")

# Função para buscar dados
@st.cache_data(ttl=600) # Atualiza o cache a cada 10 minutos
def carregar_dados():
    response = supabase.table("apostas").select("*").execute()
    return pd.DataFrame(response.data)

# Função de estilo para destacar odds
def destacar_odds(val):
    try:
        # Destaca em verde se a odd for maior ou igual a 2.00
        color = 'background-color: #d4edda' if float(val) >= 2.00 else ''
        return color
    except:
        return ''

# Carregamento e exibição
df = carregar_dados()

if not df.empty:
    st.metric("Total de Jogos Carregados", len(df))
    
    # Prepara a tabela com estilo
    st.subheader("Jogos Disponíveis")
    
    # Aplicando a formatação condicional apenas na coluna 'odd_casa'
    tabela_estilizada = df[['evento', 'time_casa', 'odd_casa', 'created_at']].style.applymap(
        destacar_odds, subset=['odd_casa']
    )
    
    st.dataframe(tabela_estilizada, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado na tabela 'apostas'.")

# Botão para atualizar dados manualmente
if st.button('Atualizar Dados'):
    st.rerun()
