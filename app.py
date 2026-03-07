import streamlit as st
import pandas as pd
import requests
from supabase import create_client
from datetime import datetime
import uuid

# --- CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(page_title="Botano+ V5 | Engine", layout="wide", initial_sidebar_state="collapsed")

# Inicialização do Supabase (Substitua pelas suas variáveis de ambiente)
URL = st.secrets.get("SUPABASE_URL", "")
KEY = st.secrets.get("SUPABASE_KEY", "")
API_KEY = st.secrets.get("ODDS_API_KEY", "")

try:
    supabase = create_client(URL, KEY)
except Exception:
    st.error("Erro na conexão com Supabase. Verifique as chaves nas configurações.")

# --- ESTILIZAÇÃO PREMIUM (BETANO DARK) ---
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top left, #1a120f 0%, #0f0f0f 45%, #0b0b0b 100%); color: white; }
    .botano-card {
        background: #1e1e1e; border-radius: 14px; padding: 20px; 
        margin-bottom: 15px; border-left: 5px solid #ff5a2a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .badge { padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; text-transform: uppercase; margin-right: 5px; }
    .badge-1x2 { background: #ff5a2a; color: white; }
    .badge-gols { background: #2a9d8f; color: white; }
    .badge-cantos { background: #e9c46a; color: black; }
    .side-stat-card {
        background: #181818; border: 1px solid #2b2b2b; border-radius: 12px;
        padding: 15px; margin-bottom: 10px;
    }
    .status-premium { color: #00ff88; font-weight: bold; }
    .status-agressiva { color: #ffcc00; font-weight: bold; }
    div.stButton > button {
        background: linear-gradient(135deg,#ff5a2a,#ff7a1a);
        border: none; color: white; font-weight: 700; border-radius: 8px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE MOTOR ---

def calcular_metrics(odd, prob_consenso):
    """Calcula EV, Score e Categoria de Risco."""
    ev = (prob_consenso * odd) - 1
    ev_pct = round(ev * 100, 2)
    score = round((ev_pct * 8) + (prob_consenso * 30) - (odd * 1.5), 1)
    
    if ev_pct > 10 and odd < 2.5: risco = "Premium"
    elif ev_pct > 5: risco = "Boa"
    elif odd > 3.5: risco = "Risco Elevado"
    else: risco = "Agressiva"
    
    return ev_pct, score, risco

def registrar_aposta(dados):
    """Persistência no Supabase."""
    try:
        dados['created_at'] = datetime.now().isoformat()
        supabase.table("apostas_simuladas").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Falha ao registrar: {e}")
        return False

def buscar_dados_api(sport="soccer_brazil_campeonato"):
    """Coleta multimercados (placeholder para estrutura real)."""
    # Em produção, iterar pelos mercados: h2h, totals, btts, corners
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h,totals", "oddsFormat": "decimal"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

# --- INTERFACE PRINCIPAL ---

st.markdown("""<h1 style='display:flex;align-items:center;gap:10px'>⚡ <span style="color:#ff5a2a">BOTANO+</span> <span style="font-size:18px;color:#c9c9c9;font-weight:400">V5 Smart Engine</span></h1>""", unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

# Simulando processamento de dados para a V5
data_raw = buscar_dados_api()
oportunidades = []

# Mock de processamento para demonstração da estrutura (será substituído pelo loop real da API)
if not data_raw:
    # Dados mockados estruturados conforme visão do produto
    oportunidades = [
        {"id": "1", "evento": "Flamengo x Vasco", "mercado": "Gols", "linha": "Over 2.5", "odd": 1.95, "prob": 0.58, "badge": "badge-gols"},
        {"id": "2", "evento": "Palmeiras x Santos", "mercado": "1x2", "linha": "Vitória Palmeiras", "odd": 1.75, "prob": 0.65, "badge": "badge-1x2"},
        {"id": "3", "evento": "Corinthians x SPFC", "mercado": "Cantos", "linha": "Over 9.5", "odd": 2.10, "prob": 0.55, "badge": "badge-cantos"}
    ]

with col_left:
    st.subheader("🚀 Oportunidades Identificadas")
    for op in oportunidades:
        ev, score, risco = calcular_metrics(op['odd'], op['prob'])
        
        with st.container():
            st.markdown(f"""
            <div class="botano-card">
                <span class="badge {op['badge']}">{op['mercado']}</span>
                <span class="status-{risco.lower()}">{risco}</span>
                <h3 style="margin:10px 0;">{op['evento']}</h3>
                <p style="font-size:14px; color:#c9c9c9;">
                    Seleção: <b>{op['linha']}</b> | Odd: <b>{op['odd']}</b> | EV: <span style="color:#ff5a2a">{ev}%</span> | Score: {score}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Apostar no simulador: {op['linha']} em {op['evento']}", key=op['id']):
                sucesso = registrar_aposta({
                    "evento": op['evento'], "mercado": op['mercado'], "linha": op['linha'],
                    "odd": op['odd'], "ev_percent": ev, "score_botano": score, "status": "pendente"
                })
                if sucesso: st.success("Registrado com sucesso!")

with col_right:
    st.subheader("🎯 Gestão & Múltiplas")
    
    # Bloco Tripla do Dia
    st.markdown('<div class="side-stat-card">', unsafe_allow_html=True)
    st.markdown("<b style='color:#ff5a2a;'>🔥 Sugestão de Tripla do Dia</b>", unsafe_allow_html=True)
    if len(oportunidades) >= 3:
        odd_comb = round(oportunidades[0]['odd'] * oportunidades[1]['odd'] * oportunidades[2]['odd'], 2)
        st.write(f"1. {oportunidades[0]['evento']} ({oportunidades[0]['linha']})")
        st.write(f"2. {oportunidades[1]['evento']} ({oportunidades[1]['linha']})")
        st.write(f"3. {oportunidades[2]['evento']} ({oportunidades[2]['linha']})")
        st.markdown(f"<h2 style='text-align:center;'>Odd: {odd_comb}</h2>", unsafe_allow_html=True)
        if st.button("Registrar Tripla Completa"):
            st.info("Registrando grupo de apostas...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Métricas de Performance
    st.markdown("""
    <div class="side-stat-card"><div class="side-label">ROI Real</div><div class="side-value" style="color:#00ff88;">+14.2%</div></div>
    <div class="side-stat-card"><div class="side-label">Win Rate</div><div class="side-value">62%</div></div>
    <div class="side-stat-card"><div class="side-label">Banca Atual</div><div class="side-value">R$ 1.250,00</div></div>
    """, unsafe_allow_html=True)

# Footer de Logs
st.divider()
st.caption(f"Botano+ Engine v5.0.1 - Última atualização: {datetime.now().strftime('%H:%M:%S')}")
