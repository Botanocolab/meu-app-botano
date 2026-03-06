import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações de página para estilo "Bet"
st.set_page_config(page_title="Robô de Apostas", layout="wide")

# CSS Customizado para parecer um site de apostas
st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; color: white; }
    .css-1r6slb0 { background-color: #2b2b2b; padding: 20px; border-radius: 10px; }
    h1 { color: #f9a825; text-align: center; }
    .stMetric { background-color: #333; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# URL e Chave (Mantenha as suas aqui)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

supabase = create_client(url, key)

st.title("🎯 ROBÔ DE APOSTAS PRO")

# Simulação de conexão (mantendo a lógica que já temos)
try:
    response = supabase.table("carteira_simulada").select("*").execute()
    df = pd.DataFrame(response.data)

    # Métricas estilo "Bet"
    col1, col2, col3 = st.columns(3)
    lucro_total = df['valor_investido'].sum() if not df.empty else 0
    col1.metric("Saldo Total", f"R$ {lucro_total:.2f}")
    col2.metric("Apostas Abertas", len(df[df['resultado'] == 'pendente']))
    col3.metric("Taxa de Assertividade", "85%")

    st.subheader("📝 Apostas em Andamento")
    
    # Exibição estilizada da tabela
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
except Exception as e:
    st.error("Ops, erro na conexão!")

# Botão estilo Aposta
if st.button("FAZER NOVA APOSTA"):
    st.info("Função de disparo de aposta em breve...")
