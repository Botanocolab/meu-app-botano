import math
from datetime import datetime, timezone

import altair as alt
import pandas as pd
import requests
import streamlit as st
from supabase import create_client

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
# CSS
# =====================================
st.markdown("""
<style>
:root{
    --bg-1:#070707;
    --bg-2:#111111;
    --card:#181818;
    --card-2:#1f1f1f;
    --border:#2c2c2c;
    --orange:#ff5a2a;
    --orange-2:#ff7a1a;
    --white:#ffffff;
    --muted:#d5d5d5;
    --green:#7CFFB2;
    --yellow:#FFD166;
    --red:#FF8FA3;
}

.stApp{
    background:linear-gradient(180deg,var(--bg-1) 0%,var(--bg-2) 100%);
    color:var(--white);
}

.block-container{
    padding-top:2rem;
    padding-bottom:3rem;
}

h1,h2,h3{
    color:var(--orange)!important;
    font-weight:800!important;
    letter-spacing:-0.02em;
}

p, span, label, div{
    color:var(--white);
}

small{
    color:var(--muted)!important;
}

.botano-card{
    background:linear-gradient(180deg,#1b1b1b 0%, #171717 100%);
    border:1px solid var(--border);
    border-left:5px solid var(--orange);
    border-radius:22px;
    padding:22px;
    margin-bottom:18px;
    box-shadow:0 12px 30px rgba(0,0,0,0.35);
}

.botano-title{
    color:var(--orange);
    font-size:24px;
    font-weight:800;
    margin-bottom:12px;
}

.botano-sub{
    color:var(--white);
    font-size:15px;
    margin-bottom:8px;
    line-height:1.45;
}

.metric-box{
    background:linear-gradient(180deg,#161616 0%, #121212 100%);
    border:1px solid var(--border);
    border-radius:20px;
    padding:18px;
    text-align:center;
    margin-bottom:10px;
    min-height:104px;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.metric-title{
    color:var(--muted);
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:0.08em;
    margin-bottom:8px;
}

.metric-value{
    color:var(--white);
    font-size:22px;
    font-weight:800;
}

.section-title{
    color:var(--orange);
    font-size:20px;
    font-weight:800;
    margin: 12px 0 14px 0;
}

.ev{
    color:var(--yellow)!important;
    font-weight:800;
}

.good{
    color:var(--green)!important;
    font-weight:800;
}

.bad{
    color:var(--red)!important;
    font-weight:800;
}

.rank-card{
    background:linear-gradient(180deg,#161616 0%,#121212 100%);
    border:1px solid var(--border);
    border-radius:18px;
    padding:16px;
    margin-bottom:12px;
}

.rank-top{
    display:flex;
    justify-content:space-between;
    gap:14px;
    align-items:flex-start;
    margin-bottom:10px;
}

.rank-event{
    color:var(--white);
    font-weight:800;
    font-size:18px;
    line-height:1.3;
}

.rank-badge{
    background:linear-gradient(135deg,var(--orange) 0%,var(--orange-2) 100%);
    color:white!important;
    font-size:12px;
    font-weight:800;
    border-radius:999px;
    padding:6px 10px;
    white-space:nowrap;
}

.rank-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:10px;
}

.rank-item{
    background:#1d1d1d;
    border:1px solid #2b2b2b;
    border-radius:14px;
    padding:10px 12px;
}

.rank-label{
    color:#bdbdbd!important;
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:0.05em;
    margin-bottom:4px;
}

.rank-value{
    color:white!important;
    font-size:15px;
    font-weight:700;
}

.filter-box{
    background:linear-gradient(180deg,#141414 0%, #111111 100%);
    border:1px solid var(--border);
    border-radius:18px;
    padding:14px;
    margin-bottom:18px;
}

/* INPUTS / FILTROS */
div[data-baseweb="select"] > div{
    background:#1e1e1e!important;
    color:white!important;
    border:1px solid #444!important;
    border-radius:14px!important;
}

div[data-baseweb="select"] *{
    color:white!important;
}

div[data-baseweb="popover"] *{
    color:#111!important;
}

div[data-testid="stNumberInput"] input{
    background:#1e1e1e!important;
    color:white!important;
    -webkit-text-fill-color:white!important;
    border-radius:14px!important;
}

div[data-testid="stNumberInput"] button{
    background:#2a2a2a!important;
    color:white!important;
    border:none!important;
}

div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] span,
div[data-testid="stCheckbox"] p{
    color:white!important;
    font-weight:700!important;
}

div[data-testid="stCheckbox"] input{
    accent-color:var(--orange)!important;
}

label[data-testid="stWidgetLabel"]{
    color:white!important;
    font-weight:800!important;
}

[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stCheckbox"] label{
    color:white!important;
    font-weight:800!important;
}

/* BUTTONS */
div.stButton > button{
    background:linear-gradient(135deg,var(--orange) 0%,var(--orange-2) 100%) !important;
    color:white !important;
    border:none !important;
    border-radius:14px !important;
    font-weight:800 !important;
    width:100% !important;
    min-height:48px;
    box-shadow:0 8px 18px rgba(255,90,42,0.18);
}

div.stButton > button:hover{
    filter:brightness(1.05)!important;
}

a[kind="secondary"]{
    background:linear-gradient(135deg,var(--orange) 0%,var(--orange-2) 100%) !important;
    color:white !important;
    border:none !important;
    border-radius:14px !important;
    font-weight:800 !important;
}

div.stLinkButton > a{
    background:linear-gradient(135deg,var(--orange) 0%,var(--orange-2) 100%) !important;
    color:white !important;
    border:none !important;
    border-radius:14px !important;
    font-weight:800 !important;
    text-decoration:none !important;
}

/* DATAFRAME */
div[data-testid="stDataFrame"]{
    border-radius:18px;
    overflow:hidden;
}

div[data-testid="stExpander"] details{
    background:#141414!important;
    border:1px solid var(--border)!important;
    border-radius:16px!important;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# HELPERS
# =====================================
def brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(v: float) -> str:
    return f"{v:.2f}%"

def safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default

def parse_dt_utc(s: str):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None

def fmt_dt_br(s: str) -> str:
    dt = parse_dt_utc(s)
    if not dt:
        return "-"
    return dt.astimezone(timezone.utc).strftime("%d/%m %H:%M UTC")

def normalize_result(v: str) -> str:
    if v in ["pendente", "green", "red"]:
        return v
    return "pendente"

def poisson_prob(lmbda: float, k: int) -> float:
    try:
        return math.exp(-lmbda) * (lmbda ** k) / math.factorial(k)
    except Exception:
        return 0.0

def poisson_1x2(home_exp: float, away_exp: float, max_goals: int = 7):
    p_home = 0.0
    p_draw = 0.0
    p_away = 0.0

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            ph = poisson_prob(home_exp, h)
            pa = poisson_prob(away_exp, a)
            p = ph * pa
            if h > a:
                p_home += p
            elif h == a:
                p_draw += p
            else:
                p_away += p

    total = p_home + p_draw + p_away
    if total > 0:
        p_home /= total
        p_draw /= total
        p_away /= total

    return {"home": p_home, "draw": p_draw, "away": p_away}

def team_strength_score(name: str) -> float:
    n = (name or "").lower()

    strong = [
        "flamengo", "palmeiras", "botafogo", "sao paulo", "são paulo", "corinthians",
        "gremio", "grêmio", "internacional", "atletico mineiro", "atlético mineiro",
        "cruzeiro", "fluminense", "liverpool", "arsenal", "man city", "manchester city",
        "real madrid", "barcelona", "bayern", "inter", "juventus", "psg"
    ]
    weak = [
        "chapecoense", "cuiaba", "cuiabá", "juventude", "mirassol", "vitoria", "vitória",
        "coritiba", "getafe", "almeria", "lecce", "cadiz", "cádiz", "remo"
    ]

    score = 0.0
    for t in strong:
        if t in n:
            score += 0.18
    for t in weak:
        if t in n:
            score -= 0.12

    score += ((sum(ord(c) for c in n) % 17) - 8) / 300
    return score

def estimate_goal_expectancy(home_team: str, away_team: str):
    base_home = 1.38
    base_away = 1.08

    home_adj = team_strength_score(home_team)
    away_adj = team_strength_score(away_team)

    home_exp = max(0.35, base_home + home_adj - (away_adj * 0.35))
    away_exp = max(0.25, base_away + away_adj - (home_adj * 0.25))

    return home_exp, away_exp

def outcome_key_for_selection(selection: str, home_team: str, away_team: str):
    if selection == home_team:
        return "home"
    if selection == away_team:
        return "away"
    if str(selection).lower() in ["draw", "empate"]:
        return "draw"
    return None

def botano_score(ev_percent: float, fair_prob_percent: float, best_odd: float, clv_percent: float = 0.0):
    return round((ev_percent * 7.5) + (fair_prob_percent * 0.35) + (clv_percent * 0.25) - (best_odd * 1.15), 2)

def kelly_fraction(prob: float, odd: float) -> float:
    b = odd - 1
    if b <= 0:
        return 0.0
    q = 1 - prob
    raw = ((b * prob) - q) / b
    raw = max(0.0, raw)
    frac = raw * 0.25
    return min(frac, 0.05)

def implied_prob_from_odd(odd: float) -> float:
    if odd <= 1:
        return 0.0
    return 1 / odd

def clv_percent(odd_entrada: float, odd_fechamento_atual: float) -> float:
    if odd_entrada <= 1 or odd_fechamento_atual <= 1:
        return 0.0
    return round(((odd_entrada / odd_fechamento_atual) - 1) * 100, 2)

# =====================================
# DB
# =====================================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
BANKROLL_INICIAL = float(st.secrets.get("BANKROLL_INICIAL", 1500))

# =====================================
# HEADER
# =====================================
st.markdown("""
<h1>⚡ BOTANO+ <span style='font-size:18px;color:white;font-weight:400'>Value Betting Engine PRO</span></h1>
""", unsafe_allow_html=True)

# =====================================
# GLOBAL LEAGUES
# =====================================
LIGAS = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl",
    "Champions League": "soccer_uefa_champs_league",
    "La Liga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga",
    "Ligue 1": "soccer_france_ligue_one",
    "Eredivisie": "soccer_netherlands_eredivisie",
    "Primeira Liga": "soccer_portugal_primeira_liga",
    "MLS": "soccer_usa_mls",
    "Argentina Primera": "soccer_argentina_primera_division",
    "England Championship": "soccer_england_championship"
}

# =====================================
# FILTERS
# =====================================
st.markdown('<div class="filter-box">', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    modo_scanner = st.selectbox("Modo", ["Liga específica", "Scanner global"])
with f2:
    liga_nome = st.selectbox("Liga", list(LIGAS.keys()))
with f3:
    filtro_hoje = st.checkbox("Mostrar apenas jogos de hoje", value=True)
with f4:
    filtro_finalizadas = st.checkbox("Mostrar apenas apostas finalizadas", value=False)

f5, f6, f7 = st.columns(3)
with f5:
    ev_min = st.number_input("EV mínimo (%)", min_value=-20.0, max_value=100.0, value=1.0, step=0.5)
with f6:
    odd_min = st.number_input("Odd mínima", min_value=1.01, max_value=100.0, value=1.20, step=0.05)
with f7:
    odd_max = st.number_input("Odd máxima", min_value=1.01, max_value=200.0, value=10.00, step=0.10)

st.markdown('</div>', unsafe_allow_html=True)

ligas_escolhidas = [LIGAS[liga_nome]] if modo_scanner == "Liga específica" else list(LIGAS.values())

# =====================================
# API
# =====================================
@st.cache_data(ttl=60)
def buscar_odds_liga(liga_key: str):
    url = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu,uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code != 200:
            return pd.DataFrame(), f"{liga_key}: {r.text}"

        data = r.json()
        if not data:
            return pd.DataFrame(), None

        df = pd.DataFrame(data)
        if not df.empty:
            df["liga_api"] = liga_key
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"{liga_key}: {e}"

@st.cache_data(ttl=60)
def buscar_odds_multiplas(ligas_keys):
    frames = []
    erros = []

    for liga in ligas_keys:
        df, erro = buscar_odds_liga(liga)
        if erro:
            erros.append(erro)
        if not df.empty:
            frames.append(df)

    if frames:
        final = pd.concat(frames, ignore_index=True)
    else:
        final = pd.DataFrame()

    return final, erros

# =====================================
# SCANNER
# =====================================
def extrair_oportunidades(df_raw: pd.DataFrame) -> pd.DataFrame:
    oportunidades = []

    if df_raw.empty or "bookmakers" not in df_raw.columns:
        return pd.DataFrame()

    for _, row in df_raw.iterrows():
        home_team = row.get("home_team")
        away_team = row.get("away_team")
        commence = row.get("commence_time")
        sport_key = row.get("sport_key", row.get("liga_api", ""))

        bookmakers = row.get("bookmakers", [])
        if not bookmakers:
            continue

        best_odds = {}
        odds_list = {}
        best_book = {}

        for book in bookmakers:
            book_title = book.get("title", "Book")
            for market in book.get("markets", []):
                if market.get("key") != "h2h":
                    continue

                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    name = outcome.get("name")
                    price = outcome.get("price")

                    if not name or not isinstance(price, (int, float)) or price <= 1:
                        continue

                    odds_list.setdefault(name, []).append(float(price))

                    if name not in best_odds or float(price) > best_odds[name]:
                        best_odds[name] = float(price)
                        best_book[name] = book_title

        if not best_odds:
            continue

        home_exp, away_exp = estimate_goal_expectancy(home_team, away_team)
        probs_poisson = poisson_1x2(home_exp, away_exp)

        for selection, best_odd in best_odds.items():
            medias = odds_list.get(selection, [best_odd])
            odd_media = sum(medias) / len(medias)

            fair_prob_market = implied_prob_from_odd(odd_media)

            out_key = outcome_key_for_selection(selection, home_team, away_team)
            fair_prob_poisson = probs_poisson.get(out_key, fair_prob_market) if out_key else fair_prob_market

            fair_prob = (fair_prob_market * 0.55) + (fair_prob_poisson * 0.45)
            fair_prob_percent = round(fair_prob * 100, 2)

            ev = (fair_prob * best_odd) - 1
            ev_percent = round(ev * 100, 2)

            if best_odd < odd_min or best_odd > odd_max:
                continue

            if ev_percent < ev_min:
                continue

            kelly_frac = kelly_fraction(fair_prob, best_odd)
            kelly_pct = round(kelly_frac * 100, 2)
            stake_pct = kelly_pct if kelly_pct > 0 else 0.25
            stake_pct = min(max(stake_pct, 0.25), 5.00)
            stake_valor = round(BANKROLL_INICIAL * (stake_pct / 100), 2)

            score = botano_score(
                ev_percent=ev_percent,
                fair_prob_percent=fair_prob_percent,
                best_odd=best_odd,
                clv_percent=0.0
            )

            oportunidades.append({
                "liga_api": sport_key,
                "evento": f"{home_team} x {away_team}",
                "home_team": home_team,
                "away_team": away_team,
                "selecao": selection,
                "odd": round(best_odd, 2),
                "odd_media": round(odd_media, 2),
                "ev": ev_percent,
                "fair_prob": fair_prob_percent,
                "stake_pct": round(stake_pct, 2),
                "stake_valor": stake_valor,
                "casa": best_book.get(selection, "N/D"),
                "commence": commence,
                "score_botano": score,
                "kelly_pct": round(kelly_pct, 2),
                "poisson_home": round(probs_poisson["home"] * 100, 2),
                "poisson_draw": round(probs_poisson["draw"] * 100, 2),
                "poisson_away": round(probs_poisson["away"] * 100, 2),
            })

    df = pd.DataFrame(oportunidades)
    if df.empty:
        return df

    df = df.sort_values(
        by=["score_botano", "ev", "fair_prob"],
        ascending=False
    ).reset_index(drop=True)

    return df

# =====================================
# DATA LOAD
# =====================================
df_odds, erros_api = buscar_odds_multiplas(tuple(ligas_escolhidas))
df_op = extrair_oportunidades(df_odds)

if filtro_hoje and not df_op.empty:
    hoje = datetime.now(timezone.utc).date()
    df_op = df_op[df_op["commence"].apply(lambda x: parse_dt_utc(x).date() == hoje if parse_dt_utc(x) else False)]

# =====================================
# HISTÓRICO
# =====================================
def carregar_historico():
    try:
        hist = supabase.table("apostas_simuladas").select("*").order("created_at", desc=False).execute()
        df = pd.DataFrame(hist.data)
        if df.empty:
            return pd.DataFrame(columns=[
                "id", "created_at", "evento", "selecao", "odd", "stake", "ev",
                "casa", "resultado", "liga_api", "closing_odd", "clv_percent",
                "score_botano", "fair_prob", "kelly_pct", "commence"
            ])
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "id", "created_at", "evento", "selecao", "odd", "stake", "ev",
            "casa", "resultado", "liga_api", "closing_odd", "clv_percent",
            "score_botano", "fair_prob", "kelly_pct", "commence"
        ])

df_hist = carregar_historico()

# =====================================
# METRICS
# =====================================
def calcular_metricas(df_hist_local: pd.DataFrame):
    bankroll = BANKROLL_INICIAL
    lucro_total = 0.0
    greens = 0
    reds = 0

    if df_hist_local.empty:
        return bankroll, lucro_total, 0.0, 0.0, 0, 0, 0

    for _, r in df_hist_local.iterrows():
        stake = safe_float(r.get("stake", 0), 0)
        odd = safe_float(r.get("odd", 1), 1)
        resultado = normalize_result(r.get("resultado", "pendente"))

        if resultado == "green":
            lucro = stake * (odd - 1)
            bankroll += lucro
            lucro_total += lucro
            greens += 1

        elif resultado == "red":
            bankroll -= stake
            lucro_total -= stake
            reds += 1

    finalizadas = greens + reds
    roi = (lucro_total / BANKROLL_INICIAL * 100) if BANKROLL_INICIAL > 0 else 0.0
    winrate = (greens / finalizadas * 100) if finalizadas > 0 else 0.0

    return bankroll, lucro_total, roi, winrate, greens, reds, finalizadas

saldo_atual, lucro_total, roi, winrate, greens, reds, finalizadas = calcular_metricas(df_hist)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Saldo Atual</div><div class="metric-value">{brl(saldo_atual)}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Lucro Total</div><div class="metric-value">{brl(lucro_total)}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">ROI</div><div class="metric-value">{pct(roi)}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Winrate</div><div class="metric-value">{pct(winrate)}</div></div>', unsafe_allow_html=True)

# =====================================
# RANKING - NOVO LAYOUT
# =====================================
st.markdown('<div class="section-title">🌍 Ranking das Melhores Apostas do Mundo</div>', unsafe_allow_html=True)

if df_op.empty:
    st.info("Nenhuma oportunidade encontrada")
else:
    top_rank = df_op.head(10).copy()

    r1, r2 = st.columns(2)
    left_items = top_rank.iloc[::2]
    right_items = top_rank.iloc[1::2]

    with r1:
        for idx, row in left_items.iterrows():
            st.markdown(f"""
            <div class="rank-card">
                <div class="rank-top">
                    <div class="rank-event">{row['evento']}</div>
                    <div class="rank-badge">#{idx+1}</div>
                </div>
                <div class="rank-grid">
                    <div class="rank-item">
                        <div class="rank-label">Seleção</div>
                        <div class="rank-value">{row['selecao']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Casa</div>
                        <div class="rank-value">{row['casa']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Odd</div>
                        <div class="rank-value">{row['odd']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">EV</div>
                        <div class="rank-value ev">{row['ev']}%</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Score BOTANO</div>
                        <div class="rank-value good">{row['score_botano']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Stake</div>
                        <div class="rank-value">{row['stake_pct']}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with r2:
        for idx, row in right_items.iterrows():
            st.markdown(f"""
            <div class="rank-card">
                <div class="rank-top">
                    <div class="rank-event">{row['evento']}</div>
                    <div class="rank-badge">#{idx+1}</div>
                </div>
                <div class="rank-grid">
                    <div class="rank-item">
                        <div class="rank-label">Seleção</div>
                        <div class="rank-value">{row['selecao']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Casa</div>
                        <div class="rank-value">{row['casa']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Odd</div>
                        <div class="rank-value">{row['odd']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">EV</div>
                        <div class="rank-value ev">{row['ev']}%</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Score BOTANO</div>
                        <div class="rank-value good">{row['score_botano']}</div>
                    </div>
                    <div class="rank-item">
                        <div class="rank-label">Stake</div>
                        <div class="rank-value">{row['stake_pct']}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =====================================
# OPORTUNIDADES
# =====================================
st.markdown('<div class="section-title">🔥 Oportunidades de Valor</div>', unsafe_allow_html=True)

if erros_api:
    with st.expander("Avisos da API"):
        for e in erros_api:
            st.write(e)

if df_op.empty:
    st.info("Nenhuma oportunidade encontrada")
else:
    for i, row in df_op.head(25).iterrows():
        st.markdown(f"""
        <div class="botano-card">
            <div class="botano-title">{row['evento']}</div>
            <div class="botano-sub"><b>Liga:</b> {row['liga_api']}</div>
            <div class="botano-sub"><b>Início:</b> {fmt_dt_br(row['commence'])}</div>
            <div class="botano-sub"><b>Entrada:</b> {row['selecao']}</div>
            <div class="botano-sub"><b>Casa:</b> {row['casa']}</div>
            <div class="botano-sub"><b>Melhor odd:</b> {row['odd']} | <b>Média:</b> {row['odd_media']}</div>
            <div class="botano-sub"><b>EV:</b> <span class="ev">{row['ev']}%</span> | <b>Score BOTANO:</b> <span class="good">{row['score_botano']}</span></div>
            <div class="botano-sub"><b>Prob. justa:</b> {row['fair_prob']}% | <b>Kelly:</b> {row['kelly_pct']}%</div>
            <div class="botano-sub"><b>Stake sugerida:</b> <span class="good">{row['stake_pct']}% ({brl(row['stake_valor'])})</span></div>
            <div class="botano-sub"><b>Poisson 1x2:</b> Casa {row['poisson_home']}% | Empate {row['poisson_draw']}% | Fora {row['poisson_away']}%</div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button(f"APOSTAR #{i+1}", key=f"apostar_{i}"):
                payload = {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "evento": row["evento"],
                    "selecao": row["selecao"],
                    "odd": float(row["odd"]),
                    "stake": float(row["stake_valor"]),
                    "ev": float(row["ev"]),
                    "casa": row["casa"],
                    "resultado": "pendente",
                    "liga_api": row["liga_api"],
                    "closing_odd": float(row["odd"]),
                    "clv_percent": 0.0,
                    "score_botano": float(row["score_botano"]),
                    "fair_prob": float(row["fair_prob"]),
                    "kelly_pct": float(row["kelly_pct"]),
                    "commence": row["commence"]
                }
                supabase.table("apostas_simuladas").insert(payload).execute()
                st.success("Aposta registrada. Recarregue para ver no histórico.")

        with b2:
            st.link_button(
                f"Abrir casa: {row['casa']}",
                f"https://www.google.com/search?q={row['casa']} apostas"
            )

# =====================================
# MAPA CLV
# =====================================
def construir_mapa_closing_odds(df_oportunidades: pd.DataFrame):
    mapa = {}
    if df_oportunidades.empty:
        return mapa

    for _, r in df_oportunidades.iterrows():
        chave = (r["evento"], r["selecao"])
        mapa[chave] = {
            "closing_odd": safe_float(r["odd"], 0),
            "score_botano": safe_float(r["score_botano"], 0),
            "fair_prob": safe_float(r["fair_prob"], 0),
            "kelly_pct": safe_float(r["kelly_pct"], 0)
        }
    return mapa

mapa_closing = construir_mapa_closing_odds(df_op)

# =====================================
# HISTÓRICO
# =====================================
st.markdown('<div class="section-title">📊 Histórico de Apostas</div>', unsafe_allow_html=True)

df_hist_view = df_hist.copy()

if filtro_finalizadas and not df_hist_view.empty:
    if "resultado" in df_hist_view.columns:
        df_hist_view = df_hist_view[df_hist_view["resultado"].fillna("pendente") != "pendente"]

if df_hist_view.empty:
    st.info("Sem apostas registradas")
else:
    for i, row in df_hist_view.iterrows():
        evento = row.get("evento", "-")
        selecao = row.get("selecao", "-")
        odd_entrada = safe_float(row.get("odd", 1), 1)
        stake = safe_float(row.get("stake", 0), 0)
        resultado_atual = normalize_result(row.get("resultado", "pendente"))

        closing_atual = safe_float(row.get("closing_odd", odd_entrada), odd_entrada)
        score_atual = safe_float(row.get("score_botano", 0), 0)
        fair_prob_atual = safe_float(row.get("fair_prob", 0), 0)
        kelly_atual = safe_float(row.get("kelly_pct", 0), 0)

        chave = (evento, selecao)
        if chave in mapa_closing:
            closing_atual = mapa_closing[chave]["closing_odd"]
            score_atual = mapa_closing[chave]["score_botano"]
            fair_prob_atual = mapa_closing[chave]["fair_prob"]
            kelly_atual = mapa_closing[chave]["kelly_pct"]

        clv_atual = clv_percent(odd_entrada, closing_atual)

        c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
        c1.write(f"**{evento}**")
        c1.write(f"Seleção: {selecao}")
        c2.write(f"Odd {odd_entrada}")
        c2.write(f"CLV {clv_atual}%")
        c3.write(f"Stake {brl(stake)}")
        c3.write(f"Score {score_atual}")
        novo_resultado = c4.selectbox(
            "Resultado",
            ["pendente", "green", "red"],
            index=["pendente", "green", "red"].index(resultado_atual),
            key=f"res_{i}"
        )

        s1, s2 = st.columns([1, 1])
        with s1:
            if st.button("Salvar resultado", key=f"save_{i}"):
                payload_update = {
                    "resultado": novo_resultado,
                    "closing_odd": closing_atual,
                    "clv_percent": clv_atual,
                    "score_botano": score_atual,
                    "fair_prob": fair_prob_atual,
                    "kelly_pct": kelly_atual
                }
                supabase.table("apostas_simuladas").update(payload_update).eq("id", row["id"]).execute()
                st.success("Atualizado. Recarregue para refletir nas métricas.")

        with s2:
            st.write(f"Casa: {row.get('casa','-')}")
            st.write(f"Prob justa: {fair_prob_atual}%")

        st.divider()

# =====================================
# RESUMO
# =====================================
st.markdown('<div class="section-title">🏆 Resumo Profissional</div>', unsafe_allow_html=True)

avg_clv = 0.0
if not df_hist.empty and "clv_percent" in df_hist.columns:
    serie_clv = pd.to_numeric(df_hist["clv_percent"], errors="coerce").fillna(0)
    avg_clv = float(serie_clv.mean()) if len(serie_clv) > 0 else 0.0

avg_ev = 0.0
if not df_hist.empty and "ev" in df_hist.columns:
    serie_ev = pd.to_numeric(df_hist["ev"], errors="coerce").fillna(0)
    avg_ev = float(serie_ev.mean()) if len(serie_ev) > 0 else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Apostas finalizadas", finalizadas)
k2.metric("Greens", greens)
k3.metric("Reds", reds)
k4.metric("CLV médio", pct(avg_clv))

k5, k6 = st.columns(2)
k5.metric("EV médio das apostas", pct(avg_ev))
k6.metric("Banca inicial", brl(BANKROLL_INICIAL))

# =====================================
# EVOLUÇÃO BANCA
# =====================================
st.markdown('<div class="section-title">📈 Evolução da Banca</div>', unsafe_allow_html=True)

def serie_banca(df_hist_local: pd.DataFrame):
    saldo = BANKROLL_INICIAL
    rows = [{"ordem": 0, "banca": saldo, "label": "Inicial"}]

    if df_hist_local.empty:
        return pd.DataFrame(rows)

    df_sorted = df_hist_local.copy()
    if "created_at" in df_sorted.columns:
        df_sorted["created_at_dt"] = pd.to_datetime(df_sorted["created_at"], errors="coerce")
        df_sorted = df_sorted.sort_values("created_at_dt")

    ordem = 1
    for _, r in df_sorted.iterrows():
        stake = safe_float(r.get("stake", 0), 0)
        odd = safe_float(r.get("odd", 1), 1)
        resultado = normalize_result(r.get("resultado", "pendente"))

        if resultado == "green":
            saldo += stake * (odd - 1)
        elif resultado == "red":
            saldo -= stake

        rows.append({
            "ordem": ordem,
            "banca": round(saldo, 2),
            "label": r.get("evento", f"Aposta {ordem}")
        })
        ordem += 1

    return pd.DataFrame(rows)

df_chart = serie_banca(df_hist)

chart = alt.Chart(df_chart).mark_line(point=True).encode(
    x=alt.X("ordem:Q", title="Sequência de apostas"),
    y=alt.Y("banca:Q", title="Banca"),
    tooltip=["label", "banca"]
).properties(height=320)

st.altair_chart(chart, use_container_width=True)

# =====================================
# DEBUG
# =====================================
with st.expander("🛠 Debug API"):
    st.write("Modo scanner:", modo_scanner)
    st.write("Ligas consultadas:", ligas_escolhidas)
    st.write("Qtd jogos retornados:", len(df_odds))
    st.write("Qtd oportunidades:", len(df_op))
    st.write("Erros API:", erros_api if erros_api else "Nenhum")
    if not df_odds.empty:
        st.dataframe(df_odds.head(), use_container_width=True)
