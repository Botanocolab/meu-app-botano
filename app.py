import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Botano+", page_icon="⚽")
st.title("⚽ Botano+ : Painel de Valor")

# Conexão (Chaves configuradas no Streamlit Cloud Secrets)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Criando abas para separar o Painel Real do Simulador
tab1, tab2 = st.tabs(["📊 Painel de Valor", "🎯 Modo Simulação"])

with tab1:
    margem_minima = st.sidebar.slider("Filtrar por Margem Mínima (%)", 0.0, 20.0, 2.0)
    
    if st.button('Atualizar Dados'):
        st.rerun()

    try:
        response = supabase.table("apostas").select("*").execute()
        dados = response.data
        
        if dados:
            df = pd.DataFrame(dados)
            colunas = ['evento', 'time_casa', 'odd_casa', 'odd_empate', 'odd_fora', 'margem']
            
            df_final = df[colunas].sort_values(by='margem', ascending=False)
            df_final = df_final[df_final['margem'] >= margem_minima]
            
            st.write(f"### Oportunidades encontradas: {len(df_final)}")
            st.dataframe(df_final, use_container_width=True)
        else:
            st.warning("Tabela vazia. Rode o script no Colab!")
    except Exception as e:
        st.error(f"Erro: {e}")

with tab2:
    st.subheader("🎯 Registrar Aposta Fake")
    col1, col2 = st.columns(2)
    with col1:
        evento_sim = st.text_input("Nome do Evento (ex: Botafogo vs Flamengo)")
    with col2:
        valor_sim = st.number_input("Valor da Aposta (R$)", min_value=1.0)
    
    if st.button("Registrar Aposta Fake"):
        novo_registro = {"evento": evento_sim, "margem": 0.0, "valor_investido": valor_sim}
        supabase.table("carteira_simulada").insert(novo_registro).execute()
        st.success("Aposta registrada na carteira simulada!")

    st.write("### Histórico de Simulações")
    hist = supabase.table("carteira_simulada").select("*").execute()
    if hist.data:
        st.table(pd.DataFrame(hist.data))
    else:
        st.write("Nenhuma aposta registrada ainda.")
