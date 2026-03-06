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
        # Lógica da simulação
        def calcular_resultado(row):
            status = str(row.get('resultado')).lower().strip()
            # Garante que o valor é numérico
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

        # Aplica o cálculo
        df['lucro_simulado'] = df.apply(calcular_resultado, axis=1)
        
        # Exibição do Saldo Acumulado
        total_acumulado = df['lucro_simulado'].sum()
        st.metric("Saldo da Simulação (R$)", f"{total_acumulado:.2f}")
        
        # Exibe a tabela forçando a inclusão de todas as colunas relevantes
        st.subheader("Histórico de Apostas e Simulação")
        
        # Usamos uma lista explícita para garantir a ordem e a exibição
        colunas_exibir = ['evento', 'valor_investido', 'resultado', 'lucro_simulado']
        st.dataframe(df[colunas_exibir], use_container_width=True)
        
    else:
        st.warning("A tabela está vazia. Adicione apostas no Supabase.")

except Exception as e:
    st.error(f"Erro ao conectar ou ler dados: {e}")
