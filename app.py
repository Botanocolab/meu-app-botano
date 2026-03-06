import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração da página
st.set_page_config(page_title="Botano+ Pro", page_icon="📈", layout="wide")

# Conexão (Chaves configuradas no Streamlit Cloud Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("⚽ Botano+ : Dashboard Profissional")

# --- Métricas no Topo (Estatísticas Rápidas) ---
col_m1, col_m2, col_m3 = st.columns(3)
# Simulação de contagem (você pode substituir pelo count real do banco se quiser)
col_m1.metric("Oportunidades", "72") 
col_m2.metric("Apostas Fake", "1")
col_m3.metric("Win Rate", "0%")

# Abas do Painel
tab1, tab2 = st.tabs(["📊 Oportunidades de Valor", "🎯 Área de Simulação"])

with tab1:
    margem_minima = st.sidebar.slider("Filtrar por Margem (%)", 0.0, 20.0, 2.0)
    st.info("💡 Dica: Quanto maior a margem, maior a probabilidade de valor no longo prazo.")
    
    # Aqui o seu carregamento de dados original
    try:
        response = supabase.table("apostas").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("Erro ao carregar dados.")

with tab2:
    st.subheader("🎯 Registrar Nova Entrada")
    with st.form("aposta_fake"):
        ev = st.text_input("Evento (ex: Time A vs Time B)")
        val = st.number_input("Valor da Aposta (R$)", min_value=1.0)
        submit = st.form_submit_button("Confirmar Aposta")
        
        if submit:
            supabase.table("carteira_simulada").insert({"evento": ev, "valor_investido": val, "status": "pendente"}).execute()
            st.success("Aposta registrada! Confira no histórico abaixo.")

    # Histórico de Simulações
    st.write("### Histórico de Simulações")
    hist = supabase.table("carteira_simulada").select("*").execute()
    df_hist = pd.DataFrame(hist.data)
    st.dataframe(df_hist, use_container_width=True)

    # --- Nova seção de Performance ---
    st.write("### 📈 Resumo da Performance")
    if not df_hist.empty:
        # Lógica para calcular performance
        finalizadas = df_hist[df_hist['status'].isin(['Green', 'Red'])]
        if not finalizadas.empty:
            st.bar_chart(finalizadas.groupby('status')['valor_investido'].sum())
        else:
            st.info("Nenhuma aposta finalizada ainda. Assim que você marcar um resultado, o gráfico aparecerá aqui!")
