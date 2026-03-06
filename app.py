import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Botano+ Pro", page_icon="📈", layout="wide")

# Estilo customizado (CSS injetado)
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚽ Botano+ : Dashboard Profissional")

# Conexão
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- Layout das Métricas ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Oportunidades", "72")
col_m2.metric("Apostas Fake", "1")
col_m3.metric("Win Rate", "0%")

tab1, tab2 = st.tabs(["📊 Oportunidades de Valor", "🎯 Área de Simulação"])

with tab1:
    margem_minima = st.slider("Filtrar por Margem (%)", 0.0, 20.0, 2.0)
    # Aqui vai o seu dataframe de oportunidades
    st.info("💡 Dica: Quanto maior a margem, maior a probabilidade de valor no longo prazo.")

with tab2:
    st.subheader("Registrar Entrada")
    with st.form("aposta_fake"):
        ev = st.text_input("Evento")
        val = st.number_input("Valor (R$)", min_value=1.0)
        submit = st.form_submit_button("Confirmar Aposta")
        if submit:
            supabase.table("carteira_simulada").insert({"evento": ev, "valor_investido": val}).execute()
            st.success("Entrada registrada no diário!")
    
    # Histórico com visual melhorado
    hist = supabase.table("carteira_simulada").select("*").execute()
    st.dataframe(pd.DataFrame(hist.data), use_container_width=True)
