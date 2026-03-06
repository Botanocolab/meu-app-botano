import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. CONFIGURAÇÃO PREMIUM
st.set_page_config(page_title="Botano+ | Engine", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top left, #1a120f 0%, #0f0f0f 45%, #0b0b0b 100%); color: white; }
    h1 { font-weight: 900; letter-spacing: -1px; }
    .botano-card {
        background: #1e1e1e; border-radius: 18px; padding: 20px; 
        margin-bottom: 16px; border-left: 5px solid #ff5a2a;
        box-shadow: 0 8px 25px rgba(0,0,0,0.45);
    }
    .side-stat-card {
        background: #181818; border: 1px solid #2b2b2b; border-radius: 16px;
        padding: 16px; margin-top: 14px; box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    }
    .side-stat-label { color: #b8b8b8; font-size: 13px; margin-bottom: 6px; }
    .side-stat-value { color: #ffffff; font-size: 28px; font-weight: 800; line-height: 1; }
    .botano-strong { font-weight: 800; color: #ff5a2a; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# 2. HEADER
st.markdown("""
<h1 style='display:flex;align-items:center;gap:10px'>
⚡ <span style="color:#ff5a2a">BOTANO+</span>
<span style="font-size:18px;color:#c9c9c9;font-weight:400">Smart Betting Engine</span>
</h1>
""", unsafe_allow_html=True)

# 3. LÓGICA (MOCKUP PARA TESTE VISUAL)
ligas = {"Brasileirão Série A": "soccer_brazil_campeonato", "Premier League": "soccer_epl"}
liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))

# 4. INTERFACE V4
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Oportunidades com Valor")
    # Loop de cards (Dados simulados para garantir o render)
    for i in range(3):
        st.markdown(f"""
        <div class="botano-card">
            <div class="botano-strong">Time A x Time B</div>
            <div class="botano-metric">Seleção: Time A | Odd: 2.05 | EV: <span style="color:#ff5a2a">+6.6%</span> | Score: 65.9</div>
        </div>
        """, unsafe_allow_html=True)
        st.button(f"Apostar Agora #{i+1}", key=f"btn_{i}")

with col_right:
    st.subheader("🎯 Simulador & Gestão")
    with st.form("sim"):
        val = st.number_input("Valor (R$):", value=10.0)
        odd = st.number_input("Odd:", value=1.5)
        st.form_submit_button("Registrar Aposta")
        
    # Blocos de métricas profissionais
    st.markdown("""
    <div class="side-stat-card">
        <div class="side-stat-label">ROI Estimado</div>
        <div class="side-stat-value">+12.4%</div>
    </div>
    <div class="side-stat-card">
        <div class="side-stat-label">Win Rate</div>
        <div class="side-stat-value">58%</div>
    </div>
    """, unsafe_allow_html=True)
