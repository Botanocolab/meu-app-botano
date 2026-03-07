import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timezone
from supabase import create_client
import altair as alt

# =====================================
# CONFIG
# =====================================
st.set_page_config(
    page_title="BOTANO+ | Value Betting Engine PRO",
    layout="wide"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
BANKROLL_INICIAL = float(st.secrets.get("BANKROLL_INICIAL", 1500))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================
# SESSION STATE
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

h1, h2, h3 {
    color: #ff5a2a !important;
    font-weight: 800 !important;
}

p, span, label, div {
    color: white;
}

/* ===== BOTÕES ===== */
div.stButton > button{
    background: linear-gradient(135deg,#ff5a2a 0%,#ff7a1a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 46px !important;
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

/* ===== MÉTRICAS ===== */
[data-testid="stMetric"]{
    background:#161616;
    border:1px solid #2a2a2a;
    border-radius:16px;
    padding:12px;
}

[data-testid="stMetricLabel"]{
    color:#cfcfcf !important;
    font-weight:700 !important;
}

[data-testid="stMetricValue"]{
    color:white !important;
    font-weight:800 !important;
}

/* ===== INPUTS / SELECTS ===== */
.stSelectbox label,
.stCheckbox label,
.stNumberInput label,
.stTextInput label {
    color: white !important;
    font-weight: 700 !important;
}

/* Caixa fechada do select */
div[data-baseweb="select"] > div {
    background: #1b1b1b !important;
    border: 1px solid #333 !important;
    color: white !important;
}

/* Texto do valor selecionado */
div[data-baseweb="select"] span {
    color: white !important;
}

/* Dropdown aberto */
ul[role="listbox"] {
    background: #1a1a1a !important;
    color: white !important;
    border: 1px solid #333 !important;
}

ul[role="listbox"] li {
    background: #1a1a1a !important;
    color: white !important;
}

ul[role="listbox"] li:hover {
    background: #2b2b2b !important;
    color: white !important;
}

/* Inputs numéricos e texto */
div[data-baseweb="input"] > div {
    background:#1b1b1b !important;
    color:white !important;
    border:1px solid #333 !important;
}

input {
    color:white !important;
    -webkit-text-fill-color: white !important;
    background: transparent !important;
}

/* Checkbox */
input[type="checkbox"] {
    accent-color: #ff6a00;
}

/* ===== CARDS ===== */
.botano-card{
    background:#1c1c1c;
    border:1px solid #2c2c2c;
    border-left:4px solid #ff5a2a;
    border-radius:18px;
    padding:18px;
    margin-bottom:14px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.25);
}

.botano-title{
    color:#ff5a2a;
    font-size:22px;
    font-weight:800;
    margin-bottom:10px;
}

.botano-sub{
    color:#d7d7d7 !important;
    font-size:15px;
    margin-bottom:12px;
}

.botano-grid{
    display:grid;
    grid-template-columns: repeat(2, minmax(180px, 1fr));
    gap:10px;
    margin-top:12px;
}

.botano-item{
    background:#151515;
    border:1px solid #2b2b2b;
    border-radius:12px;
    padding:10px 12px;
}

.botano-item-label{
    color:#a9a9a9 !important;
    font-size:12px;
    font-weight:700;
    margin-bottom:4px;
}

.botano-item-value{
    color:white !important;
    font-size:18px;
    font-weight:800;
}

.badge{
    display:inline-block;
    padding:6px 10px;
    border-radius:999px;
    font-size:12px;
    font-weight:800;
    margin-right:8px;
    margin-bottom:8px;
}

.badge-ev{
    background:#2b1a12;
    border:1px solid #ff7a1a;
    color:#ffb38a !important;
}

.badge-score{
    background:#171f15;
    border:1px solid #4caf50;
    color:#b9f2c1 !important;
}

.badge-stake{
    background:#151d24;
    border:1px solid #4ea3ff;
    color:#a8d3ff !important;
}

.badge-conf{
    background:#211825;
    border:1px solid #bb86fc;
    color:#d9b8ff !important;
}

/* ===== GLOSSÁRIO ===== */
.gloss-card{
    background:#181818;
    border:1px solid #2c2c2c;
    border-left:4px solid #ff5a2a;
    border-radius:18px;
    padding:18px;
    margin-bottom:14px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.25);
}

.gloss-title{
    color:#ff5a2a;
    font-size:22px;
    font-weight:800;
    margin-bottom:8px;
}

.gloss-text{
    color:white !important;
    font-size:16px;
    line-height:1.7;
}

hr{
    border-color:#262626 !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# HELPERS
# =====================================
def score_botano(ev_percent, fair_prob_percent, odd):
    return round((ev_percent * 8) + (fair_prob_percent * 0.3) - (odd * 1.2), 2)

def nivel_confianca(score):
    if score >= 95:
        return "Muito Alta"
    if score >= 75:
        return "Alta"
    if score >= 55:
        return "Boa"
    if score >= 40:
        return "Moderada"
    return "Baixa"

def hoje_filter(data):
    try:
        dt = datetime.fromisoformat(data.replace("Z", "+00:00"))
        return dt.date() == datetime.utcnow().date()
    except Exception:
        return False

# =====================================
# GLOSSÁRIO
# =====================================
def render_glossario():
    top1, top2 = st.columns([6, 2])

    with top1:
        st.markdown("<h1>📘 Glossário do BOTANO+</h1>", unsafe_allow_html=True)

    with top2:
        st.write("")
        st.button("⬅ Voltar ao painel principal", on_click=voltar_painel)

    cards = [
        ("Odd", "É o número que mostra quanto a aposta paga.<br><br>Exemplo:<br>Odd 2.00 = se acertar, recebe o dobro.<br>Odd 3.00 = paga mais.<br><br>Forma simples de explicar: <b>é o preço da aposta</b>."),
        ("EV", "EV é a vantagem matemática da aposta.<br><br>Quando o EV está positivo, significa que a aposta parece boa pelas contas.<br><br>Forma simples de explicar: <b>é se a aposta vale a pena ou não</b>."),
        ("Stake", "Stake é quanto do seu dinheiro o sistema recomenda apostar.<br><br>Exemplo:<br>Se sua banca é R$ 1.500 e a stake for 2%, a aposta sugerida é R$ 30.<br><br>Forma simples de explicar: <b>é quanto colocar na aposta com segurança</b>."),
        ("Odd Média", "É a média das odds oferecidas por várias casas.<br><br>Forma simples de explicar: <b>é o preço médio da aposta no mercado</b>."),
        ("Fair Probability", "É a chance estimada de um resultado acontecer, com base nas odds médias.<br><br>Forma simples de explicar: <b>é a chance real que o sistema enxerga</b>."),
        ("Saldo Atual", "É quanto dinheiro você tem agora na simulação.<br><br>Forma simples de explicar: <b>é o dinheiro que está no cofrinho neste momento</b>."),
        ("Lucro Total", "Mostra quanto você ganhou ou perdeu no total.<br><br>Forma simples de explicar: <b>é a conta geral do que entrou e saiu</b>."),
        ("ROI", "ROI mostra se o dinheiro apostado está dando retorno.<br><br>Forma simples de explicar: <b>é se o dinheiro investido está rendendo</b>."),
        ("Winrate", "É a porcentagem de apostas ganhas.<br><br>Forma simples de explicar: <b>é a taxa de acerto</b>."),
        ("Green", "Green quer dizer aposta ganha.<br><br>Forma simples de explicar: <b>foi acerto</b>."),
        ("Red", "Red quer dizer aposta perdida.<br><br>Forma simples de explicar: <b>foi erro</b>."),
        ("CLV", "CLV compara a odd que você pegou com a odd que o mercado ficou depois.<br><br>Se você pegou uma odd melhor antes dela cair, isso é bom.<br><br>Forma simples de explicar: <b>é ver se você pegou um preço bom antes da mudança</b>."),
        ("Score BOTANO", "É a nota geral que o sistema dá para a aposta.<br><br>Quanto maior o score, melhor a oportunidade parece.<br><br>Forma simples de explicar: <b>é a nota da aposta</b>."),
        ("Evolução da Banca", "É o gráfico que mostra se seu dinheiro está subindo, caindo ou parado.<br><br>Forma simples de explicar: <b>é o desenho do seu dinheiro ao longo do tempo</b>."),
    ]

    for titulo, texto in cards:
        st.markdown(f"""
        <div class="gloss-card">
            <div class="gloss-title">{titulo}</div>
            <div class="gloss-text">{texto}</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================
# GLOSSÁRIO MODE
# =====================================
if st.session_state["pagina"] == "glossario":
    render_glossario()
    st.stop()

# =====================================
# HEADER
# =====================================
c_head_1, c_head_2 = st.columns([7, 2])

with c_head_1:
    st.markdown("""
    <h1>⚡ BOTANO+ <span style='font-size:18px;color:white;font-weight:400'>Value Betting Engine PRO</span></h1>
    """, unsafe_allow_html=True)

with c_head_2:
    st.write("")
    st.button("📘 Abrir Glossário", on_click=abrir_glossario)

# =====================================
# LIGAS E FILTROS
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

    r = requests.get(url, params=params, timeout=30)

    if r.status_code != 200:
        return pd.DataFrame(), r.text

    data = r.json()

    if not data:
        return pd.DataFrame(), "Sem jogos"

    return pd.DataFrame(data), None

# =====================================
# EXTRATOR
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

            for market in book.get("markets", []):
                if market.get("key") != "h2h":
                    continue

                for outcome in market.get("outcomes", []):
                    name = outcome.get("name")
                    price = outcome.get("price")

                    if name is None or price is None:
                        continue

                    odds_media.setdefault(name, []).append(price)

                    if name not in best_odds or price > best_odds[name]:
                        best_odds[name] = price
                        casa[name] = nome_book

        for outcome in best_odds:
            if not odds_media.get(outcome):
                continue

            best_odd = float(best_odds[outcome])
            avg_odd = sum(odds_media[outcome]) / len(odds_media[outcome])

            fair_prob = 1 / avg_odd
            fair_prob_percent = round(fair_prob * 100, 2)

            ev = (fair_prob * best_odd) - 1
            ev_percent = round(ev * 100, 2)

            if ev_percent < 1:
                continue

            stake_pct = 0.5
            if ev_percent >= 4:
                stake_pct = 1.0
            if ev_percent >= 7:
                stake_pct = 2.0
            if ev_percent >= 10:
                stake_pct = 3.0

            stake_valor = round(BANKROLL_INICIAL * (stake_pct / 100), 2)
            score = score_botano(ev_percent, fair_prob_percent, best_odd)
            confianca = nivel_confianca(score)

            oportunidades.append({
                "evento": f"{home} x {away}",
                "selecao": outcome,
                "odd": round(best_odd, 2),
                "odd_media": round(avg_odd, 2),
                "fair_prob": fair_prob_percent,
                "ev": ev_percent,
                "score_botano": score,
                "confianca": confianca,
                "stake_pct": stake_pct,
                "stake_valor": stake_valor,
                "casa": casa[outcome],
                "commence": commence
            })

    df_op = pd.DataFrame(oportunidades)

    if df_op.empty:
        return df_op

    return df_op.sort_values(["score_botano", "ev"], ascending=False)

# =====================================
# DADOS
# =====================================
df_odds, erro = buscar_odds(liga_api)
df_op = extrair_oportunidades(df_odds)

if filtro_hoje and not df_op.empty:
    df_op = df_op[df_op["commence"].apply(hoje_filter)]

# =====================================
# HISTÓRICO BASE
# =====================================
hist = supabase.table("apostas_simuladas").select("*").execute()
df_hist = pd.DataFrame(hist.data)

if df_hist.empty:
    df_hist = pd.DataFrame(columns=["id", "stake", "odd", "resultado", "evento"])

# =====================================
# CÁLCULO DE BANCA
# =====================================
bankroll = BANKROLL_INICIAL
lucro_total = 0
greens = 0
reds = 0

for _, r in df_hist.iterrows():
    stake = float(r.get("stake", 0) or 0)
    odd = float(r.get("odd", 1) or 1)
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
# MÉTRICAS
# =====================================
m1, m2, m3, m4 = st.columns(4)
m1.metric("Saldo Atual", f"R$ {round(bankroll, 2)}")
m2.metric("Lucro Total", f"R$ {round(lucro_total, 2)}")
m3.metric("ROI", f"{round(roi, 2)}%")
m4.metric("Winrate", f"{round(winrate, 1)}%")

st.markdown("---")

# =====================================
# SIMULADOR RÁPIDO
# =====================================
st.markdown("### 🎯 Simulador Rápido")

sim1, sim2, sim3 = st.columns([3, 1, 1])

with sim1:
    evento_sim = st.text_input("Evento", value="")

with sim2:
    odd_sim = st.number_input("Odd", min_value=1.01, value=2.00, step=0.01)

with sim3:
    stake_sim = st.number_input("Stake (R$)", min_value=1.0, value=20.0, step=1.0)

lucro_potencial = round(stake_sim * (odd_sim - 1), 2)
retorno_total = round(stake_sim * odd_sim, 2)

s1, s2 = st.columns(2)
s1.metric("Lucro Potencial", f"R$ {lucro_potencial}")
s2.metric("Retorno Total", f"R$ {retorno_total}")

st.markdown("---")

# =====================================
# OPORTUNIDADES
# =====================================
st.subheader("🔥 Ranking das Melhores Oportunidades")

if erro:
    st.error(erro)

elif df_op.empty:
    st.info("Nenhuma oportunidade encontrada")

else:
    for i, row in df_op.head(15).iterrows():
        st.markdown(f"""
        <div class="botano-card">
            <div class="botano-title">{row['evento']}</div>
            <div class="botano-sub">Seleção: <b>{row['selecao']}</b> | Casa: <b>{row['casa']}</b></div>

            <span class="badge badge-ev">EV {row['ev']}%</span>
            <span class="badge badge-score">Score {row['score_botano']}</span>
            <span class="badge badge-stake">Stake {row['stake_pct']}% (R$ {row['stake_valor']})</span>
            <span class="badge badge-conf">Confiança {row['confianca']}</span>

            <div class="botano-grid">
                <div class="botano-item">
                    <div class="botano-item-label">Melhor odd</div>
                    <div class="botano-item-value">{row['odd']}</div>
                </div>
                <div class="botano-item">
                    <div class="botano-item-label">Odd média</div>
                    <div class="botano-item-value">{row['odd_media']}</div>
                </div>
                <div class="botano-item">
                    <div class="botano-item-label">Probabilidade justa</div>
                    <div class="botano-item-value">{row['fair_prob']}%</div>
                </div>
                <div class="botano-item">
                    <div class="botano-item-label">Stake sugerida</div>
                    <div class="botano-item-value">R$ {row['stake_valor']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🟧 Apostar no simulador", key=f"apostar_{i}"):
            payload = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "evento": row["evento"],
                "selecao": row["selecao"],
                "odd": float(row["odd"]),
                "stake": float(row["stake_valor"]),
                "ev": float(row["ev"]),
                "score_botano": float(row["score_botano"]),
                "casa": row["casa"],
                "resultado": "pendente"
            }
            supabase.table("apostas_simuladas").insert(payload).execute()
            st.success("Aposta adicionada ao simulador / histórico.")
            st.rerun()

# =====================================
# HISTÓRICO
# =====================================
st.subheader("📚 Histórico de Apostas")

hist = supabase.table("apostas_simuladas").select("*").execute()
df_hist = pd.DataFrame(hist.data)

if df_hist.empty:
    df_hist = pd.DataFrame(columns=["id", "evento", "odd", "stake", "resultado"])

if filtro_finalizadas and not df_hist.empty:
    df_hist = df_hist[df_hist["resultado"] != "pendente"]

if df_hist.empty:
    st.info("Sem apostas registradas.")

else:
    for i, row in df_hist.iterrows():
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

        with c1:
            st.write(row.get("evento", ""))

        with c2:
            st.write(f"Odd {row.get('odd', 1)}")

        with c3:
            st.write(f"Stake R$ {row.get('stake', 0)}")

        resultado_atual = row.get("resultado", "pendente")
        opcoes = ["pendente", "green", "red"]
        indice = opcoes.index(resultado_atual) if resultado_atual in opcoes else 0

        with c4:
            resultado = st.selectbox(
                "Resultado",
                opcoes,
                index=indice,
                key=f"res_{i}"
            )

        if st.button("Salvar resultado", key=f"save_{i}"):
            supabase.table("apostas_simuladas").update(
                {"resultado": resultado}
            ).eq("id", row["id"]).execute()
            st.success("Resultado atualizado.")
            st.rerun()

# =====================================
# GRÁFICO
# =====================================
st.subheader("📈 Evolução da Banca")

saldo = BANKROLL_INICIAL
historia = [saldo]

for _, r in df_hist.iterrows():
    stake = float(r.get("stake", 0) or 0)
    odd = float(r.get("odd", 1) or 1)
    resultado = r.get("resultado", "pendente")

    if resultado == "green":
        saldo += stake * (odd - 1)

    if resultado == "red":
        saldo -= stake

    historia.append(round(saldo, 2))

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
