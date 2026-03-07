# ==========================================
# BLOCO 1: CONFIGURAÇÕES, UI/CSS E CONEXÕES
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import requests
from supabase import create_client, Client
import plotly.graph_objects as go
from datetime import datetime

# Configuração da Página - Define o título e o ícone na aba do navegador
st.set_page_config(
    page_title="Botano+ Smart Betting V5.2",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (CORREÇÃO DE CONTRASTE DA SIDEBAR) ---
# Aqui resolvemos o problema das letras "sumindo" na barra lateral
st.markdown("""
<style>
    /* Fundo Principal Dark Mode */
    .stApp { background-color: #0f0f0f; color: #ffffff; }
    
    /* SIDEBAR - Ajuste de visibilidade total */
    [data-testid="stSidebar"] {
        background-color: #161616 !important;
        border-right: 1px solid #2d2d2d;
    }
    
    /* Força os textos (Labels, Sliders, Parágrafos) a ficarem BRANCOS */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stSlider p,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Estilização dos Sliders de Filtro */
    .stSlider [data-baseweb="slider"] { margin-bottom: 25px; }

    /* Cards de Métricas (Banca, ROI, Win Rate) */
    .metric-card {
        background: #1e1e1e;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #ff5a2a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Banner Principal do Engine */
    .main-banner {
        background: linear-gradient(90deg, #2d1610 0%, #1a1a1a 100%);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #ff5a2a;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CONEXÃO E SEGURANÇA ---
def get_api_keys():
    """Busca as chaves de API nos Secrets do Streamlit"""
    try:
        # Tenta ler as chaves configuradas no Streamlit Cloud ou arquivo secrets.toml
        return {
            "ODDS_API": st.secrets["THE_ODDS_API_KEY"],
            "SUPABASE_URL": st.secrets["SUPABASE_URL"],
            "SUPABASE_KEY": st.secrets["SUPABASE_KEY"]
        }
    except Exception:
        # Se não encontrar, retorna None para exibirmos um aviso na interface depois
        return None

def get_supabase_client() -> Client:
    """Inicializa a conexão com o banco de dados Supabase"""
    keys = get_api_keys()
    if keys:
        try:
            return create_client(keys["SUPABASE_URL"], keys["SUPABASE_KEY"])
        except:
            return None
    return None

# Inicialização da Banca no Estado da Sessão
if 'banca_inicial' not in st.session_state:
    st.session_state.banca_inicial = 1500.00

# Placeholder para indicar que o Bloco 1 foi carregado com sucesso
st.sidebar.success("✅ Estrutura e Interface Carregadas")

# ==========================================
# FIM DO BLOCO 1
# ==========================================

