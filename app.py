import streamlit as st
import pandas as pd
import requests
from supabase import create_client

# 1. Configuração da página (Deve ser o primeiro comando do Streamlit)
st.set_page_config(page_title="Botano+ nas bets", layout="wide")

# 2. CSS Customizado (Visual estilo Betano/Trading)
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    div[data-testid="stContainer"] {
        background-color: #2d2d2d;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #ff4b2b;
        margin-bottom: 10px;
    }
    div.stButton > button {
        background-color: #ff4b2b !important;
        color: white !important;
        border-radius: 20px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    h1, h2, h3 {
        color: #ff4b2b !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Título e Início do App
st.title("📊 Botano+ nas bets")

# Conexão Supabase
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
