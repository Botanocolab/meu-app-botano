import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração da conexão (Use as mesmas secrets que configuramos no GitHub)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("Botano+ nas bets")

# 1. Buscando dados da tabela CORRETA
response = supabase.table("apostas").select("*").execute()
df = pd.DataFrame(response.data)

# 2. Exibindo métricas rápidas
if not df.empty:
    st.metric("Total de Jogos Carregados", len(df))
    
    # 3. Exibindo a tabela formatada
    st.subheader("Jogos Disponíveis")
    # Selecionamos apenas as colunas que fazem sentido para o usuário
    st.dataframe(df[['evento', 'time_casa', 'odd_casa', 'created_at']])
else:
    st.warning("Nenhum dado encontrado na tabela 'apostas'.")

# Botão para atualizar (forçar nova busca)
if st.button('Atualizar Dados'):
    st.rerun()
