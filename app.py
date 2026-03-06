import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração de página
st.set_page_config(page_title="Botano+", layout="wide")

# CSS para o visual 'Bet' customizado
st.markdown("""
    <style>
    /* Fundo Laranja vibrante */
    .stApp { background-color: #ff5e00; color: #333; }
    
    /* Cards brancos */
    [data-testid="stMetricValue"] { color: #ff5e00; }
    div[data-testid="stMetric"] { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    
    /* Tabela e Texto */
    h1 { color: white; text-align: center; font-size: 60px !important; margin-bottom: 30px; }
    h2 { color: white; }
    .stDataFrame { background-color: white; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# URL e Chave
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

supabase = create_client(url, key)

st.title("Botano+ nas bets")

try:
    response = supabase.table("carteira_simulada").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Lógica de cálculo
        def calcular_lucro(row):
            status = str(row.get('status', '')).lower().strip()
            valor = float(row.get('valor_investido', 0))
            if status == 'green': return valor * 0.9
            if status == 'red': return -valor
            return 0.0

        df['lucro_simulado'] = df.apply(calcular_lucro, axis=1)

        # Layout de Cards Brancos
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Estimado", f"R$ {df['lucro_simulado'].sum():.2f}")
        c2.metric("Total Investido", f"R$ {df['valor_investido'].sum():.2f}")
        c3.metric("Apostas Ativas", len(df[df['status'] == 'pendente']))

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Histórico de Apostas")
        
        # Exibição
        st.dataframe(
            df[['evento', 'valor_investido', 'status', 'lucro_simulado']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado.")

except Exception as e:
    st.error(f"Erro: {e}")
