import streamlit as st
import pandas as pd
from supabase import create_client

url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE"
supabase = create_client(url, key)

st.title("📊 Painel de Performance - Robô de Apostas")

response = supabase.table("carteira_simulada").select("*").execute()
df = pd.DataFrame(response.data)

if not df.empty:
    # Função ajustada para as novas colunas
    def calcular_lucro(row):
        # Ajuste aqui o multiplicador da sua ODD se precisar
        if row.get('resultado') == 'Green':
            return float(row.get('valor_investido', 0)) * 0.9 
        elif row.get('resultado') == 'Red':
            return -float(row.get('valor_investido', 0))
        return 0

    df['lucro'] = df.apply(calcular_lucro, axis=1)
    
    st.metric("Saldo Acumulado (R$)", f"{df['lucro'].sum():.2f}")
    
    st.subheader("Histórico de Apostas")
    st.dataframe(df[['evento', 'valor_investido', 'resultado', 'lucro']])
else:
    st.write("Nenhuma aposta encontrada no banco.")
