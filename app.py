import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações do Supabase
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

# Criar a conexão
supabase = create_client(url, key)

st.title("📊 Painel de Performance - Robô de Apostas")

# Carregar dados da tabela
try:
    response = supabase.table("carteira_simulada").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Lógica da simulação: Cálculo de Lucro/Prejuízo
        def calcular_resultado(row):
            status = str(row.get('resultado')).lower()
            valor = float(row.get('valor_investido', 0))
            
            # Regra da simulação: 
            # Se Green, lucro de 90% (ajuste conforme sua estratégia)
            # Se Red, perda total do valor investido
            if status == 'green':
                return valor * 0.9
            elif status == 'red':
                return -valor
            else:
                return 0.0

        # Aplica a simulação em cada linha
        df['lucro_simulado'] = df.apply(calcular_resultado, axis=1)
        
        # Exibição do Saldo Acumulado (Simulação)
        total_acumulado = df['lucro_simulado'].sum()
        st.metric("Saldo da Simulação (R$)", f"{total_acumulado:.2f}")
        
        # Tabela completa com a simulação
        st.subheader("Histórico de Apostas e Simulação")
        st.dataframe(df[['evento', 'valor_investido', 'resultado', 'lucro_simulado']])
        
    else:
        st.warning("A tabela está vazia. Adicione apostas no Supabase para ver a simulação.")

except Exception as e:
    st.error(f"Erro ao conectar ou ler dados: {e}")
