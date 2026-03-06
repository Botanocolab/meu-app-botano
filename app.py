import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração simples
st.set_page_config(page_title="Botano+ nas bets", layout="wide")

# URL e Chave (Mantenha as suas aqui)
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

supabase = create_client(url, key)

st.title("Botano+ nas bets")

try:
    # Busca os dados
    response = supabase.table("carteira_simulada").select("*").execute()
    data = response.data
    
    if data:
        df = pd.DataFrame(data)
        
        # Lógica de cálculo
        def calcular_lucro(row):
            status = str(row.get('status', '')).lower().strip()
            valor = float(row.get('valor_investido', 0))
            if status == 'green': return valor * 0.9
            if status == 'red': return -valor
            return 0.0

        # Cria a coluna de simulação
        df['lucro_simulado'] = df.apply(calcular_lucro, axis=1)

        # Métricas (Layout padrão do Streamlit)
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Estimado", f"R$ {df['lucro_simulado'].sum():.2f}")
        c2.metric("Total Investido", f"R$ {df['valor_investido'].sum():.2f}")
        c3.metric("Apostas Ativas", len(df[df['status'] == 'pendente']))

        st.subheader("Histórico de Apostas")
        
        # Exibição da tabela
        st.dataframe(df[['evento', 'valor_investido', 'status', 'lucro_simulado']], 
                     use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado.")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
