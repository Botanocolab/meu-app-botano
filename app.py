import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração da página
st.set_page_config(page_title="Botano+", page_icon="⚽")
st.title("⚽ Botano+ : Painel de Valor")

# Conexão com Supabase
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Botão para atualizar
if st.button('Atualizar Dados'):
    st.rerun()

# Busca os dados
try:
    response = supabase.table("apostas").select("*").execute()
    dados = response.data
    
    if dados:
        # Transforma os dados em DataFrame para organizar melhor
        df = pd.DataFrame(dados)
        
        # Filtra apenas as colunas que você quer mostrar e na ordem que você quer
        # Nota: Ajustei para os nomes que criamos no banco
        colunas_exibicao = ['evento', 'time_casa', 'odd_casa', 'odd_empate', 'odd_fora', 'margem']
        
        # Exibe a tabela organizada
        st.write("### Oportunidades Encontradas")
        st.dataframe(df[colunas_exibicao], use_container_width=True)
    else:
        st.warning("Tabela encontrada, mas está vazia. Rode seu script no Colab!")

except Exception as e:
    st.error(f"Erro ao conectar: {e}")
