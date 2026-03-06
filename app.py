import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. CONFIGURAÇÃO PREMIUM
st.set_page_config(page_title="Botano+ | Engine", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0f0f0f; color: white; }
    h1 { font-weight: 900; letter-spacing: -1px; }
    .botano-card {
        background: #1e1e1e; border-radius: 18px; padding: 20px; 
        margin-bottom: 16px; border-left: 5px solid #ff5a2a;
        box-shadow: 0 8px 25px rgba(0,0,0,0.45);
    }
    .botano-metric { font-size: 14px; color: #c9c9c9; }
    .botano-strong { font-weight: 800; color: #ff5a2a; font-size: 1.1em; }
    div.stButton > button { background: linear-gradient(135deg,#ff5a2a,#ff7a1a); 
    border-radius: 12px; border: none; color: white; font-weight: 700; width: 100%; }
</style>
""", unsafe_allow_html=True)

# 2. HEADER PROFISSIONAL
st.markdown("""
<h1 style='display:flex;align-items:center;gap:10px'>
⚡ <span style="color:#ff5a2a">BOTANO+</span>
<span style="font-size:18px;color:#c9c9c9;font-weight:400">Smart Betting Engine</span>
</h1>
""", unsafe_allow_html=True)

# 3. LÓGICA DE EV REAL (Cálculo via Fair Prob)
def calcular_ev(best_odd, fair_prob):
    return (fair_prob * best_odd) - 1

# ... [função buscar_odds mantida aqui] ...

# 4. INTERFACE V3
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Oportunidades com Valor")
    # Aqui entra o loop dos cards com o novo CSS "botano-card"
    # Adicionaremos o Score Botano: (EV % * 10) + (Odd * 2)

with col_right:
    st.subheader("🎯 Simulador & Gestão")
    # Aqui o formulário + métricas de ROI (puxadas do Supabase)
