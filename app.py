import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import altair as alt
import pandas as pd
import requests
import streamlit as st
from supabase import create_client


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="BOTANO+ | Value Betting Engine PRO V5",
    layout="wide",
)

API_TIMEOUT = 30
BANKROLL_INICIAL_PADRAO = 1500.0

# ---------------------------------------------------------
# SECRETS / CLIENTS
# ---------------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
ODDS_API_KEY = st.secrets.get("ODDS_API_KEY", "")
BANKROLL_INICIAL = float(
    st.secrets.get("BANKROLL_INICIAL", BANKROLL_INICIAL_PADRAO)
)

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None


# =========================================================
# SESSION STATE
# =========================================================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "painel"

if "sim_evento" not in st.session_state:
    st.session_state["sim_evento"] = ""

if "sim_odd" not in st.session_state:
    st.session_state["sim_odd"] = 2.00

if "sim_valor" not in st.session_state:
    st.session_state["sim_valor"] = 20.0

if "toast_msg" not in st.session_state:
    st.session_state["toast_msg"] = ""


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
.stApp{
    background: linear-gradient(180deg, #090909 0%, #111111 100%);
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

hr {
    border-color: #262626 !important;
}

/* ===== labels ===== */
.stSelectbox label,
.stCheckbox label,
.stNumberInput label,
.stTextInput label {
    color: white !important;
    font-weight: 700 !important;
}

/* ===== inputs ===== */
div[data-baseweb="select"] > div {
    background: #1b1b1b !important;
    border: 1px solid #333 !important;
    color: white !important;
}

div[data-baseweb="select"] span {
    color: white !important;
}

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

div[data-baseweb="input"] > div {
    background: #1b1b1b !important;
    color: white !important;
    border: 1px solid #333 !important;
}

input {
    color: white !important;
    -webkit-text-fill-color: white !important;
    background: transparent !important;
}

input[type="checkbox"] {
    accent-color: #ff6a00;
}

/* ===== buttons ===== */
div.stButton > button {
    background: linear-gradient(135deg, #ff5a2a 0%, #ff7a1a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 48px !important;
    width: 100% !important;
    white-space: normal !important;
}

div.stButton > button:hover {
    color: white !important;
    border: none !important;
    opacity: 0.96;
}

div.stButton > button:focus,
div.stButton > button:active {
    color: white !important;
    border: none !important;
    box-shadow: none !important;
}

/* ===== metrics ===== */
[data-testid="stMetric"] {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 12px;
}

[data-testid="stMetricLabel"] {
    color: #cfcfcf !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 800 !important;
}

/* ===== cards ===== */
.botano-card {
    background: #1e1e1e;
    border: 1px solid #2f2f2f;
    border-left: 4px solid #ff5a2a;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
}

.botano-title {
    color: #ff5a2a;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 10px;
}

.botano-sub {
    color: #d7d7d7 !important;
    font-size: 15px;
    margin-bottom: 12px;
}

.botano-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(160px, 1fr));
    gap: 10px;
    margin-top: 12px;
}

.botano-item {
    background: #151515;
    border: 1px solid #2b2b2b;
    border-radius: 12px;
    padding: 10px 12px;
}

.botano-item-label {
    color: #a9a9a9 !important;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 4px;
}

.botano-item-value {
    color: white !important;
    font-size: 18px;
    font-weight: 800;
}

.botano-panel {
    background: #141414;
    border: 1px solid #2b2b2b;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
}

.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    margin-right: 8px;
    margin-bottom: 8px;
}

.badge-market {
    background: #211816;
    border: 1px solid #ff5a2a;
    color: #ffb38a !important;
}

.badge-ev {
    background: #2b1a12;
    border: 1px solid #ff7a1a;
    color: #ffb38a !important;
}

.badge-score {
    background: #171f15;
    border: 1px solid #4caf50;
    color: #b9f2c1 !important;
}

.badge-risk-low {
    background: #152018;
    border: 1px solid #45c96b;
    color: #b9f2c1 !important;
}

.badge-risk-medium {
    background: #2a2312;
    border: 1px solid #ffc107;
    color: #ffe59b !important;
}

.badge-risk-high {
    background: #2b1616;
    border: 1px solid #ff5252;
    color: #ffb4b4 !important;
}

.gloss-card {
    background: #181818;
    border: 1px solid #2c2c2c;
    border-left: 4px solid #ff5a2a;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
}

.gloss-title {
    color: #ff5a2a;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}

.gloss-text {
    color: white !important;
    font-size: 16px;
    line-height: 1.7;
}

.small-muted {
    color: #b5b5b5 !important;
    font-size: 12px;
}

.tripla-box {
    background: linear-gradient(180deg, #171717 0%, #111111 100%);
    border: 1px solid #343434;
    border-left: 4px solid #ff5a2a;
    border-radius: 18px;
    padding: 18px;
}

.kpi-chip {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    margin-right: 8px;
    margin-bottom: 8px;
    background: #171717;
    border: 1px solid #333;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# NAVEGAÇÃO
# =========================================================
def abrir_glossario() -> None:
    st.session_state["pagina"] = "glossario"


def voltar_painel() -> None:
    st.session_state["pagina"] = "painel"


# =========================================================
# HELPERS DE RISCO / SCORE
# =========================================================
def score_botano(ev_percent: float, fair_prob_percent: float, odd: float) -> float:
    return round((ev_percent * 8.0) + (fair_prob_percent * 0.30) - (odd * 1.20), 2)


def classificar_risco(odd: float, fair_prob_percent: float, ev_percent: float) -> Tuple[str, str]:
    if odd >= 4.50 or fair_prob_percent < 28:
        return "Risco Elevado", "badge-risk-high"
    if odd >= 2.60 or fair_prob_percent < 45 or ev_percent < 2.2:
        return "Risco Moderado", "badge-risk-medium"
    return "Risco Controlado", "badge-risk-low"


def nivel_oportunidade(score: float) -> str:
    if score >= 110:
        return "Premium"
    if score >= 80:
        return "Boa"
    if score >= 55:
        return "Agressiva"
    return "Observação"


def hoje_filter(data_str: str) -> bool:
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return dt.date() == datetime.utcnow().date()
    except Exception:
        return False


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def hash_grupo_multipla(itens: List[Dict]) -> str:
    base = "|".join([f"{i['evento']}::{i['mercado']}::{i['selecao']}" for i in itens])
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:12]


# =========================================================
# MERCADOS
# =========================================================
LIGAS: Dict[str, str] = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl",
    "Champions League": "soccer_uefa_champs_league",
    "La Liga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga",
}

# Mapeamento preparado para processar o que vier da API.
# h2h / totals / btts são documentados publicamente; corners/cards são tentados de forma resiliente.
MARKET_PRIORITY = [
    "h2h",
    "totals",
    "btts",
    "team_totals",
    "alternate_totals",
    "corners",
    "alternate_corners",
    "cards",
    "alternate_cards",
]

MARKET_LABELS = {
    "h2h": "1x2",
    "totals": "Gols",
    "alternate_totals": "Gols",
    "btts": "BTTS",
    "corners": "Cantos",
    "alternate_corners": "Cantos",
    "cards": "Cartões",
    "alternate_cards": "Cartões",
    "team_totals": "Gols",
}


# =========================================================
# API / SUPABASE
# =========================================================
@st.cache_data(ttl=60)
def buscar_odds(sport_key: str) -> Tuple[pd.DataFrame, Optional[str]]:
    try:
        if not ODDS_API_KEY:
            return pd.DataFrame(), "ODDS_API_KEY não configurada."

        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "eu,uk",
            "markets": ",".join(MARKET_PRIORITY),
            "oddsFormat": "decimal",
            "dateFormat": "iso",
        }

        response = requests.get(url, params=params, timeout=API_TIMEOUT)

        if response.status_code != 200:
            return pd.DataFrame(), f"Erro API Odds: {response.status_code} - {response.text}"

        data = response.json()
        if not data:
            return pd.DataFrame(), "Sem jogos retornados para os mercados consultados."

        return pd.DataFrame(data), None

    except requests.RequestException as exc:
        return pd.DataFrame(), f"Falha de conexão na Odds API: {exc}"
    except Exception as exc:
        return pd.DataFrame(), f"Erro inesperado ao buscar odds: {exc}"


def carregar_historico() -> Tuple[pd.DataFrame, Optional[str]]:
    try:
        if supabase is None:
            return pd.DataFrame(), "Supabase não configurado."

        resposta = supabase.table("apostas_simuladas").select("*").execute()
        df_hist = pd.DataFrame(resposta.data)

        if df_hist.empty:
            df_hist = pd.DataFrame(
                columns=[
                    "id",
                    "created_at",
                    "evento",
                    "liga",
                    "mercado",
                    "linha",
                    "selecao",
                    "odd",
                    "odd_media",
                    "fair_prob",
                    "ev_percent",
                    "score_botano",
                    "valor",
                    "stake",
                    "casa",
                    "status",
                    "resultado",
                    "ticket_tipo",
                    "grupo_id_multipla",
                ]
            )
        return df_hist, None

    except Exception as exc:
        return pd.DataFrame(), f"Erro ao carregar histórico do Supabase: {exc}"


def registrar_aposta(payload: Dict) -> Tuple[bool, str]:
    try:
        if supabase is None:
            return False, "Supabase não configurado."

        supabase.table("apostas_simuladas").insert(payload).execute()
        return True, "Aposta registrada com sucesso."

    except Exception as exc:
        return False, f"Erro ao registrar aposta: {exc}"


def atualizar_resultado(aposta_id: str, resultado: str) -> Tuple[bool, str]:
    try:
        if supabase is None:
            return False, "Supabase não configurado."

        supabase.table("apostas_simuladas").update(
            {"resultado": resultado, "status": resultado}
        ).eq("id", aposta_id).execute()

        return True, "Resultado atualizado."

    except Exception as exc:
        return False, f"Erro ao atualizar resultado: {exc}"


# =========================================================
# PARSING / MOTOR DE OPORTUNIDADES
# =========================================================
def outcome_key(outcome: Dict) -> str:
    name = str(outcome.get("name", ""))
    point = outcome.get("point")
    desc = str(outcome.get("description", ""))
    return f"{name}|{point}|{desc}"


def market_display(market_key: str, outcome: Dict) -> str:
    point = outcome.get("point")
    name = str(outcome.get("name", "")).strip()
    desc = str(outcome.get("description", "")).strip()

    if market_key == "h2h":
        return "Vencedor"
    if market_key in ("totals", "alternate_totals"):
        if point is not None:
            return f"{name} {point} Gols"
        return "Totais de Gols"
    if market_key == "btts":
        return "Ambas Marcam"
    if market_key in ("corners", "alternate_corners"):
        if point is not None:
            return f"{name} {point} Cantos"
        return "Cantos"
    if market_key in ("cards", "alternate_cards"):
        if point is not None:
            return f"{name} {point} Cartões"
        return "Cartões"
    if market_key == "team_totals":
        if desc and point is not None:
            return f"{desc} {name} {point}"
        return "Team Totals"
    return market_key


def selection_display(market_key: str, outcome: Dict) -> str:
    name = str(outcome.get("name", "")).strip()
    point = outcome.get("point")
    desc = str(outcome.get("description", "")).strip()

    if market_key == "h2h":
        return name

    if desc and point is not None:
        return f"{desc} | {name} {point}"

    if point is not None:
        return f"{name} {point}"

    return name


def extrair_oportunidades(df_raw: pd.DataFrame, liga_nome: str) -> pd.DataFrame:
    oportunidades: List[Dict] = []

    if df_raw.empty:
        return pd.DataFrame()

    for _, row in df_raw.iterrows():
        home = row.get("home_team", "")
        away = row.get("away_team", "")
        commence = row.get("commence_time", "")
        bookmakers = row.get("bookmakers", []) or []

        market_accumulator: Dict[str, Dict] = {}

        for book in bookmakers:
            nome_book = book.get("title", "book")
            for market in book.get("markets", []):
                market_key = market.get("key", "")
                if market_key not in MARKET_PRIORITY:
                    continue

                for outcome in market.get("outcomes", []):
                    price = outcome.get("price")
                    if price is None:
                        continue

                    o_key = f"{market_key}::{outcome_key(outcome)}"

                    if o_key not in market_accumulator:
                        market_accumulator[o_key] = {
                            "market_key": market_key,
                            "outcome": outcome,
                            "prices": [],
                            "best_odd": None,
                            "best_book": None,
                        }

                    market_accumulator[o_key]["prices"].append(float(price))

                    if (
                        market_accumulator[o_key]["best_odd"] is None
                        or float(price) > market_accumulator[o_key]["best_odd"]
                    ):
                        market_accumulator[o_key]["best_odd"] = float(price)
                        market_accumulator[o_key]["best_book"] = nome_book

        for _, data in market_accumulator.items():
            prices = data["prices"]
            if not prices:
                continue

            avg_odd = sum(prices) / len(prices)
            best_odd = float(data["best_odd"])
            fair_prob = 1.0 / avg_odd
            fair_prob_percent = round(fair_prob * 100.0, 2)
            ev = (fair_prob * best_odd) - 1.0
            ev_percent = round(ev * 100.0, 2)

            if ev_percent < 1.0:
                continue

            stake_pct = 0.5
            if ev_percent >= 4:
                stake_pct = 1.0
            if ev_percent >= 7:
                stake_pct = 2.0
            if ev_percent >= 10:
                stake_pct = 3.0

            stake_valor = round(BANKROLL_INICIAL * (stake_pct / 100.0), 2)
            score = score_botano(ev_percent, fair_prob_percent, best_odd)
            risco_label, risco_css = classificar_risco(
                odd=best_odd,
                fair_prob_percent=fair_prob_percent,
                ev_percent=ev_percent,
            )

            oportunidades.append(
                {
                    "evento": f"{home} x {away}",
                    "liga": liga_nome,
                    "commence": commence,
                    "mercado_key": data["market_key"],
                    "mercado_tipo": MARKET_LABELS.get(data["market_key"], data["market_key"]),
                    "mercado": market_display(data["market_key"], data["outcome"]),
                    "linha": data["outcome"].get("point"),
                    "selecao": selection_display(data["market_key"], data["outcome"]),
                    "odd": round(best_odd, 2),
                    "odd_media": round(avg_odd, 2),
                    "fair_prob": fair_prob_percent,
                    "ev_percent": ev_percent,
                    "score_botano": score,
                    "stake_pct": stake_pct,
                    "stake_valor": stake_valor,
                    "casa": data["best_book"],
                    "risco_label": risco_label,
                    "risco_css": risco_css,
                    "nivel": nivel_oportunidade(score),
                }
            )

    df_op = pd.DataFrame(oportunidades)
    if df_op.empty:
        return df_op

    return df_op.sort_values(
        by=["score_botano", "ev_percent", "fair_prob"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


# =========================================================
# TRIPLA DO DIA
# =========================================================
def gerar_tripla_do_dia(df_op: pd.DataFrame) -> List[Dict]:
    if df_op.empty:
        return []

    selecionadas: List[Dict] = []
    eventos_usados = set()

    for _, row in df_op.sort_values(
        by=["score_botano", "fair_prob", "ev_percent"],
        ascending=[False, False, False],
    ).iterrows():
        evento = row["evento"]
        if evento in eventos_usados:
            continue

        selecionadas.append(row.to_dict())
        eventos_usados.add(evento)

        if len(selecionadas) == 3:
            break

    return selecionadas


# =========================================================
# GLOSSÁRIO
# =========================================================
def render_glossario() -> None:
    top1, top2 = st.columns([6, 2])

    with top1:
        st.markdown("<h1>📘 Glossário do BOTANO+</h1>", unsafe_allow_html=True)

    with top2:
        st.write("")
        st.button("⬅ Voltar ao painel principal", on_click=voltar_painel)

    cards = [
        (
            "Odd",
            "É o número que mostra quanto a aposta paga. Odd 2.00 significa dobrar o valor apostado se acertar."
        ),
        (
            "Fair Probability",
            "É a chance justa estimada com base no consenso do mercado. Quanto maior, mais provável o evento parece."
        ),
        (
            "EV",
            "É o valor esperado. EV positivo indica que a odd oferecida parece melhor do que a chance justa estimada."
        ),
        (
            "Score BOTANO",
            "É a nota da oportunidade, combinando EV, probabilidade justa e penalização por odd excessiva."
        ),
        (
            "Risco",
            "É a leitura de variância da entrada. Odds altas ou probabilidade justa baixa elevam o risco."
        ),
        (
            "BTTS",
            "Ambas as equipes marcam. Normalmente 'Yes' ou 'No'."
        ),
        (
            "Tripla do Dia",
            "Uma múltipla sugerida automaticamente com três oportunidades fortes, evitando repetir o mesmo jogo."
        ),
    ]

    for titulo, texto in cards:
        st.markdown(
            f"""
            <div class="gloss-card">
                <div class="gloss-title">{titulo}</div>
                <div class="gloss-text">{texto}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if st.session_state["pagina"] == "glossario":
    render_glossario()
    st.stop()


# =========================================================
# HEADER
# =========================================================
h1, h2 = st.columns([7, 2])

with h1:
    st.markdown(
        """
        <h1>⚡ BOTANO+ <span style='font-size:18px;color:white;font-weight:400'>
        Trading Intelligence Engine V5
        </span></h1>
        """,
        unsafe_allow_html=True,
    )

with h2:
    st.write("")
    st.button("📘 Abrir Glossário", on_click=abrir_glossario)


# =========================================================
# FILTROS
# =========================================================
f1, f2, f3 = st.columns(3)

with f1:
    liga_nome = st.selectbox("Liga", list(LIGAS.keys()))

with f2:
    filtro_hoje = st.checkbox("Mostrar apenas jogos de hoje", value=True)

with f3:
    filtro_finalizadas = st.checkbox("Mostrar apenas apostas finalizadas", value=False)

liga_api = LIGAS[liga_nome]


# =========================================================
# DADOS PRINCIPAIS
# =========================================================
df_odds, erro_odds = buscar_odds(liga_api)
df_op = extrair_oportunidades(df_odds, liga_nome)

if filtro_hoje and not df_op.empty:
    df_op = df_op[df_op["commence"].apply(hoje_filter)].reset_index(drop=True)

df_hist, erro_hist = carregar_historico()


# =========================================================
# KPI HISTÓRICO
# =========================================================
bankroll = BANKROLL_INICIAL
lucro_total = 0.0
greens = 0
reds = 0

if not df_hist.empty:
    for _, r in df_hist.iterrows():
        stake = float(r.get("valor", r.get("stake", 0)) or 0)
        odd = float(r.get("odd", 1) or 1)
        resultado = str(r.get("resultado", "pendente"))

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
roi_real = (lucro_total / BANKROLL_INICIAL) * 100 if total_apostas > 0 else 0.0
winrate_real = (greens / total_apostas) * 100 if total_apostas > 0 else 0.0


# =========================================================
# LAYOUT PRINCIPAL
# =========================================================
left_col, right_col = st.columns([1.55, 1.0], gap="large")

# ---------------------------------------------------------
# ESQUERDA: FEED DE OPORTUNIDADES
# ---------------------------------------------------------
with left_col:
    st.subheader("🔥 Feed de Oportunidades de Valor")

    if erro_odds:
        st.error(erro_odds)

    if df_op.empty and not erro_odds:
        st.info("Nenhuma oportunidade de valor encontrada com os filtros atuais.")

    for i, row in df_op.head(20).iterrows():
        st.markdown(
            f"""
            <div class="botano-card">
                <div class="botano-title">{row['evento']}</div>
                <div class="botano-sub">
                    Mercado: <b>{row['mercado']}</b> |
                    Seleção: <b>{row['selecao']}</b> |
                    Casa: <b>{row['casa']}</b>
                </div>

                <span class="badge badge-market">{row['mercado_tipo']}</span>
                <span class="badge badge-ev">EV {row['ev_percent']}%</span>
                <span class="badge badge-score">Score {row['score_botano']}</span>
                <span class="badge {row['risco_css']}">{row['risco_label']}</span>

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
                        <div class="botano-item-value">{formatar_moeda(row['stake_valor'])}</div>
                    </div>
                </div>

                <div style="margin-top:12px" class="small-muted">
                    Nível: {row['nivel']} | Liga: {row['liga']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        label_botao = f"Apostar no simulador: {row['mercado']} em {row['evento']}"
        if st.button(label_botao, key=f"bet_{i}"):
            payload = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "evento": row["evento"],
                "liga": row["liga"],
                "mercado": row["mercado"],
                "linha": row["linha"],
                "selecao": row["selecao"],
                "odd": float(row["odd"]),
                "odd_media": float(row["odd_media"]),
                "fair_prob": float(row["fair_prob"]),
                "ev_percent": float(row["ev_percent"]),
                "score_botano": float(row["score_botano"]),
                "valor": float(row["stake_valor"]),
                "stake": float(row["stake_valor"]),
                "casa": row["casa"],
                "status": "pendente",
                "resultado": "pendente",
                "ticket_tipo": "single",
                "grupo_id_multipla": None,
            }
            ok, msg = registrar_aposta(payload)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


# ---------------------------------------------------------
# DIREITA: GESTÃO + TRIPLA + HISTÓRICO
# ---------------------------------------------------------
with right_col:
    st.subheader("📊 Painel de Gestão")

    p1, p2 = st.columns(2)
    p3, p4 = st.columns(2)

    with p1:
        st.metric("Banca Atual", formatar_moeda(bankroll))
    with p2:
        st.metric("Lucro Total", formatar_moeda(lucro_total))
    with p3:
        st.metric("ROI Real", f"{round(roi_real, 2)}%")
    with p4:
        st.metric("Win Rate", f"{round(winrate_real, 1)}%")

    st.markdown("---")

    st.markdown("### 🎯 Simulador de Gestão")

    sim_evento = st.text_input("Evento", value=st.session_state["sim_evento"])
    sim_odd = st.number_input(
        "Odd",
        min_value=1.01,
        value=float(st.session_state["sim_odd"]),
        step=0.01,
    )
    sim_valor = st.number_input(
        "Valor (R$)",
        min_value=1.0,
        value=float(st.session_state["sim_valor"]),
        step=1.0,
    )

    st.session_state["sim_evento"] = sim_evento
    st.session_state["sim_odd"] = sim_odd
    st.session_state["sim_valor"] = sim_valor

    lucro_potencial = round(sim_valor * (sim_odd - 1), 2)
    retorno_total = round(sim_valor * sim_odd, 2)

    s1, s2 = st.columns(2)
    s1.metric("Lucro Potencial", formatar_moeda(lucro_potencial))
    s2.metric("Retorno Total", formatar_moeda(retorno_total))

    st.markdown("---")

    st.markdown("### 🛡️ Sugestão de Múltipla")
    tripla = gerar_tripla_do_dia(df_op)

    if len(tripla) < 3:
        st.info("Ainda não há 3 oportunidades elegíveis para montar a Tripla do Dia.")
    else:
        odd_combinada = 1.0
        ev_medio = 0.0
        score_medio = 0.0
        for item in tripla:
            odd_combinada *= float(item["odd"])
            ev_medio += float(item["ev_percent"])
            score_medio += float(item["score_botano"])

        ev_medio = round(ev_medio / 3.0, 2)
        score_medio = round(score_medio / 3.0, 2)
        grupo_id = hash_grupo_multipla(tripla)

        st.markdown('<div class="tripla-box">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="margin-bottom:10px">
                <span class="kpi-chip">Odd combinada {round(odd_combinada, 2)}</span>
                <span class="kpi-chip">EV médio {ev_medio}%</span>
                <span class="kpi-chip">Score médio {score_medio}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, item in enumerate(tripla, start=1):
            st.markdown(
                f"""
                <div style="margin-bottom:10px">
                    <b>{idx}. {item['evento']}</b><br>
                    <span class="small-muted">{item['mercado']} | {item['selecao']} | odd {item['odd']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Registrar Tripla do Dia no simulador"):
            falhas = []
            for item in tripla:
                payload = {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "evento": item["evento"],
                    "liga": item["liga"],
                    "mercado": item["mercado"],
                    "linha": item["linha"],
                    "selecao": item["selecao"],
                    "odd": float(item["odd"]),
                    "odd_media": float(item["odd_media"]),
                    "fair_prob": float(item["fair_prob"]),
                    "ev_percent": float(item["ev_percent"]),
                    "score_botano": float(item["score_botano"]),
                    "valor": float(item["stake_valor"]),
                    "stake": float(item["stake_valor"]),
                    "casa": item["casa"],
                    "status": "pendente",
                    "resultado": "pendente",
                    "ticket_tipo": "multipla",
                    "grupo_id_multipla": grupo_id,
                }
                ok, msg = registrar_aposta(payload)
                if not ok:
                    falhas.append(msg)

            if falhas:
                st.error("Parte da múltipla falhou no registro.")
                for falha in falhas:
                    st.write(f"- {falha}")
            else:
                st.success("Tripla do Dia registrada no histórico.")
                st.rerun()

    st.markdown("---")

    st.markdown("### 📚 Histórico de Apostas")

    if erro_hist:
        st.error(erro_hist)

    df_hist_view = df_hist.copy()
    if filtro_finalizadas and not df_hist_view.empty:
        df_hist_view = df_hist_view[df_hist_view["resultado"] != "pendente"]

    if df_hist_view.empty:
        st.info("Sem apostas registradas.")
    else:
        for i, row in df_hist_view.iterrows():
            st.markdown(
                f"""
                <div class="botano-panel">
                    <b>{row.get('evento', '')}</b><br>
                    <span class="small-muted">
                        {row.get('mercado', '')} | {row.get('selecao', '')}
                    </span><br><br>
                    Odd: <b>{row.get('odd', 1)}</b> |
                    Valor: <b>{formatar_moeda(float(row.get('valor', row.get('stake', 0)) or 0))}</b> |
                    Status: <b>{row.get('resultado', 'pendente')}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            opcoes = ["pendente", "green", "red"]
            resultado_atual = str(row.get("resultado", "pendente"))
            idx_default = opcoes.index(resultado_atual) if resultado_atual in opcoes else 0

            novo_resultado = st.selectbox(
                "Resultado",
                opcoes,
                index=idx_default,
                key=f"hist_res_{i}",
            )

            if st.button("Salvar resultado", key=f"save_hist_{i}"):
                aposta_id = row.get("id")
                if not aposta_id:
                    st.error("ID da aposta ausente; não foi possível atualizar.")
                else:
                    ok, msg = atualizar_resultado(aposta_id, novo_resultado)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")

    st.markdown("### 📈 Evolução da Banca")

    saldo = BANKROLL_INICIAL
    historia = [saldo]

    if not df_hist.empty:
        for _, r in df_hist.iterrows():
            stake = float(r.get("valor", r.get("stake", 0)) or 0)
            odd = float(r.get("odd", 1) or 1)
            resultado = str(r.get("resultado", "pendente"))

            if resultado == "green":
                saldo += stake * (odd - 1)

            if resultado == "red":
                saldo -= stake

            historia.append(round(saldo, 2))

    df_chart = pd.DataFrame(
        {
            "aposta": list(range(len(historia))),
            "banca": historia,
        }
    )

    chart = alt.Chart(df_chart).mark_line(point=True).encode(
        x=alt.X("aposta:Q", title="Apostas"),
        y=alt.Y("banca:Q", title="Banca"),
    ).properties(height=320)

    st.altair_chart(chart, use_container_width=True)


# =========================================================
# DEBUG
# =========================================================
with st.expander("Debug técnico"):
    st.write("Liga:", liga_api)
    st.write("Erro Odds:", erro_odds)
    st.write("Erro Histórico:", erro_hist)
    st.write("Jogos retornados:", len(df_odds))
    st.write("Oportunidades:", 0 if df_op.empty else len(df_op))
    if not df_odds.empty:
        st.dataframe(df_odds.head())
