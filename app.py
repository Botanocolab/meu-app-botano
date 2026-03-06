import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Robô de Apostas", layout="wide")

# CSS para o visual 'Bet' (Dark e profissional)
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #ffffff; }
    .metric-card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    .stDataFrame { border: 1px solid #333; border-radius: 5px; }
    h1, h2 { color: #ff5e00; }
    </style>
""", unsafe_allow_html=True)

# URL e Chave
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

supabase = create_client(url, key)

st.title("🎯 DASHBOARD DE PERFORMANCE")

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

        # Layout de Cards (Estilo Bet)
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Estimado", f"R$ {df['lucro_simulado'].sum():.2f}")
        c2.metric("Total Investido", f"R$ {df['valor_investido'].sum():.2f}")
        c3.metric("Apostas Ativas", len(df[df['status'] == 'pendente']))

        st.markdown("---")
        st.subheader("📋 Histórico de Apostas")
        
        # Exibição limpa
        st.dataframe(
            df[['evento', 'valor_investido', 'status', 'lucro_simulado']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado.")

except Exception as e:
    st.error(f"Erro: {e}")
