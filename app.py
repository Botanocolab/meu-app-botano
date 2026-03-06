import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração da conexão
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE"
supabase = create_client(url, key)

st.title("📊 Painel de Performance - Robô de Apostas")

# Busca dados do Supabase
response = supabase.table("carteira_simulada").select("*").execute()
df = pd.DataFrame(response.data)

if not df.empty:
    # Lógica de cálculo do lucro/prejuízo
    # Se Green: (Valor * Odd) - Valor
    # Se Red: -Valor
    def calcular_lucro(row):
        if row['status'] == 'Green':
            return (row['valor_aposta'] * row['odd']) - row['valor_aposta']
        elif row['status'] == 'Red':
            return -row['valor_aposta']
        return 0

    df['lucro'] = df.apply(calcular_lucro, axis=1)
    
    # Exibir saldo acumulado no topo
    saldo_total = df['lucro'].sum()
    st.metric("Saldo Acumulado (R$)", f"{saldo_total:.2f}")

    # Exibir tabela de histórico
    st.subheader("Histórico de Apostas")
    st.dataframe(df[['evento', 'status', 'valor_aposta', 'odd', 'lucro']])
else:
    st.write("Nenhuma aposta encontrada no banco.")

