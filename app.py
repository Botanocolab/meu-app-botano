import streamlit as st
from supabase import create_client

# Configuração da página para ficar com visual profissional
st.set_page_config(page_title="Botano+", page_icon="⚽")

st.title("⚽ Botano+ : Painel de Valor")

# Puxando as credenciais dos Secrets que você configurou
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]

# Conexão
supabase = create_client(url, key)

# Botão para atualizar dados manualmente
if st.button('Atualizar Dados'):
    st.rerun()

# Busca os dados da tabela 'apostas'
# Certifique-se de que o nome da tabela no Supabase é exatamente 'apostas'
try:
    response = supabase.table("apostas").select("*").execute()
    dados = response.data
    
    if dados:
        st.write(f"Encontrei {len(dados)} oportunidades:")
        st.dataframe(dados) # Exibe em formato de tabela interativa
    else:
        st.warning("Tabela encontrada, mas está vazia. Rode seu script no Colab!")
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
