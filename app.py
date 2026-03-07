import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timezone
from supabase import create_client
import altair as alt

# =====================================
# CONFIG
# =====================================
st.set_page_config(page_title="BOTANO+ | Value Betting Engine PRO", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
BANKROLL_INICIAL = float(st.secrets.get("BANKROLL_INICIAL", 1500))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================
# NAVEGAÇÃO
# =====================================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "painel"

def abrir_glossario():
    st.session_state["pagina"] = "glossario"

def voltar_painel():
    st.session_state["pagina"] = "painel"

# =====================================
# CSS
# =====================================
st.markdown("""
<style>
.stApp{
    background: linear-gradient(180deg,#0b0b0c 0%,#141414 100%);
    color: white;
}

html, body, [class*="css"] {
    color: white !important;
}

label, span, p, div {
    color: white;
}

h1, h2, h3 {
    color: #ff5a2a !important;
    font-weight: 800 !important;
}

.botano-card{
    background: #1c1c1c;
    border: 1px solid #2c2c2c;
    border-left: 4px solid #ff5a2a;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22);
}

.botano-title{
    color: #ff5a2a;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 6px;
}

.metric-box{
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 16px;
    text-align: center;
}

.metric-value{
    font-size: 28px;
    font-weight: 800;
}

div.stButton > button{
    background: linear-gradient(135deg,#ff5a2a 0%,#ff7a1a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 52px !important;
    width: 100% !important;
    white-space: normal !important;
}

div.stButton > button:hover{
    color: white !important;
    border: none !important;
    opacity: 0.96;
}

div.stButton > button:focus,
div.stButton > button:active{
    color: white !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stMetric"] {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 10px;
}

[data-testid="stMetricLabel"] {
    color: #cfcfcf !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 800 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: #1a1a1a !important;
    color: white !important;
    border: 1px solid #333 !important;
}

div[data-baseweb="select"] * {
    color: white !important;
}

input {
    color: white !important;
}

.stSelectbox label,
.stCheckbox label {
    color: white !important;
    font-weight: 700 !important;
}

.gloss-card{
    background: #181818;
    border: 1px solid #2c2c2c;
    border-left: 4px solid #ff5a2a;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22);
}

.gloss-title{
    color: #ff5a2a;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}

.gloss-text{
    color: white;
    font-size: 16px;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# GLOSSÁRIO
# =====================================
def render_glossario():
    top1, top2 = st.columns([6, 2])

    with top1:
        st.markdown("""
        <h1>📘 Glossário do BOTANO+</h1>
        """, unsafe_allow_html=True)

    with top2:
        st.write("")
        st.button("⬅ Voltar ao painel principal", on_click=voltar_painel)

    cards = [
        (
            "Odd",
            "É o número que mostra quanto a aposta paga.<br><br>"
            "Exemplo:<br>"
            "Odd 2.00 = se acertar, recebe o dobro.<br>"
            "Odd 3.00 = paga mais.<br><br>"
            "Forma simples de explicar: <b>é o preço da aposta</b>."
        ),
        (
            "EV",
            "EV é a vantagem matemática da aposta.<br><br>"
            "Quando o EV está positivo, significa que a aposta parece boa pelas contas.<br><br>"
            "Forma simples de explicar: <b>é se a aposta vale a pena ou não</b>."
        ),
        (
            "Stake",
            "Stake é quanto do seu dinheiro o sistema recomenda apostar.<br><br>"
            "Exemplo:<br>"
            "Se sua banca é R$ 1.500 e a stake for 2%, a aposta sugerida é R$ 30.<br><br>"
            "Forma simples de explicar: <b>é quanto colocar na aposta com segurança</b>."
        ),
        (
            "Saldo Atual",
            "É quanto dinheiro você tem agora na simulação.<br><br>"
            "Forma simples de explicar: <b>é o dinheiro que está no cofrinho neste momento</b>."
        ),
        (
            "Lucro Total",
            "Mostra quanto você ganhou ou perdeu no total.<br><br>"
            "Forma simples de explicar: <b>é a conta geral do que entrou e saiu</b>."
        ),
        (
            "ROI",
            "ROI mostra se o dinheiro apostado está dando retorno.<br><br>"
            "Forma simples de explicar: <b>é se o dinheiro investido está rendendo</b>."
        ),
        (
            "Winrate",
            "É a porcentagem de apostas ganhas.<br><br>"
            "Forma simples de explicar: <b>é a taxa de acerto</b>."
        ),
        (
            "Green",
            "Green quer dizer aposta ganha.<br><br>"
            "Forma simples de explicar: <b>foi acerto</b>."
        ),
        (
            "Red",
            "Red quer dizer aposta perdida.<br><br>"
            "Forma simples de explicar: <b>foi erro</b>."
        ),
        (
            "CLV",
            "CLV compara a odd que você pegou com a odd que o mercado ficou depois.<br><br>"
            "Se você pegou uma odd melhor antes dela cair, isso é bom.<br><br>"
            "Forma simples de explicar: <b>é ver se você pegou um preço bom antes da mudança</b>."
        ),
        (
            "Score BOTANO",
            "É a nota geral que o sistema dá para a aposta.<br><br>"
            "Quanto maior o score, melhor a oportunidade parece.<br><br>"
            "Forma simples de explicar: <b>é a nota da aposta</b>."
        ),
        (
            "Evolução da Banca",
            "É o gráfico que mostra se seu dinheiro está subindo, caindo ou parado.<br><br>"
            "Forma simples de explicar: <b>é o desenho do seu dinheiro ao longo do tempo</b>."
        ),
    ]

    for titulo, texto in cards:
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">{titulo}</div>
            <div class="gloss-text">{texto}</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================
# SE ESTIVER NO GLOSSÁRIO, PARA AQUI
# =====================================
if st.session_state["pagina"] == "glossario":
    render_glossario()
    st.stop()

# =====================================
# HEADER
# =====================================
col_header_1, col_header_2 = st.columns([7, 2])

with col_header_1:
    st.markdown("""
    <h1>⚡ BOTANO+ <span style='font-size:18px;color:white;font-weight:400'>Value Betting Engine PRO</span></h1>
    """, unsafe_allow_html=True)

with col_header_2:
    st.write("")
    st.button("📘 Abrir Glossário", on_click=abrir_glossario)

# =====================================
# LIGAS
# =====================================
ligas = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl",
    "Champions League": "soccer_uefa_champs_league",
    "La Liga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga"
}

colf1, colf2, colf3 = st.columns(3)

with colf1:
    liga_nome = st.selectbox("Liga", list(ligas.keys()))

with colf2:
    filtro_hoje = st.checkbox("Mostrar apenas jogos de hoje", value=True)

with colf3:
    filtro_finalizadas = st.checkbox("Mostrar apenas apostas finalizadas")

liga_api = ligas[liga_nome]

# =====================================
# API
# =====================================
@st.cache_data(ttl=60)
def buscar_odds(liga):
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu,uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return pd.DataFrame(), r.text

    data = r.json()

    if not data:
        return pd.DataFrame(), "Sem jogos"

    return pd.DataFrame(data), None

# =====================================
# SCANNER VALUE
# =====================================
def extrair_oportunidades(df):
    oportunidades = []

    if df.empty:
        return pd.DataFrame()

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        commence = row["commence_time"]
        bookmakers = row["bookmakers"]

        best_odds = {}
        odds_media = {}
        casa = {}

        for book in bookmakers:
            nome_book = book.get("title", "book")

            for market in book["markets"]:
                if market["key"] != "h2h":
                    continue

                for outcome in market["outcomes"]:
                    name = outcome["name"]
                    price = outcome["price"]

                    odds_media.setdefault(name, []).append(price)

                    if name not in best_odds or price > best_odds[name]:
                        best_odds[name] = price
                        casa[name] = nome_book

        for outcome in best_odds:
            best_odd = best_odds[outcome]
            avg_odd = sum(odds_media[outcome]) / len(odds_media[outcome])

            fair_prob = 1 / avg_odd
            ev = (fair_prob * best_odd) - 1
            ev_percent = round(ev * 100, 2)

            if ev_percent < 1:
                continue

            stake_pct = 0.5
            if ev_percent >= 4:
                stake_pct = 1
            if ev_percent >= 7:
                stake_pct = 2
            if ev_percent >= 10:
                stake_pct = 3

            stake_valor = round(BANKROLL_INICIAL * (stake_pct / 100), 2)

            oportunidades.append({
                "evento": f"{home} x {away}",
                "selecao": outcome,
                "odd": round(best_odd, 2),
                "odd_media": round(avg_odd, 2),
                "ev": ev_percent,
                "stake_pct": stake_pct,
                "stake_valor": stake_valor,
                "casa": casa[outcome],
                "commence": commence
            })

    df_op = pd.DataFrame(oportunidades)

    if df_op.empty:
        return df_op

    df_op = df_op.sort_values("ev", ascending=False)
    return df_op

# =====================================
# DATA
# =====================================
df_odds, erro = buscar_odds(liga_api)
df_op = extrair_oportunidades(df_odds)

# =====================================
# FILTRO HOJE
# =====================================
if filtro_hoje and not df_op.empty:
    hoje = datetime.utcnow().date()

    def hoje_filter(data):
        try:
            dt = datetime.fromisoformat(data.replace("Z", "+00:00"))
            return dt.date() == hoje
        except:
            return False

    df_op = df_op[df_op["commence"].apply(hoje_filter)]

# =====================================
# HISTORICO
# =====================================
hist = supabase.table("apostas_simuladas").select("*").execute()
df_hist = pd.DataFrame(hist.data)

if df_hist.empty:
    df_hist = pd.DataFrame(columns=["stake", "odd", "resultado"])

# =====================================
# CALCULO BANCA
# =====================================
bankroll = BANKROLL_INICIAL
lucro_total = 0
greens = 0
reds = 0

for _, r in df_hist.iterrows():
    stake = r.get("stake", 0)
    odd = r.get("odd", 1)
    resultado = r.get("resultado", "pendente")

    if resultado == "green":
        lucro = stake * (odd - 1)
        bankroll += lucro
        lucro_total += lucro
        greens += 1

    if resultado == "red":
        bankroll -= stake
        lucro_total -= stake
        reds += 1

total_apostas = greens + reds
roi = (lucro_total / BANKROLL_INICIAL) * 100 if total_apostas > 0 else 0
winrate = (greens / total_apostas) * 100 if total_apostas > 0 else 0

# =====================================
# METRICS
# =====================================
m1, m2, m3, m4 = st.columns(4)

m1.metric("Saldo Atual", f"R$ {round(bankroll, 2)}")
m2.metric("Lucro Total", f"R$ {round(lucro_total, 2)}")
m3.metric("ROI", f"{round(roi, 2)}%")
m4.metric("Winrate", f"{round(winrate, 1)}%")

# =====================================
# OPORTUNIDADES
# =====================================
st.subheader("🔥 Oportunidades de Valor")

if erro:
    st.error(erro)

elif df_op.empty:
    st.info("Nenhuma oportunidade encontrada")

else:
    for i, row in df_op.head(15).iterrows():
        st.markdown(f"""
        <div class="botano-card">
            <div class="botano-title">{row['evento']}</div>
            Entrada: {row['selecao']} <br>
            Casa: {row['casa']} <br>
            Melhor odd: {row['odd']} | Média: {row['odd_media']} <br>
            EV: {row['ev']}% <br>
            Stake: {row['stake_pct']}% (R$ {row['stake_valor']})
        </div>
        """, unsafe_allow_html=True)

        if st.button("APOSTAR", key=f"a{i}"):
            payload = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "evento": row["evento"],
                "selecao": row["selecao"],
                "odd": row["odd"],
                "stake": row["stake_valor"],
                "ev": row["ev"],
                "casa": row["casa"],
                "resultado": "pendente"
            }

            supabase.table("apostas_simuladas").insert(payload).execute()
            st.success("Aposta registrada")

# =====================================
# HISTÓRICO
# =====================================
st.subheader("Histórico de Apostas")

hist = supabase.table("apostas_simuladas").select("*").execute()
df_hist = pd.DataFrame(hist.data)

if filtro_finalizadas and not df_hist.empty:
    df_hist = df_hist[df_hist["resultado"] != "pendente"]

if df_hist.empty:
    st.info("Sem apostas")

else:
    for i, row in df_hist.iterrows():
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

        c1.write(row.get("evento", ""))
        c2.write(f"Odd {row.get('odd', 1)}")
        c3.write(f"Stake {row.get('stake', 0)}")

        resultado_atual = row.get("resultado", "pendente")

        with c4:
            resultado = st.selectbox(
                "Resultado",
                ["pendente", "green", "red"],
                index=["pendente", "green", "red"].index(resultado_atual),
                key=f"res{i}"
            )

        if st.button("Salvar", key=f"save{i}"):
            supabase.table("apostas_simuladas").update(
                {"resultado": resultado}
            ).eq("id", row["id"]).execute()
            st.success("Resultado atualizado")

# =====================================
# GRAFICO BANCA
# =====================================
st.subheader("Evolução da Banca")

saldo = BANKROLL_INICIAL
historia = [saldo]

for _, r in df_hist.iterrows():
    stake = r.get("stake", 0)
    odd = r.get("odd", 1)
    resultado = r.get("resultado", "pendente")

    if resultado == "green":
        saldo += stake * (odd - 1)

    if resultado == "red":
        saldo -= stake

    historia.append(saldo)

df_chart = pd.DataFrame({
    "aposta": list(range(len(historia))),
    "banca": historia
})

chart = alt.Chart(df_chart).mark_line(point=True).encode(
    x=alt.X("aposta:Q", title="Apostas"),
    y=alt.Y("banca:Q", title="Banca")
).properties(height=350)

st.altair_chart(chart, use_container_width=True)

# =====================================
# DEBUG
# =====================================
with st.expander("Debug API"):
    st.write("Liga:", liga_api)
    st.write("Erro:", erro)
    st.write("Jogos retornados:", len(df_odds))
    st.dataframe(df_odds.head())
