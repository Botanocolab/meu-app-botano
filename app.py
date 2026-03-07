import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timezone
from supabase import create_client

# =====================================
# CONFIG
# =====================================
st.set_page_config(page_title="BOTANO+ | Value Betting Engine", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]

BANKROLL = 1500

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================
# CSS
# =====================================
st.markdown("""
<style>

.stApp{
background:linear-gradient(180deg,#0b0b0c 0%,#141414 100%);
color:white;
}

label,p,span{
color:white!important;
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
padding:18px;
margin-bottom:14px;
}

.botano-titulo{
color:#ff5a2a;
font-size:20px;
font-weight:800;
margin-bottom:8px;
}

.botano-metric{
color:white;
font-size:14px;
margin-bottom:6px;
}

.botano-highlight{
color:#7CFFB2;
font-weight:800;
}

.botano-ev{
color:#FFD166;
font-weight:800;
}

.metric-box{
background:#161616;
border:1px solid #2a2a2a;
border-radius:16px;
padding:16px;
text-align:center;
margin-bottom:20px;
}

.metric-title{
color:white;
font-size:12px;
}

.metric-value{
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

</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown("""
<h1>⚡ BOTANO+ <span style='font-size:18px;color:white;font-weight:400'>Value Betting Engine</span></h1>
""", unsafe_allow_html=True)

# =====================================
# FILTROS
# =====================================
colf1, colf2, colf3 = st.columns(3)

ligas = {
"Brasileirão Série A": "soccer_brazil_campeonato",
"Premier League": "soccer_epl",
"Champions League": "soccer_uefa_champs_league"
}

with colf1:
    liga_nome = st.selectbox("Liga", list(ligas.keys()))

with colf2:
    filtro_hoje = st.checkbox("Mostrar apenas jogos de hoje", value=True)

with colf3:
    filtro_resultados = st.checkbox("Mostrar apenas apostas finalizadas")

liga_api = ligas[liga_nome]

# =====================================
# API
# =====================================
@st.cache_data(ttl=60)
def buscar_odds(liga):

    url=f"https://api.the-odds-api.com/v4/sports/{liga}/odds"

    params={
        "apiKey":ODDS_API_KEY,
        "regions":"eu,uk",
        "markets":"h2h",
        "oddsFormat":"decimal",
        "dateFormat":"iso"
    }

    r=requests.get(url,params=params,timeout=15)

    if r.status_code!=200:
        return pd.DataFrame(),r.text

    data=r.json()

    if not data:
        return pd.DataFrame(),"Sem jogos retornados"

    return pd.DataFrame(data),None

# =====================================
# SCANNER
# =====================================
def extrair_oportunidades(df):

    oportunidades=[]

    if df.empty:
        return pd.DataFrame()

    for _,row in df.iterrows():

        home=row["home_team"]
        away=row["away_team"]
        commence=row["commence_time"]

        bookmakers=row["bookmakers"]

        melhores_odds={}
        odds_lista={}
        casa={}

        for book in bookmakers:

            book_title=book.get("title","book")

            for market in book["markets"]:

                if market["key"]!="h2h":
                    continue

                for outcome in market["outcomes"]:

                    nome=outcome["name"]
                    price=outcome["price"]

                    odds_lista.setdefault(nome,[]).append(price)

                    if nome not in melhores_odds or price>melhores_odds[nome]:
                        melhores_odds[nome]=price
                        casa[nome]=book_title

        for outcome in melhores_odds:

            best_odd=melhores_odds[outcome]
            avg_odd=sum(odds_lista[outcome])/len(odds_lista[outcome])

            fair_prob=1/avg_odd
            ev=(fair_prob*best_odd)-1
            ev_percent=round(ev*100,2)

            if ev_percent<1:
                continue

            stake_pct=0.5
            if ev_percent>=4: stake_pct=1
            if ev_percent>=7: stake_pct=2
            if ev_percent>=10: stake_pct=3

            stake_valor=round(BANKROLL*(stake_pct/100),2)

            oportunidades.append({
                "evento":f"{home} x {away}",
                "selecao":outcome,
                "odd":round(best_odd,2),
                "stake":stake_valor,
                "ev":ev_percent,
                "casa":casa[outcome],
                "commence":commence
            })

    df_op=pd.DataFrame(oportunidades)

    if df_op.empty:
        return df_op

    df_op=df_op.sort_values("ev",ascending=False)

    return df_op

# =====================================
# DATA
# =====================================
df_odds,erro=buscar_odds(liga_api)
df_op=extrair_oportunidades(df_odds)

# =====================================
# FILTRO HOJE
# =====================================
if filtro_hoje and not df_op.empty:

    hoje=datetime.utcnow().date()

    def jogo_hoje(data):
        try:
            dt=datetime.fromisoformat(data.replace("Z","+00:00"))
            return dt.date()==hoje
        except:
            return False

    df_op=df_op[df_op["commence"].apply(jogo_hoje)]

# =====================================
# BANKROLL
# =====================================
st.markdown(f"""
<div class="metric-box">
<div class="metric-title">SALDO SIMULADO</div>
<div class="metric-value">R$ {BANKROLL}</div>
</div>
""",unsafe_allow_html=True)

# =====================================
# OPORTUNIDADES
# =====================================
st.subheader("🔥 Oportunidades de Valor")

if erro:
    st.error(erro)

elif df_op.empty:
    st.info("Nenhuma oportunidade encontrada")

else:

    for i,row in df_op.head(20).iterrows():

        st.markdown(f"""
        <div class="botano-card">
        <div class="botano-titulo">{row['evento']}</div>
        <div class="botano-metric"><b>Entrada:</b> {row['selecao']}</div>
        <div class="botano-metric"><b>Casa:</b> {row['casa']}</div>
        <div class="botano-metric"><b>Odd:</b> {row['odd']}</div>
        <div class="botano-metric"><b>EV:</b> <span class="botano-ev">{row['ev']}%</span></div>
        <div class="botano-metric"><b>Stake:</b> <span class="botano-highlight">R$ {row['stake']}</span></div>
        </div>
        """,unsafe_allow_html=True)

        if st.button("APOSTAR",key=f"apostar{i}"):

            payload={
                "created_at":datetime.now(timezone.utc).isoformat(),
                "evento":row["evento"],
                "selecao":row["selecao"],
                "odd":row["odd"],
                "stake":row["stake"],
                "ev":row["ev"],
                "casa":row["casa"],
                "resultado":"pendente"
            }

            supabase.table("apostas_simuladas").insert(payload).execute()

            st.success("Aposta registrada")

# =====================================
# HISTORICO
# =====================================
st.markdown("### Histórico de Apostas")

hist=supabase.table("apostas_simuladas").select("*").execute()

df_hist=pd.DataFrame(hist.data)

if filtro_resultados and not df_hist.empty:
    df_hist=df_hist[df_hist["resultado"]!="pendente"]

if df_hist.empty:
    st.info("Sem apostas registradas")

else:

    for i,row in df_hist.iterrows():

        col1,col2,col3=st.columns([3,1,1])

        col1.write(row.get("evento",""))
        col2.write(f"Odd {row.get('odd',0)}")
        col3.write(f"Stake {row.get('stake',0)}")

# =====================================
# DEBUG
# =====================================
with st.expander("Debug API"):
    st.write("Liga:",liga_api)
    st.write("Erro:",erro)
    st.write("Jogos retornados:",len(df_odds))
    st.dataframe(df_odds.head())
