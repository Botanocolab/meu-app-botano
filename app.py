import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Botano+", page_icon="⚽")
st.title("⚽ Botano+ : Painel de Valor")

# Conexão
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Sidebar para filtro
margem_minima = st.sidebar.slider("Filtrar por Margem Mínima (%)", 0.0, 20.0, 2.0)

if st.button('Atualizar Dados'):
    st.rerun()

try:
    response = supabase.table("apostas").select("*").execute()
    dados = response.data
    
    if dados:
        df = pd.DataFrame(dados)
        colunas = ['evento', 'time_casa', 'odd_casa', 'odd_empate', 'odd_fora', 'margem']
        
        # Ordenação e Filtro
        df_final = df[colunas].sort_values(by='margem', ascending=False)
        df_final = df_final[df_final['margem'] >= margem_minima]
        
        st.write(f"### Oportunidades encontradas: {len(df_final)}")
        st.dataframe(df_final, use_container_width=True)
    else:
        st.warning("Tabela vazia. Rode o script no Colab!")
except Exception as e:
    st.error(f"Erro: {e}")
