import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =====================================
# CONFIGURAÇÃO
# =====================================
st.set_page_config(page_title="Botano+ | Engine", layout="wide")

# Histórico local temporário
if "historico_apostas" not in st.session_state:
    st.session_state["historico_apostas"] = []

# =====================================
# CSS - VOLTANDO PARA O ESTILO MELHOR
# =====================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #111111 0%, #191919 100%);
        color: #ffffff;
    }

    h1, h2, h3 {
        color: #ff5a2a !important;
        font-weight: 800 !important;
    }

    .botano-card {
        background: #202020;
        border: 1px solid #333333;
        border-left: 4px solid #ff5a2a;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.22);
    }

    .botano-titulo {
        color: #ff5a2a;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .botano-metric {
        font-size: 0.95rem;
        color: #d0d0d0;
        margin-bottom: 4px;
    }

    .botano-strong {
        color: #ffffff;
        font-weight: 700;
    }

    .side-card {
        background: #181818;
        border: 1px solid #2b2b2b;
        border-radius: 16px;
        padding: 16px;
        margin-top: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    }

    .side-label {
        color: #b8b8b8;
        font-size: 13px;
        margin-bottom: 6px;
    }

    .side-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        line-height: 1;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff5a2a 0%, #ff7a1a 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        width: 100% !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
    }

    div.stButton > button:hover {
        filter: brightness(1.05);
    }

    div[data-baseweb="select"] > div {
        background-color: #232323 !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid #3a3a3a !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown("""
<h1 style='display:flex;align-items:center;gap:10px'>
⚡ <span style="color:#ff5a2a">BOTANO+</span>
<span style="font-size:18px;color:#c9c9c9;font-weight:400">Smart Betting Engine</span>
</h1>
""", unsafe_allow_html=True)

# =====================================
# DADOS MOCK PARA TESTE VISUAL
# Depois trocamos pelos dados reais da API
# =====================================
ligas = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl"
}

liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))

dados_mock = [
    {
        "evento": "Mirassol x Santos",
        "selecao": "Mirassol",
        "mercado": "Vitória do Mirassol",
        "odd": 2.05,
        "ev": 6.6,
        "score": 65.9,
        "confianca": "Alta"
    },
    {
        "evento": "Atlético Mineiro x Internacional",
        "selecao": "Atlético Mineiro",
        "mercado": "Vitória do Atlético Mineiro",
        "odd": 2.05,
        "ev": 6.6,
        "score": 65.9,
        "confianca": "Alta"
    },
    {
        "evento": "Athletico Paranaense x Botafogo",
        "selecao": "Athletico Paranaense",
        "mercado": "Vitória do Athletico Paranaense",
        "odd": 2.05,
        "ev": 6.6,
        "score": 65.9,
        "confianca": "Alta"
    },
    {
        "evento": "Bahia x Vitória",
        "selecao": "Bahia",
        "mercado": "Vitória do Bahia",
        "odd": 2.05,
        "ev": 6.6,
        "score": 65.9,
        "confianca": "Alta"
    }
]

# =====================================
# FUNÇÕES
# =====================================
def registrar_aposta_local(evento, selecao, mercado, odd, ev, score, valor=10.0):
    registro = {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "evento": evento,
        "selecao": selecao,
        "mercado": mercado,
        "odd": odd,
        "ev_%": ev,
        "score": score,
        "valor_apostado": valor,
        "status": "Pendente"
    }
    st.session_state["historico_apostas"].insert(0, registro)

# =====================================
# LAYOUT
# =====================================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Oportunidades com Valor")

    for i, op in enumerate(dados_mock):
        st.markdown(f"""
        <div class="botano-card">
            <div class="botano-titulo">{op['evento']}</div>
            <div class="botano-metric"><span class="botano-strong">Entrada recomendada:</span> {op['mercado']}</div>
            <div class="botano-metric"><span class="botano-strong">Seleção:</span> {op['selecao']}</div>
            <div class="botano-metric"><span class="botano-strong">Odd:</span> {op['odd']}</div>
            <div class="botano-metric"><span class="botano-strong">EV:</span> {op['ev']}%</div>
            <div class="botano-metric"><span class="botano-strong">Score Botano:</span> {op['score']}</div>
            <div class="botano-metric"><span class="botano-strong">Confiança:</span> {op['confianca']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            f"Apostar em: {op['mercado']} | Odd {op['odd']}",
            key=f"apostar_{i}"
        ):
            registrar_aposta_local(
                evento=op["evento"],
                selecao=op["selecao"],
                mercado=op["mercado"],
                odd=op["odd"],
                ev=op["ev"],
                score=op["score"],
                valor=10.0
            )
            st.success(f"Aposta registrada: {op['mercado']} em {op['evento']}")

with col_right:
    st.subheader("🎯 Simulador & Gestão")

    with st.form("sim_form"):
        valor = st.number_input("Valor (R$):", value=10.0, min_value=0.0)
        odd = st.number_input("Odd:", value=1.5, min_value=1.01)

        retorno_bruto = round(valor * odd, 2)
        lucro_liquido = round(retorno_bruto - valor, 2)

        st.markdown(f"""
        <div class="side-card">
            <div class="side-label">Retorno Bruto</div>
            <div class="side-value">R$ {retorno_bruto}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="side-card">
            <div class="side-label">Lucro Líquido</div>
            <div class="side-value">R$ {lucro_liquido}</div>
        </div>
        """, unsafe_allow_html=True)

        st.form_submit_button("Registrar Aposta Manual")

    st.markdown("""
    <div class="side-card">
        <div class="side-label">ROI Estimado</div>
        <div class="side-value">+12.4%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="side-card">
        <div class="side-label">Win Rate</div>
        <div class="side-value">58%</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# HISTÓRICO
# =====================================
st.markdown("### 🧾 Histórico de Apostas")

if st.session_state["historico_apostas"]:
    df_hist = pd.DataFrame(st.session_state["historico_apostas"])
    st.dataframe(df_hist, use_container_width=True)
else:
    st.info("Nenhuma aposta registrada ainda.")
