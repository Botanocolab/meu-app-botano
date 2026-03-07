import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timezone
from typing import Any
from supabase import create_client

# =====================================
# CONFIG
# =====================================
st.set_page_config(page_title="BOTANO+ | Smart Betting Engine V5", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================
# SESSION
# =====================================
if "selecionado_evento" not in st.session_state:
    st.session_state["selecionado_evento"] = ""

if "selecionado_mercado" not in st.session_state:
    st.session_state["selecionado_mercado"] = ""

if "selecionado_odd" not in st.session_state:
    st.session_state["selecionado_odd"] = 1.50

# =====================================
# CSS
# =====================================
st.markdown("""
<style>
.stApp{
background:linear-gradient(180deg,#0b0b0c 0%,#141414 100%);
color:#ffffff;
}

h1,h2,h3{
color:#ff5a2a!important;
font-weight:800!important;
}

.botano-card{
background:#1c1c1c;
border:1px solid #2c2c2c;
border-left:4px solid #ff5a2a;
border-radius:16px;
padding:16px;
margin-bottom:12px;
box-shadow:0 6px 18px rgba(0,0,0,0.3);
}

.botano-titulo{
color:#ff5a2a;
font-weight:800;
font-size:18px;
margin-bottom:6px;
}

.botano-metric{
color:#d0d0d0;
font-size:14px;
margin-bottom:4px;
}

.side-card{
background:#161616;
border:1px solid #2c2c2c;
border-radius:16px;
padding:16px;
margin-top:12px;
}

.side-label{
font-size:12px;
color:#aaaaaa;
}

.side-value{
font-size:28px;
font-weight:800;
color:white;
}

div.stButton > button{
background:linear-gradient(135deg,#ff5a2a 0%,#ff7a1a 100%)!important;
color:white!important;
border:none!important;
border-radius:14px!important;
font-weight:700!important;
width:100%!important;
}

div[data-baseweb="select"]>div{
background:#232323!important;
color:white!important;
}

div[data-testid="stNumberInput"] input{
background:#232323!important;
color:white!important;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown("""
<h1>⚡ BOTANO+ <span style='font-size:18px;color:#cfcfcf;font-weight:400'>Smart Betting Engine V5</span></h1>
""", unsafe_allow_html=True)

# =====================================
# LIGAS
# =====================================
ligas = {
"Brasileirão Série A": "soccer_brazil_campeonato",
"Premier League": "soccer_epl",
"Champions League": "soccer_uefa_champs_league"
}

# =====================================
# API
# =====================================
@st.cache_data(ttl=60)
def buscar_odds(liga):

    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url, params=params, timeout=15)

        if r.status_code != 200:
            return pd.DataFrame(), r.text

        data = r.json()

        if not data:
            return pd.DataFrame(), "Sem jogos retornados pela API"

        return pd.DataFrame(data), None

    except Exception as e:
        return pd.DataFrame(), str(e)

# =====================================
# SCANNER
# =====================================
def extrair_oportunidades(df):

    oportunidades = []

    if df.empty:
        return pd.DataFrame()

    for _,row in df.iterrows():

        home = row["home_team"]
        away = row["away_team"]
        bookmakers = row["bookmakers"]

        melhores_odds={}
        odds_lista={}

        for book in bookmakers:

            for market in book["markets"]:

                if market["key"]!="h2h":
                    continue

                for outcome in market["outcomes"]:

                    nome=outcome["name"]
                    price=outcome["price"]

                    odds_lista.setdefault(nome,[]).append(price)

                    if nome not in melhores_odds or price>melhores_odds[nome]:
                        melhores_odds[nome]=price

        for outcome in melhores_odds:

            best_odd=melhores_odds[outcome]

            avg_odd=sum(odds_lista[outcome])/len(odds_lista[outcome])

            fair_prob=1/avg_odd

            ev=(fair_prob*best_odd)-1

            oportunidades.append({
                "evento":f"{home} x {away}",
                "selecao":outcome,
                "best_odd":round(best_odd,2),
                "avg_odd":round(avg_odd,2),
                "ev_percent":round(ev*100,2)
            })

    df_op=pd.DataFrame(oportunidades)

    df_op=df_op.sort_values("ev_percent",ascending=False)

    return df_op

# =====================================
# FILTROS
# =====================================
liga_nome=st.selectbox("Escolha a Liga:",list(ligas.keys()))

liga_api=ligas[liga_nome]

df_odds,erro=buscar_odds(liga_api)

df_oportunidades=extrair_oportunidades(df_odds)

# =====================================
# LAYOUT
# =====================================
col1,col2=st.columns([2,1])

# =====================================
# OPORTUNIDADES
# =====================================
with col1:

    st.subheader("🚀 Oportunidades com Valor")

    if erro:
        st.error(erro)

    elif df_oportunidades.empty:
        st.info("Nenhum jogo retornado pela API")

    else:

        for i,row in df_oportunidades.head(15).iterrows():

            st.markdown(f"""
            <div class='botano-card'>
            <div class='botano-titulo'>{row['evento']}</div>
            <div class='botano-metric'><b>Seleção:</b> {row['selecao']}</div>
            <div class='botano-metric'><b>Melhor odd:</b> {row['best_odd']}</div>
            <div class='botano-metric'><b>Odd média:</b> {row['avg_odd']}</div>
            <div class='botano-metric'><b>EV:</b> {row['ev_percent']}%</div>
            </div>
            """,unsafe_allow_html=True)

            if st.button(f"Apostar {row['selecao']} {row['best_odd']}",key=f"a{i}"):

                payload={
                    "created_at":datetime.now(timezone.utc).isoformat(),
                    "evento":row["evento"],
                    "odd":row["best_odd"],
                    "valor_apostado":10
                }

                supabase.table("apostas_simuladas").insert(payload).execute()

                st.success("Aposta registrada")

# =====================================
# SIMULADOR
# =====================================
with col2:

    st.subheader("🎯 Simulador & Gestão")

    valor=st.number_input("Valor (R$)",value=10.0)

    odd=st.number_input("Odd",value=1.50)

    retorno=valor*odd

    lucro=retorno-valor

    st.markdown(f"""
    <div class='side-card'>
    <div class='side-label'>Retorno Bruto</div>
    <div class='side-value'>R$ {retorno:.2f}</div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown(f"""
    <div class='side-card'>
    <div class='side-label'>Lucro Líquido</div>
    <div class='side-value'>R$ {lucro:.2f}</div>
    </div>
    """,unsafe_allow_html=True)

# =====================================
# HISTORICO
# =====================================
st.markdown("### 🧾 Histórico Real de Apostas")

try:

    hist=supabase.table("apostas_simuladas").select("*").execute()

    df_hist=pd.DataFrame(hist.data)

    if df_hist.empty:
        st.info("Sem histórico")

    else:
        st.dataframe(df_hist)

except:
    st.info("Tabela ainda não criada")

# =====================================
# DEBUG
# =====================================
with st.expander("🛠 Debug da API"):
    st.write("Liga:",liga_api)
    st.write("Erro:",erro)
    st.write("Linhas retornadas:",len(df_odds))
    st.dataframe(df_odds.head())
