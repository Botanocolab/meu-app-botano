import streamlit as st
import pandas as pd

# Configuração Básica
st.set_page_config(page_title="Botano+ Engine", layout="wide")

# CSS Limpo
st.markdown("""
<style>
    .stApp { background-color: #0f0f0f; color: white; }
    .botano-card { background: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #ff5a2a; }
</style>
""", unsafe_allow_html=True)

# Título
st.title("⚡ BOTANO+ Engine")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Oportunidades")
    st.markdown('<div class="botano-card">Mirassol x Santos | Odd 2.05 | EV +6.6%</div>', unsafe_allow_html=True)

with col2:
    st.subheader("🎯 Simulador")
    st.number_input("Valor (R$):", value=10.0)
    st.button("Registrar Aposta")
