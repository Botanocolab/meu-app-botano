import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações de layout Betano-like
st.set_page_config(page_title="Robô de Apostas", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; color: white; }
    h1 { color: #f9a825; text-align: center; }
    .stMetric { background-color: #333; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# URL e Chave (Cole sua chave aqui)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

supabase = create_client(url, key)

st.title("🎯 ROBÔ DE APOSTAS PRO")

try:
    # Busca dados
    response = supabase.table("carteira_simulada").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # LÓGICA DA SIMULAÇÃO
        def calcular_lucro(row):
            status = str(row.get('status', '')).lower().strip() # Usando a coluna 'status' que apareceu no seu print
            valor = float(row.get('valor_investido', 0))
            
            if status == 'green':
                return valor * 0.9  # Ajuste conforme sua ODD
            elif status == 'red':
                return -valor
            return 0.0

        # Cria a coluna de simulação
        df['lucro_simulado'] = df.apply(calcular_lucro, axis=1)
        
        # Métricas no topo
        total_acumulado = df['lucro_simulado'].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Saldo da Simulação (R$)", f"R$ {total_acumulado:.2f}")
        col2.metric("Total Apostado", f"R$ {df['valor_investido'].sum():.2f}")
        col3.metric("Apostas Finalizadas", len(df[df['status'] != 'pendente']))

        st.subheader("📝 Histórico e Simulação")
        
        # Exibe a tabela com a coluna de lucro
        st.dataframe(df[['evento', 'valor_investido', 'status', 'lucro_simulado']], 
                     use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado no banco.")

except Exception as e:
    st.error(f"Erro ao conectar: {e}")
