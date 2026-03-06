import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações do Supabase
url = "https://yovylzbqqulaiqfvugdg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" 

# Conexão
supabase = create_client(url, key)

st.title("📊 Painel de Performance - Robô de Apostas")

# Busca dados do Supabase
try:
    response = supabase.table("carteira_simulada").select("*").execute()
    data = response.data
    
    if data:
        df = pd.DataFrame(data)
        
        # 1. Função de Cálculo
        def calcular_resultado(row):
            # Normaliza o texto para evitar erros
            status = str(row.get('resultado', '')).lower().strip()
            try:
                valor = float(row.get('valor_investido', 0))
            except:
                valor = 0.0
            
            if status == 'green':
                return valor * 0.9
            elif status == 'red':
                return -valor
            else:
                return 0.0

        # 2. Criação da coluna
        df['lucro_simulado'] = df.apply(calcular_resultado, axis=1)
        
        # 3. Saldo Acumulado
        total_acumulado = df['lucro_simulado'].sum()
        st.metric("Saldo da Simulação (R$)", f"{total_acumulado:.2f}")
        
        # 4. Exibição da tabela garantindo a exibição da coluna
        st.subheader("Histórico de Apostas e Simulação")
        
        # Seleção explicita de colunas para forçar a visualização
        colunas_exibir = ['evento', 'valor_investido', 'resultado', 'lucro_simulado']
        
        # Verifica se as colunas existem antes de exibir
        cols_disponiveis = [c for c in colunas_exibir if c in df.columns]
        st.dataframe(df[cols_disponiveis], use_container_width=True)
        
    else:
        st.warning("A tabela está vazia no Supabase.")

except Exception as e:
    st.error(f"Erro na conexão: {e}")
