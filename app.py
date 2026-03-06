import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações - Mantenha sem a barra no final
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

# Conexão
supabase = create_client(url, key)

st.title("📊 Painel de Performance - Robô de Apostas")

# Busca dados do Supabase
try:
    response = supabase.table("carteira_simulada").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Exibir colunas para você conferir se tudo está certo
        st.write("Colunas detectadas:", df.columns.tolist())

        # Cálculo do Saldo baseado nas colunas reais: 'valor_investido' e 'resultado'
        # Assumindo que 'resultado' contém 'Green' ou outro status
        def calcular_lucro(row):
            if row.get('resultado') == 'Green':
                # Aqui você pode ajustar o cálculo conforme sua regra de ganho
                return float(row.get('valor_investido', 0)) * 0.9 
            elif row.get('resultado') == 'Red':
                return -float(row.get('valor_investido', 0))
            return 0

        df['lucro'] = df.apply(calcular_lucro, axis=1)
        
        # Exibe métrica
        st.metric("Saldo Acumulado (R$)", f"{df['lucro'].sum():.2f}")
        
        # Exibe tabela
        st.subheader("Histórico de Apostas")
        st.dataframe(df)
    else:
        st.warning("A tabela está vazia no momento.")

except Exception as e:
    st.error(f"Erro ao conectar ou ler dados: {e}")
