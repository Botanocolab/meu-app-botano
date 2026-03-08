import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
from supabase import Client, create_client

league_map = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Brasileirão Série B": "soccer_brazil_serie_b",
    "Copa do Brasil": "soccer_brazil_copa_do_brasil",
    "Libertadores": "soccer_conmebol_libertadores"
}

AUTO_REGION = "eu"

AUTO_LEAGUES = [
    "Brasileirão Série A",
    "Brasileirão Série B",
    "Copa do Brasil",
    "Libertadores"
]

AUTO_MARKETS = ["h2h", "totals_corners", "totals_cards"]

BANKROLL_INICIAL = 1500.0
AUTO_MIN_EV = 0.3
AUTO_SCORE_MIN = 5

# ==============================
# BOOKMAKERS
# ==============================

BOOKMAKER_URLS = {
    "bet365": "https://www.bet365.com",
    "betfair": "https://www.betfair.com",
    "pinnacle": "https://www.pinnacle.com",
    "bwin": "https://sports.bwin.com",
    "williamhill": "https://sports.williamhill.com",
    "betway": "https://betway.com",
    "unibet": "https://www.unibet.com",
    "1xbet": "https://1xbet.com",
    "10bet": "https://www.10bet.com",
    "marathonbet": "https://www.marathonbet.com",
}

st.markdown("""
<style>

/* ===== SELECTBOX ===== */
div[data-baseweb="select"] > div {
    background-color: #1e1e1e !important;
    color: white !important;
    border: 1px solid #444 !important;
}

/* texto dentro do select */
div[data-baseweb="select"] span {
    color: white !important;
}

/* ===== MENU DROPDOWN ===== */
ul[role="listbox"] {
    background-color: #1e1e1e !important;
    color: white !important;
}

/* opções do dropdown */
li[role="option"] {
    background-color: #1e1e1e !important;
    color: white !important;
}

/* hover nas opções */
li[role="option"]:hover {
    background-color: #333 !important;
}

/* ===== MULTISELECT TAGS ===== */
span[data-baseweb="tag"] {
    background-color: #ff6b00 !important;
    color: white !important;
}

/* ===== INPUTS ===== */
input, textarea {
    background-color: #1e1e1e !important;
    color: white !important;
}

/* ===== LABELS ===== */
label {
    color: #dddddd !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# THEME
# ============================================================
BG_COLOR = "#0f0f0f"
PANEL_COLOR = "#171717"
CARD_COLOR = "#141414"
BORDER_COLOR = "#262626"
TEXT_COLOR = "#f5f5f5"
MUTED_COLOR = "#b8b8b8"
ACCENT_COLOR = "#ff5a2a"
GREEN_COLOR = "#19c37d"
RED_COLOR = "#ff4d4f"
YELLOW_COLOR = "#ffb020"
BLUE_COLOR = "#4da3ff"
PURPLE_COLOR = "#a855f7"

SPORTS_MAP = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl",
    "Champions League": "soccer_uefa_champs_league",
}

SUPPORTED_MARKETS = [
    "h2h",
    "totals_corners",
    "totals_cards",
]

MARKET_NAMES = {
    "h2h": "Vencedor (1x2)",
    "totals_corners": "Escanteios",
    "totals_cards": "Cartões",
}

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports"


# ============================================================
# CSS
# ============================================================
CUSTOM_CSS = f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {BG_COLOR} 0%, #101010 100%);
        color: {TEXT_COLOR};
    }}

    [data-testid="stSidebar"] {{
        background: #101010;
        border-right: 1px solid {BORDER_COLOR};
    }}

    [data-testid="stHeader"] {{
        background: rgba(15, 15, 15, 0.65);
    }}

    .block-container {{
        max-width: 1600px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: {TEXT_COLOR} !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {{
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #2d2d2d !important;
    }}

    .stButton > button {{
        width: 100%;
        min-height: 44px;
        border-radius: 12px !important;
        border: 1px solid #ff734b !important;
        background: {ACCENT_COLOR} !important;
        color: #ffffff !important;
        font-weight: 800 !important;
    }}

    .stButton > button:hover {{
        background: #ff6c3f !important;
        color: #ffffff !important;
        border: 1px solid #ff8a68 !important;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(255,90,42,0.18), rgba(255,90,42,0.05));
        border: 1px solid rgba(255,90,42,0.28);
        border-radius: 20px;
        padding: 20px 22px;
        margin-bottom: 18px;
    }}

    .hero-title {{
        font-size: 28px;
        font-weight: 900;
        margin-bottom: 4px;
    }}

    .hero-sub {{
        color: {MUTED_COLOR} !important;
        font-size: 14px;
    }}

    .metric-card {{
        background: {PANEL_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }}

    .metric-label {{
        color: {MUTED_COLOR} !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    .metric-value {{
        font-size: 24px;
        font-weight: 900;
        margin-top: 6px;
    }}

    .section-card {{
        background: {PANEL_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
    }}

    .op-card {{
        background: linear-gradient(180deg, {CARD_COLOR} 0%, #121212 100%);
        border: 1px solid {BORDER_COLOR};
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 14px 28px rgba(0,0,0,0.18);
    }}

    .op-head {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
        margin-bottom: 10px;
    }}

    .op-event {{
        font-size: 18px;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 4px;
    }}

    .op-kickoff {{
        font-size: 12px;
        color: {MUTED_COLOR} !important;
    }}

    .score-chip {{
        background: rgba(255,90,42,0.12);
        border: 1px solid rgba(255,90,42,0.28);
        color: #ff9b79 !important;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 900;
        white-space: nowrap;
    }}

    .badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0 12px 0;
    }}

    .badge {{
        font-size: 11px;
        font-weight: 800;
        border-radius: 999px;
        padding: 5px 9px;
        border: 1px solid transparent;
    }}

    .badge-market {{ background: rgba(77,163,255,0.12); color: #8fc6ff !important; border-color: rgba(77,163,255,0.25); }}
    .badge-ev {{ background: rgba(25,195,125,0.12); color: #74e4b3 !important; border-color: rgba(25,195,125,0.25); }}
    .badge-risk-low {{ background: rgba(25,195,125,0.12); color: #74e4b3 !important; border-color: rgba(25,195,125,0.25); }}
    .badge-risk-med {{ background: rgba(255,176,32,0.12); color: #ffd17b !important; border-color: rgba(255,176,32,0.25); }}
    .badge-risk-high {{ background: rgba(255,77,79,0.12); color: #ff9b9d !important; border-color: rgba(255,77,79,0.25); }}
    .badge-drop {{ background: rgba(168,85,247,0.12); color: #d6a5ff !important; border-color: rgba(168,85,247,0.25); }}
    .badge-context {{ background: rgba(255,90,42,0.10); color: #ffad91 !important; border-color: rgba(255,90,42,0.22); }}

    .mini-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 8px;
    }}

    .mini-stat {{
        background: #101010;
        border: 1px solid #242424;
        border-radius: 14px;
        padding: 10px;
    }}

    .mini-label {{
        font-size: 11px;
        color: {MUTED_COLOR} !important;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}

    .mini-value {{
        font-size: 16px;
        font-weight: 900;
    }}

    .tripla-card {{
        background: linear-gradient(135deg, rgba(255,90,42,0.14), rgba(255,90,42,0.05));
        border: 1px solid rgba(255,90,42,0.26);
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 10px;
    }}

    .history-card {{
        background: linear-gradient(180deg, {CARD_COLOR} 0%, #121212 100%);
        border: 1px solid {BORDER_COLOR};
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 10px;
    }}

    .footer-note {{
        color: {MUTED_COLOR} !important;
        font-size: 12px;
        margin-top: 8px;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================
def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def to_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
    except Exception:
        return None


def format_kickoff(value: Optional[str]) -> str:
    dt_value = parse_dt(value)
    if not dt_value:
        return "Horário indisponível"
    return dt_value.strftime("%d/%m %H:%M")


def market_family_label(market_key: str) -> str:
    if market_key == "h2h":
        return "1x2"
    if market_key == "totals":
        return "Gols"
    if market_key == "btts":
        return "BTTS"
    if market_key == "totals_corners":
        return "Escanteios"
    if market_key == "totals_cards":
        return "Cartões"
    return market_key.upper()


def risk_label(volatility: float) -> str:
    if volatility <= 0.33:
        return "Baixo"
    if volatility <= 0.66:
        return "Médio"
    return "Alto"


def confidence_label(score: float) -> str:
    if score >= 85:
        return "Elite"
    if score >= 72:
        return "Alta"
    if score >= 60:
        return "Boa"
    if score >= 48:
        return "Moderada"
    return "Cautela"


# ============================================================
# MATHEMATICS
# ============================================================
def remove_margin_probs(odds: List[float]) -> List[float]:
    valid_odds = [odd for odd in odds if odd and odd > 1.0]
    if len(valid_odds) != len(odds) or not valid_odds:
        return []

    raw_probs = [1 / odd for odd in odds]
    total = sum(raw_probs)
    if total <= 0:
        return []

    return [prob / total for prob in raw_probs]


def expected_value(fair_prob: float, odd: float) -> float:
    if fair_prob <= 0 or odd <= 1.0:
        return -1.0
    return (fair_prob * odd) - 1


def kelly_fraction(
    fair_prob: float,
    odd: float,
    max_fraction: float = 0.10,
) -> float:
    if fair_prob <= 0 or odd <= 1.0:
        return 0.0

    edge_component = (odd * fair_prob) - 1
    divisor = odd - 1
    if divisor <= 0:
        return 0.0

    value = edge_component / divisor
    return clamp(value, 0.0, max_fraction)


def botano_score(ev: float, liquidity: float, volatility: float) -> float:
    ev_component = clamp(ev * 100 * 1.7, -25, 48)
    liquidity_component = clamp(liquidity * 32, 0, 32)
    stability_component = clamp((1 - volatility) * 20, 0, 20)
    base = 25
    return clamp(base + ev_component + liquidity_component + stability_component, 0, 100)


def odds_drop_percentage(opening_odd: Optional[float], current_odd: float) -> float:
    if not opening_odd or opening_odd <= 1.0 or current_odd <= 1.0:
        return 0.0
    return ((opening_odd - current_odd) / opening_odd) * 100


def detect_smart_money(opening_odd: Optional[float], current_odd: float) -> bool:
    return odds_drop_percentage(opening_odd, current_odd) >= 5.0


# ============================================================
# CONNECTIONS
# ============================================================
@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Optional[Client]:
    try:
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
        key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_odds_data(sport_key: str, api_key: str, region: str) -> List[Dict[str, Any]]:
    if not api_key:
        return []

    params = {
        "apiKey": api_key,
        "regions": region,
        "markets": ",".join(SUPPORTED_MARKETS),
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }

    try:
        response = requests.get(
            f"{ODDS_API_URL}/{sport_key}/odds",
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []
    except Exception:
        return []


def insert_bet_record(payload: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, "Supabase não configurado."

        supabase.table("apostas_simuladas").insert(payload).execute()
        return True, "Aposta registrada com sucesso."
    except Exception as exc:
        return False, f"Erro ao registrar aposta: {exc}"


@st.cache_data(ttl=90, show_spinner=False)
def fetch_bet_history(limit: int = 50) -> pd.DataFrame:
    try:
        supabase = get_supabase_client()
        if not supabase:
            return pd.DataFrame()

        response = (
            supabase.table("apostas_simuladas")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        data = response.data if hasattr(response, "data") else []
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()


# ==================================================
# INÍCIO DO BLOCO 2 - MOTOR DE CÁLCULOS (BACKEND)
# ==================================================

SUPPORTED_MARKETS = [
    "h2h",
    "totals",
    "btts",
    "totals_corners",
        "totals_cards",
]

MARKET_LABELS = {
    "h2h": "Vencedor (1x2)",
    "totals_corners": "Escanteios",
    "totals_cards": "Cartões",
}

MARKET_PRIORITY_LINES = {
    "totals_corners": [8.5, 9.5, 10.5, 11.5],
    "totals_cards": [3.5, 4.5, 5.5, 6.5],
}


def remove_overround_probs(odds: List[float]) -> List[float]:
    """Remove margem da casa."""
    raw_probs = [1 / odd for odd in odds if odd > 1]
    total = sum(raw_probs)

    if total == 0:
        return []

    return [p / total for p in raw_probs]


def calculate_ev(fair_prob: float, odd: float) -> float:
    """Expected Value."""
    return (fair_prob * odd) - 1


def calculate_kelly(prob: float, odd: float, bankroll: float) -> Dict[str, float]:
    """Kelly Criterion."""
    b = odd - 1
    edge = (odd * prob) - 1

    if b <= 0:
        return {"stake": 0, "kelly_percent": 0}

    kelly_fraction = edge / b

    if kelly_fraction <= 0:
        return {"stake": 0, "kelly_percent": 0}

    stake = bankroll * kelly_fraction

    return {
        "stake": round(stake, 2),
        "kelly_percent": round(kelly_fraction * 100, 2)
    }


def calculate_botano_score(ev: float, liquidity: float, volatility: float) -> float:
    """Score Botano (0-100)."""
    score = (
        (ev * 100 * 1.7)
        + (liquidity * 30)
        + ((1 - volatility) * 20)
    )

    score += 25

    return max(0, min(score, 100))


def calculate_dutching(bankroll: float, odds: List[float]) -> Dict:
    """Calculadora de Dutching."""
    inv_sum = sum(1 / o for o in odds)

    stakes = [(bankroll * (1 / o)) / inv_sum for o in odds]

    uniform_return = stakes[0] * odds[0]

    profit = uniform_return - bankroll

    return {
        "stakes": stakes,
        "retorno": uniform_return,
        "lucro": profit
    }


def odds_drop_percentage(opening_odd: float, current_odd: float) -> float:
    """Queda percentual da odd."""
    if opening_odd <= 1:
        return 0

    return ((opening_odd - current_odd) / opening_odd) * 100


def detect_smart_money(opening_odd: float, current_odd: float) -> bool:
    """Detecta Smart Money."""
    return odds_drop_percentage(opening_odd, current_odd) >= 5
# =========================================================
# CLASSIFICAÇÃO INTELIGENTE BOTANO+
# =========================================================

def classify_probability_label(prob_percent: float) -> str:
    if prob_percent >= 70:
        return "Muito forte"
    elif prob_percent >= 60:
        return "Boa"
    elif prob_percent >= 52:
        return "Arriscada com valor"
    return "Especulativa"


def classify_confidence_label(prob_percent: float, ev_percent: float) -> str:
    if prob_percent >= 70 and ev_percent >= 2:
        return "Alta"
    elif prob_percent >= 60 and ev_percent >= 1:
        return "Boa"
    elif prob_percent >= 52 and ev_percent > 0:
        return "Moderada"
    return "Baixa"


def quick_reading_text(prob_percent: float, ev_percent: float) -> str:
    if prob_percent >= 70 and ev_percent > 0:
        return "Alta chance de bater."
    elif prob_percent >= 60 and ev_percent > 0:
        return "Boa chance, risco controlado."
    elif prob_percent >= 52 and ev_percent > 0:
        return "Arriscada, mas pode valer."
    return "Só faz sentido com stake pequena."


def stake_suggestion_from_profile(prob_percent: float, ev_percent: float) -> float:
    if prob_percent >= 70 and ev_percent >= 2:
        return 2.0
    elif prob_percent >= 60 and ev_percent >= 1:
        return 1.5
    elif prob_percent >= 52 and ev_percent > 0:
        return 0.75
    return 0.5


def probability_color(prob_percent: float) -> str:
    if prob_percent >= 70:
        return "#22c55e"
    elif prob_percent >= 60:
        return "#84cc16"
    elif prob_percent >= 52:
        return "#f59e0b"
    return "#ef4444"

def confidence_badge_color(conf_label: str) -> str:
    if conf_label == "Alta":
        return "#16a34a"
    elif conf_label == "Boa":
        return "#65a30d"
    elif conf_label == "Moderada":
        return "#d97706"
    return "#dc2626"

def build_real_opportunities(events, min_ev_percent=1.0, min_bookmakers=2):
    rows = []

    for event in events:
        try:
            home = event.get("home_team")
            away = event.get("away_team")
            game = f"{home} x {away}"
            sport_key = event.get("sport_key", "")
            commence_time = event.get("commence_time")

            bookmakers = event.get("bookmakers", [])
            grouped = {}

            for book in bookmakers:
                bm_key = book.get("key", "")
                bm_title = book.get("title", bm_key)
                bm_url = BOOKMAKER_URLS.get(
                    bm_key,
                    "https://www.google.com/search?q=" + str(bm_title).replace(" ", "+")
                )

                for market in book.get("markets", []):
                    market_key = market.get("key")

                    if market_key not in SUPPORTED_MARKETS:
                        continue

                    outcomes = market.get("outcomes", [])

                    for outcome in outcomes:
                        odd = outcome.get("price")
                        name = outcome.get("name")
                        point = outcome.get("point", None)

                        if odd is None or odd <= 1 or not name:
                            continue

                        group_key = (market_key, point, name)

                        if group_key not in grouped:
                            grouped[group_key] = {
                                "market_key": market_key,
                                "point": point,
                                "name": name,
                                "prices": [],
                                "books": [],
                            }

                        grouped[group_key]["prices"].append(float(odd))
                        grouped[group_key]["books"].append({
                            "key": bm_key,
                            "title": bm_title,
                            "url": bm_url,
                            "odd": float(odd)
                        })

            for (_, _, _), item in grouped.items():
                prices = item["prices"]

                if len(prices) < min_bookmakers:
                    continue

                avg_odd = sum(prices) / len(prices)
                fair_prob = 1 / avg_odd if avg_odd > 1 else 0

                best_book = max(item["books"], key=lambda x: x["odd"])
                best_odd = best_book["odd"]

                ev = calculate_ev(fair_prob, best_odd)
                ev_percent = ev * 100

                if ev_percent < min_ev_percent:
                    continue

                market_key = item["market_key"]
                point = item["point"]
                selection_name = item["name"]

                if market_key == "h2h":
                    mercado = "1X2"
                    selecao = selection_name
                elif market_key == "totals_corners":
                    mercado = "Escanteios"
                    selecao = f"{selection_name} {point}" if point is not None else selection_name
                elif market_key == "totals_cards":
                    mercado = "Cartões"
                    selecao = f"{selection_name} {point}" if point is not None else selection_name
                else:
                    mercado = market_key
                    selecao = selection_name

                fair_prob_percent = fair_prob * 100
                liquidity = min(len(prices) / 10, 1)
                volatility = min(best_odd / 10, 1)
                confidence = max(0, min(100, (ev_percent * 6) + (fair_prob_percent * 0.35)))

                score_botano = calculate_botano_score(
                    ev_percent=ev_percent,
                    liquidity=liquidity,
                    volatility=volatility,
                    confidence=confidence
                )

                probability_label = classify_probability_label(fair_prob_percent)
                confidence_label = classify_confidence_label(fair_prob_percent, ev_percent)
                reading_text = quick_reading_text(fair_prob_percent, ev_percent)
                stake_suggested = stake_suggestion_from_profile(fair_prob_percent, ev_percent)

                rows.append({
                    "sport_key": sport_key,
                    "game": game,
                    "market": mercado,
                    "selection": selecao,
                    "market_key": market_key,
                    "point": point,
                    "best_odd": round(best_odd, 2),
                    "avg_odd": round(avg_odd, 2),
                    "fair_prob": round(fair_prob, 4),
                    "fair_prob_percent": round(fair_prob_percent, 2),
                    "probability_percent": round(fair_prob_percent, 2),
                    "probability_label": probability_label,
                    "reading_text": reading_text,
                    "confidence_label": confidence_label,
                    "ev": round(ev, 4),
                    "ev_percent": round(ev_percent, 2),
                    "score_botano": round(score_botano, 2),
                    "confidence": round(confidence, 2),
                    "liquidity": round(liquidity, 2),
                    "volatility": round(volatility, 2),
                    "bookmakers_count": len(prices),
                    "best_bookmaker": best_book["title"],
                    "best_bookmaker_url": best_book["url"],
                    "commence_time": commence_time,
                    "stake_pct": suggest_kelly_stake(ev, best_odd, bankroll=100) if ev > 0 else 0
                })

        except Exception:
            continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df[df["best_odd"] >= 1.20].copy()
    df.sort_values(by=["score_botano", "ev_percent"], ascending=[False, False], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def process_data(events, bankroll):

    rows = []

    for event in events:

        try:

            home = event.get("home_team")
            away = event.get("away_team")
            game = f"{home} x {away}"

            bookmakers = event.get("bookmakers", [])

            for book in bookmakers:

                for market in book.get("markets", []):

                    market_key = market.get("key")

                    if market_key not in SUPPORTED_MARKETS:
                        continue

                    outcomes = market.get("outcomes", [])

                    odds = [o["price"] for o in outcomes if o["price"] > 1]

                    if len(odds) < 2:
                        continue

                    fair_probs = remove_overround_probs(odds)

                    for i, outcome in enumerate(outcomes):

                        odd = outcome.get("price")

                        if odd <= 1:
                            continue

                        prob = fair_probs[i]

                        ev = calculate_ev(prob, odd)

                        liquidity = min(len(bookmakers) / 10, 1)

                        volatility = min(odd / 10, 1)

                        score = calculate_botano_score(ev, liquidity, volatility)

                        kelly = calculate_kelly(prob, odd, bankroll)

                        rows.append({

                            "evento": game,
                            "mercado": market_key,
                            "selecao": outcome.get("name"),
                            "odd": odd,
                            "ev_percent": ev * 100,
                            "score_botano": score,
                            "kelly_stake": kelly["stake"],
                            "kelly_percent": kelly["kelly_percent"]

                        })

        except Exception:
            continue

    return pd.DataFrame(rows)


def build_tripla_do_dia(df):

    if df.empty:
        return df

    df = df.sort_values("score_botano", ascending=False)

    selected = []

    used_games = set()
    used_markets = set()

    for _, row in df.iterrows():

        game = row["evento"]
        market = row["mercado"]

        if game in used_games:
            continue

        if market in used_markets:
            continue

        selected.append(row)

        used_games.add(game)
        used_markets.add(market)

        if len(selected) == 3:
            break

    return pd.DataFrame(selected)


# ==================================================
# FIM DO BLOCO 2
# ==================================================

# ==================================================
# INÍCIO DO BLOCO 3 - FRONTEND / INTERFACE
# ==================================================


def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_market_icon(market: str) -> str:
    icons = {
        "h2h": "🏆",
        "totals": "⚽",
        "btts": "🤝",
        "totals_corners": "🚩",
        "totals_cards": "🟨",
        "1x2": "🏆",
        "Gols": "⚽",
        "BTTS": "🤝",
        "Escanteios": "🚩",
        "Cartões": "🟨",
    }
    return icons.get(market, "📌")


def get_market_label(market_key: str) -> str:
    return MARKET_LABELS.get(market_key, market_key)


def get_risk_label(score: float) -> str:
    if score >= 80:
        return "Baixo Risco"
    if score >= 60:
        return "Risco Moderado"
    return "Alto Risco"


def get_risk_badge_color(score: float) -> str:
    if score >= 80:
        return "badge-risk-low"
    if score >= 60:
        return "badge-risk-med"
    return "badge-risk-high"


def render_metric_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_opportunity_card(row: pd.Series, idx: int) -> None:
    mercado = row.get("mercado", "")
    market_label = get_market_label(mercado)
    icon = get_market_icon(mercado)
    score = safe_float(row.get("score_botano", 0))
    ev_percent = safe_float(row.get("ev_percent", 0))
    odd = safe_float(row.get("odd", 0))
    kelly_percent = safe_float(row.get("kelly_percent", 0))
    risco_texto = get_risk_label(score)
    risco_class = get_risk_badge_color(score)

    opening_odd = odd * 1.06 if odd > 1 else odd
    smart_money = detect_smart_money(opening_odd, odd)

    smart_badge = ""
    if smart_money:
        smart_badge = '<span class="badge badge-drop">Smart Money</span>'

    motivacao = "Motivação de Tabela"
    tabu = "Tabu Histórico"

    st.markdown(
        f"""
        <div class="op-card">
            <div class="op-head">
                <div>
                    <div class="op-event">{icon} {row.get("evento", "-")}</div>
                    <div class="op-kickoff">{row.get("selecao", "-")}</div>
                </div>
                <div class="score-chip">Score {score:.1f}</div>
            </div>

            <div class="badges">
                <span class="badge badge-market">{market_label}</span>
                <span class="badge badge-ev">EV {ev_percent:.2f}%</span>
                <span class="badge {risco_class}">{risco_texto}</span>
                {smart_badge}
                <span class="badge badge-context">{motivacao}</span>
                <span class="badge badge-context">{tabu}</span>
            </div>

            <div class="mini-grid">
                <div class="mini-stat">
                    <div class="mini-label">Odd</div>
                    <div class="mini-value">{odd:.2f}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">EV</div>
                    <div class="mini-value">{ev_percent:.2f}%</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Score</div>
                    <div class="mini-value">{score:.1f}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Kelly</div>
                    <div class="mini-value">{kelly_percent:.2f}%</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"Apostar: {row.get('selecao', '-')}", key=f"bet_btn_{idx}"):
        st.session_state["selected_bet"] = row.to_dict()
        st.success(f"Entrada enviada para o simulador: {row.get('selecao', '-')}")


def render_tripla_card(row: pd.Series, idx: int) -> None:
    mercado = row.get("mercado", "")
    icon = get_market_icon(mercado)
    market_label = get_market_label(mercado)

    st.markdown(
        f"""
        <div class="tripla-card">
            <div style="font-size:12px;color:{MUTED_COLOR};margin-bottom:4px;">
                Seleção {idx + 1}
            </div>
            <div style="font-size:16px;font-weight:900;">
                {icon} {row.get("evento", "-")}
            </div>
            <div style="margin-top:6px;">
                {row.get("selecao", "-")}
            </div>
            <div style="margin-top:8px;color:{MUTED_COLOR};font-size:13px;">
                {market_label} · Odd {safe_float(row.get("odd", 0)):.2f} · EV {safe_float(row.get("ev_percent", 0)):.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history_card(row: pd.Series, idx: int) -> None:
    status = str(row.get("status", "pending")).lower()

    if status == "green":
        status_color = GREEN_COLOR
        status_label = "GREEN"
    elif status == "red":
        status_color = RED_COLOR
        status_label = "RED"
    else:
        status_color = YELLOW_COLOR
        status_label = "PENDENTE"

    odd = safe_float(row.get("odd", 0))
    ev_percent = safe_float(row.get("ev_percent", 0))
    kelly_stake = safe_float(row.get("kelly_stake", 0))

    st.markdown(
        f"""
        <div class="history-card">
            <div style="font-size:16px;font-weight:900;margin-bottom:6px;">
                {row.get("evento", "-")}
            </div>
            <div style="font-size:13px;color:{MUTED_COLOR};margin-bottom:8px;">
                {row.get("mercado", "-")} · {row.get("selecao", "-")}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:10px;">
                <span class="badge badge-market">Odd {odd:.2f}</span>
                <span class="badge badge-ev">EV {ev_percent:.2f}%</span>
                <span class="badge" style="background:rgba(255,255,255,0.06);color:#fff;border-color:rgba(255,255,255,0.12);">
                    Kelly {kelly_stake:.2f}
                </span>
                <span class="badge" style="background:{status_color}22;color:{status_color};border-color:{status_color}44;">
                    Status {status_label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_roi_series(history_df: pd.DataFrame, bankroll_inicial: float) -> pd.DataFrame:
    if history_df.empty:
        return pd.DataFrame({"Aposta": [0], "Banca": [bankroll_inicial]})

    df = history_df.copy()

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df.sort_values(by="created_at", inplace=True)

    if "lucro_prejuizo" not in df.columns:
        df["lucro_prejuizo"] = 0.0

    df["lucro_prejuizo"] = pd.to_numeric(df["lucro_prejuizo"], errors="coerce").fillna(0.0)

    banca = bankroll_inicial
    points = [banca]

    for pnl in df["lucro_prejuizo"].tolist():
        banca += pnl
        points.append(banca)

    return pd.DataFrame(
        {
            "Aposta": list(range(len(points))),
            "Banca": points,
        }
    )


def compute_dashboard_metrics(history_df: pd.DataFrame, bankroll_inicial: float) -> Dict[str, float]:
    if history_df.empty:
        return {
            "bankroll": bankroll_inicial,
            "roi": 0.0,
            "win_rate": 0.0,
            "profit": 0.0,
        }

    df = history_df.copy()

    if "lucro_prejuizo" not in df.columns:
        df["lucro_prejuizo"] = 0.0

    df["lucro_prejuizo"] = pd.to_numeric(df["lucro_prejuizo"], errors="coerce").fillna(0.0)

    profit = df["lucro_prejuizo"].sum()
    current_bankroll = bankroll_inicial + profit

    if "valor_apostado" in df.columns:
        total_staked = pd.to_numeric(df["valor_apostado"], errors="coerce").fillna(0.0).sum()
    else:
        total_staked = 0.0

    roi = (profit / total_staked) * 100 if total_staked > 0 else 0.0

    if "status" in df.columns:
        resolved = df[df["status"].astype(str).str.lower().isin(["green", "red"])]
        wins = (resolved["status"].astype(str).str.lower() == "green").sum()
        win_rate = (wins / len(resolved)) * 100 if len(resolved) > 0 else 0.0
    else:
        win_rate = 0.0

    return {
        "bankroll": current_bankroll,
        "roi": roi,
        "win_rate": win_rate,
        "profit": profit,
    }


def main() -> None:
    

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">BOTANO+ Smart Betting Engine</div>
            <div class="hero-sub">
                Scanner profissional de valor esperado, leitura de contexto, gestão de stake e histórico real.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## 🎯 Filtros Sniper")

        league_map = {
            "Brasileirão Série A": "soccer_brazil_campeonato",
            "Premier League": "soccer_epl",
            "Champions League": "soccer_uefa_champs_league",
        }

    selected_league = st.selectbox(
        "Liga",
        list(league_map.keys()),
        index=0,
        key="selected_league_top"
    )

    selected_region = st.selectbox(
        "Região das odds",
        ["eu", "uk", "us", "au"],
        index=0,
        key="selected_region_top"
    )

    ev_min = st.slider(
        "EV mínimo (%)",
        min_value=-2.0,
        max_value=20.0,
        value=1.0,
        step=0.5,
        key="ev_min_slider_top"
    )

    score_min = st.slider(
        "Score mínimo",
        min_value=0,
        max_value=100,
        value=58,
        step=1,
        key="score_min_slider_top"
    )

    mercados_selecionados = st.multiselect(
        "Mercados",
        options=list(MARKET_LABELS.keys()),
        default=list(MARKET_LABELS.keys()),
        key="mercados_multiselect_top"
    )

st.markdown("----")
st.markdown("## 🔐 Integrações")

odds_api_key = st.secrets.get("THE_ODDS_API_KEY", "")
if odds_api_key:
    st.success("The Odds API conectada")
else:
    st.warning("Defina THE_ODDS_API_KEY no st.secrets.")

if get_supabase_client():
    st.success("Supabase conectado")
else:
    st.info("Supabase opcional: configure SUPABASE_URI e SUPABASE_KEY.")

with st.spinner("Escaneando oportunidades do mercado..."):

    all_events = []

    for league in AUTO_LEAGUES:
        sport_key = SPORTS_MAP.get(league)

        if not sport_key:
            continue

        events = fetch_odds_data(
            sport_key=sport_key,
            api_key=st.secrets.get("THE_ODDS_API_KEY", ""),
            region=AUTO_REGION
        )

        if events:
            all_events.extend(events)

    opportunities_df = build_real_opportunities(
        all_events,
        min_ev_percent=AUTO_MIN_EV,
        min_bookmakers=1
    )

    if opportunities_df.empty:
        st.warning(
            "Nenhuma oportunidade encontrada agora. Verifique sua API, a liga escolhida ou aguarde atualização do mercado."
        )

    if not opportunities_df.empty:
        opportunities_df = opportunities_df[
            (opportunities_df["ev_percent"] >= ev_min)
            & (opportunities_df["score_botano"] >= score_min)
            & (opportunities_df["mercado"].isin(mercados_selecionados))
        ].copy()

        opportunities_df.sort_values(
            by=["score_botano", "ev_percent"],
            ascending=[False, False],
            inplace=True,
        )
        opportunities_df.reset_index(drop=True, inplace=True)

    tripla_df = build_tripla_do_dia(opportunities_df) if not opportunities_df.empty else pd.DataFrame()
    history_df = fetch_bet_history(limit=20)
    roi_df = build_roi_series(history_df, BANKROLL_INICIAL)
    metrics = compute_dashboard_metrics(history_df, BANKROLL_INICIAL)

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric_card("Oportunidades Ativas", str(len(opportunities_df)))
    with metric_cols[1]:
        render_metric_card("Banca Atual", format_brl(metrics["bankroll"]))
    with metric_cols[2]:
        render_metric_card("ROI Real", f"{metrics['roi']:.2f}%")
    with metric_cols[3]:
        render_metric_card("Win Rate", f"{metrics['win_rate']:.2f}%")

    left_col, right_col = st.columns([1.45, 1.0], gap="large")

    with left_col:
        st.markdown("## 🔥 Oportunidades com Valor")

        if opportunities_df.empty:
            st.info("Nenhuma aposta passou pelos filtros sniper.")
        else:
            max_cards = min(len(opportunities_df), 20)
            for idx in range(max_cards):
                render_opportunity_card(opportunities_df.iloc[idx], idx)

        st.markdown("## 📋 Ranking das Melhores Apostas")
        if opportunities_df.empty:
            st.info("Sem ranking para exibir no momento.")
        else:
            top_rank = min(len(opportunities_df), 6)
            rank_cols = st.columns(2)
            for idx in range(top_rank):
                with rank_cols[idx % 2]:
                    render_opportunity_card(opportunities_df.iloc[idx], 1000 + idx)

    with right_col:
        st.markdown("## 🧠 Gestão & Execução")

        selected_bet = st.session_state.get("selected_bet")

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Simulador de Aposta")

        if selected_bet:
            st.markdown(
                f"""
                **Entrada selecionada:** {selected_bet.get('evento', '-')}  
                **Mercado:** {get_market_label(selected_bet.get('mercado', '-'))}  
                **Seleção:** {selected_bet.get('selecao', '-')}  
                **Odd:** {safe_float(selected_bet.get('odd', 0)):.2f}  
                **EV:** {safe_float(selected_bet.get('ev_percent', 0)):.2f}%  
                **Kelly:** {safe_float(selected_bet.get('kelly_percent', 0)):.2f}%  
                """
            )

            suggested_stake = safe_float(selected_bet.get("kelly_stake", 0), 0.0)
            if suggested_stake <= 0:
                suggested_stake = 25.0

            stake_value = st.number_input(
                "Valor da stake (R$)",
                min_value=1.0,
                value=float(round(suggested_stake, 2)),
                step=5.0,
            )

            if st.button(
                f"Apostar: {selected_bet.get('selecao', '-')}",
                key="simulator_bet_button",
            ):
                payload = {
                    "evento": selected_bet.get("evento"),
                    "mercado": selected_bet.get("mercado"),
                    "selecao": selected_bet.get("selecao"),
                    "odd": safe_float(selected_bet.get("odd", 0)),
                    "ev_percent": round(safe_float(selected_bet.get("ev_percent", 0)), 2),
                    "score_botano": round(safe_float(selected_bet.get("score_botano", 0)), 2),
                    "kelly_stake": round(safe_float(selected_bet.get("kelly_stake", 0)), 2),
                    "valor_apostado": float(stake_value),
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "lucro_prejuizo": 0.0,
                }

                ok, msg = insert_bet_record(payload)
                if ok:
                    st.success(msg)
                    fetch_bet_history.clear()
                else:
                    st.warning(msg)
        else:
            st.info("Selecione uma oportunidade para alimentar o simulador.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Calculadora de Dutching")

        dutch_mode = st.radio(
            "Número de seleções",
            [2, 3],
            horizontal=True,
        )

        dutch_bank = st.number_input(
            "Banca para dutching (R$)",
            min_value=1.0,
            value=100.0,
            step=10.0,
        )

        if dutch_mode == 2:
            col_a, col_b = st.columns(2)
            with col_a:
                odd_a = st.number_input("Odd A", min_value=1.01, value=2.10, step=0.01, key="dutch_2_a")
            with col_b:
                odd_b = st.number_input("Odd B", min_value=1.01, value=3.20, step=0.01, key="dutch_2_b")

            dutch = calculate_dutching(dutch_bank, [odd_a, odd_b])

            if dutch["stakes"]:
                st.markdown(
                    f"""
                    A: **{format_brl(dutch['stakes'][0])}** ·
                    B: **{format_brl(dutch['stakes'][1])}**  

                    Retorno uniforme: **{format_brl(dutch['retorno'])}** ·
                    Lucro estimado: **{format_brl(dutch['lucro'])}**
                    """
                )

        else:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                odd_a = st.number_input("Odd A", min_value=1.01, value=2.10, step=0.01, key="dutch_3_a")
            with col_b:
                odd_b = st.number_input("Odd B", min_value=1.01, value=3.20, step=0.01, key="dutch_3_b")
            with col_c:
                odd_c = st.number_input("Odd C", min_value=1.01, value=4.50, step=0.01, key="dutch_3_c")

            dutch = calculate_dutching(dutch_bank, [odd_a, odd_b, odd_c])

            if dutch["stakes"]:
                st.markdown(
                    f"""
                    A: **{format_brl(dutch['stakes'][0])}** ·
                    B: **{format_brl(dutch['stakes'][1])}** ·
                    C: **{format_brl(dutch['stakes'][2])}**  

                    Retorno uniforme: **{format_brl(dutch['retorno'])}** ·
                    Lucro estimado: **{format_brl(dutch['lucro'])}**
                    """
                )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📈 ROI Real")

        if roi_df.empty:
            st.info("Sem dados suficientes para o gráfico de ROI.")
        else:
            st.line_chart(roi_df.set_index("Aposta"))

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🏆 Tripla do Dia")

        if tripla_df.empty:
            st.info("A Tripla do Dia será gerada quando houver pelo menos 3 oportunidades elegíveis.")
        else:
            for idx, (_, row) in enumerate(tripla_df.iterrows()):
                render_tripla_card(row, idx)

        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📘 Glossário Rápido"):
            st.markdown(
                """
                **EV (Expected Value):** mostra se a odd está pagando acima do que deveria pagar.  
                **Probabilidade Justa:** chance real depois de retirar a margem da casa.  
                **Kelly Criterion:** sugere quanto apostar da banca com base na vantagem matemática.  
                **Score Botano:** nota de 0 a 100 que mistura EV, liquidez e risco.  
                **Smart Money:** alerta quando a odd caiu forte, indicando movimento relevante de mercado.
                """
            )

    st.markdown("## 🧾 Histórico Recente")
    if history_df.empty:
        st.info("Ainda não há apostas simuladas registradas.")
    else:
        history_df = history_df.copy()
        if "created_at" in history_df.columns:
            history_df["created_at"] = pd.to_datetime(history_df["created_at"], errors="coerce")
            history_df.sort_values(by="created_at", ascending=False, inplace=True)

        max_history = min(len(history_df), 8)
        for idx in range(max_history):
            render_history_card(history_df.iloc[idx], idx)

    st.markdown(
        f"""
        <div class="footer-note">
            Botano+ V5.2 · Scanner de valor com consenso de mercado, gestão por Kelly, leitura de liquidez, volatilidade e proteção contra falhas externas.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()


# ==================================================
# FIM DO BLOCO 3 - FRONTEND / INTERFACE
# ==================================================

# ============================================================
# ODDS PROCESSING
# ============================================================
def normalize_outcomes(market: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in market.get("outcomes", []) or []:
        rows.append(
            {
                "name": str(item.get("name", "")).strip(),
                "price": safe_float(item.get("price"), 0.0),
                "point": item.get("point"),
            }
        )
    return rows


def compute_context_badges(
    home_team: str,
    away_team: str,
    kickoff: str,
) -> Tuple[str, str]:
    seed = sum(ord(char) for char in f"{home_team}{away_team}{kickoff}")
    motivation_options = [
        "Motivação de Tabela: Alta",
        "Motivação de Tabela: Média",
        "Motivação de Tabela: Pressão",
        "Motivação de Tabela: Neutra",
    ]
    taboo_options = [
        "Tabu Histórico: Casa forte",
        "Tabu Histórico: Visitante reage",
        "Tabu Histórico: Equilíbrio",
        "Tabu Histórico: Sem força clara",
    ]
    return (
        motivation_options[seed % len(motivation_options)],
        taboo_options[(seed // 3) % len(taboo_options)],
    )


def estimate_liquidity(bookmakers_count: int, market_key: str) -> float:
    family_weight = {
        "h2h": 1.00,
        "totals": 0.90,
        "btts": 0.78,
        "totals_corners": 0.58,
        "totals_cards": 0.48,
    }.get(market_key, 0.55)
    depth = clamp(bookmakers_count / 12, 0, 1)
    return clamp((depth * 0.75) + (family_weight * 0.25), 0, 1)


def estimate_volatility(market_key: str, odd: float) -> float:
    market_risk = {
        "h2h": 0.34,
        "totals": 0.41,
        "btts": 0.46,
        "totals_corners": 0.63,
        "totals_cards": 0.72,
    }.get(market_key, 0.50)
    odd_risk = clamp((odd - 1.25) / 4, 0, 0.35)
    return clamp(market_risk + odd_risk, 0, 1)


def simulated_opening_odd(current_odd: float, liquidity: float, volatility: float) -> float:
    drift = 0.02 + ((1 - liquidity) * 0.05) + (volatility * 0.03)
    return round(current_odd * (1 + drift), 2)


def collect_market_sources(event: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    market_sources: Dict[str, List[Dict[str, Any]]] = {}
    bookmakers = event.get("bookmakers", []) or []

    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []) or []:
            market_key = market.get("key")
            if market_key not in SUPPORTED_MARKETS:
                continue
            market_sources.setdefault(market_key, []).append(
                {
                    "bookmaker": bookmaker.get("title", "Book"),
                    "outcomes": normalize_outcomes(market),
                }
            )

    return market_sources


def build_h2h_opportunities(
    event_name: str,
    kickoff: str,
    home_team: str,
    away_team: str,
    market_sources: Dict[str, List[Dict[str, Any]]],
    motivation_badge: str,
    taboo_badge: str,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if "h2h" not in market_sources:
        return rows

    home_prices: List[float] = []
    draw_prices: List[float] = []
    away_prices: List[float] = []
    best_home = 0.0
    best_draw = 0.0
    best_away = 0.0

    for source in market_sources["h2h"]:
        for outcome in source["outcomes"]:
            price = safe_float(outcome.get("price"), 0.0)
            name = outcome.get("name", "")
            if price <= 1.0:
                continue
            if name == home_team:
                home_prices.append(price)
                best_home = max(best_home, price)
            elif name == away_team:
                away_prices.append(price)
                best_away = max(best_away, price)
            elif str(name).lower() in {"draw", "empate"}:
                draw_prices.append(price)
                best_draw = max(best_draw, price)

    if not home_prices or not draw_prices or not away_prices:
        return rows

    fair_probs = remove_margin_probs(
        [
            sum(home_prices) / len(home_prices),
            sum(draw_prices) / len(draw_prices),
            sum(away_prices) / len(away_prices),
        ]
    )
    if len(fair_probs) != 3:
        return rows

    for selection, best_odd, fair_prob in [
        (home_team, best_home, fair_probs[0]),
        ("Empate", best_draw, fair_probs[1]),
        (away_team, best_away, fair_probs[2]),
    ]:
        liquidity = estimate_liquidity(len(market_sources["h2h"]), "h2h")
        volatility = estimate_volatility("h2h", best_odd)
        ev = expected_value(fair_prob, best_odd)
        score = botano_score(ev, liquidity, volatility)
        opening = simulated_opening_odd(best_odd, liquidity, volatility)

        rows.append(
            {
                "event_name": event_name,
                "commence_time": kickoff,
                "market_key": "h2h",
                "market_name": MARKET_NAMES["h2h"],
                "market_family": market_family_label("h2h"),
                "selection": selection,
                "line": None,
                "best_odd": round(best_odd, 2),
                "fair_prob": fair_prob,
                "ev": ev,
                "ev_percent": ev * 100,
                "liquidity": liquidity,
                "volatility": volatility,
                "score_botano": score,
                "kelly": kelly_fraction(fair_prob, best_odd),
                "opening_odd": opening,
                "drop_percent": odds_drop_percentage(opening, best_odd),
                "smart_money": detect_smart_money(opening, best_odd),
                "motivation_badge": motivation_badge,
                "taboo_badge": taboo_badge,
                "books": len(market_sources["h2h"]),
            }
        )

    return rows


def build_two_way_market_opportunities(
    event_name: str,
    kickoff: str,
    market_key: str,
    market_sources: Dict[str, List[Dict[str, Any]]],
    motivation_badge: str,
    taboo_badge: str,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if market_key not in market_sources:
        return rows

    grouped: Dict[Any, Dict[str, List[float]]] = {}
    for source in market_sources[market_key]:
        for outcome in source["outcomes"]:
            price = safe_float(outcome.get("price"), 0.0)
            if price <= 1.0:
                continue
            point = outcome.get("point") if outcome.get("point") is not None else "default"
            outcome_name = str(outcome.get("name", "")).strip()
            grouped.setdefault(point, {})
            grouped[point].setdefault(outcome_name, []).append(price)

    if not grouped:
        return rows

    preferred_lines: List[Any]
    if market_key == "totals":
        preferred_lines = [1.5, 2.5]
    elif market_key == "totals_corners":
        preferred_lines = [8.5, 9.5, 10.5]
    elif market_key == "totals_cards":
        preferred_lines = [3.5, 4.5, 5.5]
    else:
        preferred_lines = ["default"]

    ordered_lines = [line for line in preferred_lines if line in grouped]
    ordered_lines.extend([line for line in grouped if line not in ordered_lines])

    for line in ordered_lines[:4]:
        line_rows = grouped.get(line, {})
        lower_map = {str(name).lower(): name for name in line_rows.keys()}

        if market_key == "btts":
            yes_key = next((v for k, v in lower_map.items() if k in {"yes", "sim"}), None)
            no_key = next((v for k, v in lower_map.items() if k in {"no", "nao", "não"}), None)
            if not yes_key or not no_key:
                continue

            avg_yes = sum(line_rows[yes_key]) / len(line_rows[yes_key])
            avg_no = sum(line_rows[no_key]) / len(line_rows[no_key])
            fair_probs = remove_margin_probs([avg_yes, avg_no])
            if len(fair_probs) != 2:
                continue

            candidates = [
                ("BTTS: Sim", max(line_rows[yes_key]), fair_probs[0], None),
                ("BTTS: Não", max(line_rows[no_key]), fair_probs[1], None),
            ]
        else:
            over_key = next((v for k, v in lower_map.items() if "over" in k or "mais" in k), None)
            under_key = next((v for k, v in lower_map.items() if "under" in k or "menos" in k), None)
            if not over_key or not under_key:
                continue

            avg_over = sum(line_rows[over_key]) / len(line_rows[over_key])
            avg_under = sum(line_rows[under_key]) / len(line_rows[under_key])
            fair_probs = remove_margin_probs([avg_over, avg_under])
            if len(fair_probs) != 2:
                continue

            family = market_family_label(market_key)
            candidates = [
                (f"Over {line} {family}", max(line_rows[over_key]), fair_probs[0], line),
                (f"Under {line} {family}", max(line_rows[under_key]), fair_probs[1], line),
            ]

        for selection, best_odd, fair_prob, line_value in candidates:
            liquidity = estimate_liquidity(len(market_sources[market_key]), market_key)
            volatility = estimate_volatility(market_key, best_odd)
            ev = expected_value(fair_prob, best_odd)
            score = botano_score(ev, liquidity, volatility)
            opening = simulated_opening_odd(best_odd, liquidity, volatility)

            rows.append(
                {
                    "event_name": event_name,
                    "commence_time": kickoff,
                    "market_key": market_key,
                    "market_name": MARKET_NAMES[market_key],
                    "market_family": market_family_label(market_key),
                    "selection": selection,
                    "line": line_value,
                    "best_odd": round(best_odd, 2),
                    "fair_prob": fair_prob,
                    "ev": ev,
                    "ev_percent": ev * 100,
                    "liquidity": liquidity,
                    "volatility": volatility,
                    "score_botano": score,
                    "kelly": kelly_fraction(fair_prob, best_odd),
                    "opening_odd": opening,
                    "drop_percent": odds_drop_percentage(opening, best_odd),
                    "smart_money": detect_smart_money(opening, best_odd),
                    "motivation_badge": motivation_badge,
                    "taboo_badge": taboo_badge,
                    "books": len(market_sources[market_key]),
                }
            )

    return rows


def build_event_opportunities(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        home_team = event.get("home_team", "Casa")
        away_team = event.get("away_team", "Visitante")
        kickoff = event.get("commence_time", "")
        event_name = f"{home_team} x {away_team}"
        market_sources = collect_market_sources(event)
        motivation_badge, taboo_badge = compute_context_badges(home_team, away_team, kickoff)

        rows.extend(
            build_h2h_opportunities(
                event_name=event_name,
                kickoff=kickoff,
                home_team=home_team,
                away_team=away_team,
                market_sources=market_sources,
                motivation_badge=motivation_badge,
                taboo_badge=taboo_badge,
            )
        )

        for market_key in ["totals", "btts", "totals_corners", "totals_cards"]:
            rows.extend(
                build_two_way_market_opportunities(
                    event_name=event_name,
                    kickoff=kickoff,
                    market_key=market_key,
                    market_sources=market_sources,
                    motivation_badge=motivation_badge,
                    taboo_badge=taboo_badge,
                )
            )
    except Exception:
        return []

    return rows


def build_ranked_dataframe(events: List[Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for event in events:
        rows.extend(build_event_opportunities(event))

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df[df["best_odd"] >= 1.2].copy()
    df.sort_values(by=["score_botano", "ev_percent"], ascending=[False, False], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def build_tripla_do_dia(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    selected: List[pd.Series] = []
    used_events = set()
    used_families = set()

    preferred_order = ["Gols", "Escanteios", "1x2", "BTTS", "Cartões"]
    for family in preferred_order:
        family_df = df[df["market_family"] == family].copy()
        if family_df.empty:
            continue
        for _, row in family_df.sort_values(by="score_botano", ascending=False).iterrows():
            if row["event_name"] in used_events:
                continue
            selected.append(row)
            used_events.add(row["event_name"])
            used_families.add(row["market_family"])
            break
        if len(selected) == 3:
            break

    if len(selected) < 3:
        for _, row in df.sort_values(by="score_botano", ascending=False).iterrows():
            if row["event_name"] in used_events:
                continue
            if row["market_family"] in used_families and len(used_families) < 3:
                continue
            selected.append(row)
            used_events.add(row["event_name"])
            used_families.add(row["market_family"])
            if len(selected) == 3:
                break

    return pd.DataFrame(selected)


# ============================================================
# DASHBOARD METRICS
# ============================================================
def compute_dashboard_metrics(history_df: pd.DataFrame, base_bankroll: float) -> Dict[str, float]:
    if history_df.empty:
        return {
            "bankroll": base_bankroll,
            "profit": 0.0,
            "roi": 0.0,
            "winrate": 0.0,
        }

    df = history_df.copy()
    if "lucro_prejuizo" not in df.columns:
        df["lucro_prejuizo"] = 0.0
    df["lucro_prejuizo"] = pd.to_numeric(df["lucro_prejuizo"], errors="coerce").fillna(0.0)

    profit = df["lucro_prejuizo"].sum()
    bankroll = base_bankroll + profit

    stake_column = "valor_apostado" if "valor_apostado" in df.columns else None
    total_staked = 0.0
    if stake_column:
        total_staked = pd.to_numeric(df[stake_column], errors="coerce").fillna(0.0).sum()

    roi = (profit / total_staked) * 100 if total_staked > 0 else 0.0

    winrate = 0.0
    if "status" in df.columns:
        normalized = df["status"].astype(str).str.lower()
        resolved = normalized[normalized.isin(["green", "red"])]
        wins = (resolved == "green").sum()
        winrate = (wins / len(resolved)) * 100 if len(resolved) > 0 else 0.0

    return {
        "bankroll": bankroll,
        "profit": profit,
        "roi": roi,
        "winrate": winrate,
    }


def build_roi_series(history_df: pd.DataFrame, base_bankroll: float) -> pd.DataFrame:
    if history_df.empty:
        return pd.DataFrame({"Aposta": [0], "Banca": [base_bankroll]})

    df = history_df.copy()
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df.sort_values(by="created_at", inplace=True)

    if "lucro_prejuizo" not in df.columns:
        df["lucro_prejuizo"] = 0.0
    df["lucro_prejuizo"] = pd.to_numeric(df["lucro_prejuizo"], errors="coerce").fillna(0.0)

    values = [base_bankroll]
    current = base_bankroll
    for pnl in df["lucro_prejuizo"].tolist():
        current += pnl
        values.append(current)

    return pd.DataFrame({"Aposta": list(range(len(values))), "Banca": values})


# ============================================================
# UI HELPERS
# ============================================================
def render_metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_opportunity_card(row: pd.Series) -> None:
    risk = risk_label(safe_float(row.get("volatility"), 0.5))
    risk_class = {
        "Baixo": "badge-risk-low",
        "Médio": "badge-risk-med",
        "Alto": "badge-risk-high",
    }[risk]

    smart_money_badge = ""
    if bool(row.get("smart_money")):
        smart_money_badge = (
            f'<span class="badge badge-drop">Smart Money: -{safe_float(row.get("drop_percent")):.1f}%</span>'
        )

    st.markdown(
        f"""
        <div class="op-card">
            <div class="op-head">
                <div>
                    <div class="op-event">{row["event_name"]}</div>
                    <div class="op-kickoff">Início: {format_kickoff(row.get("commence_time"))}</div>
                </div>
                <div class="score-chip">Score {safe_float(row.get("score_botano")):.1f}</div>
            </div>
            <div class="badges">
                <span class="badge badge-market">{row["market_family"]}</span>
                <span class="badge badge-ev">EV {safe_float(row.get("ev_percent")):.2f}%</span>
                <span class="badge {risk_class}">Risco {risk}</span>
                {smart_money_badge}
                <span class="badge badge-context">{row.get("motivation_badge", "")}</span>
                <span class="badge badge-context">{row.get("taboo_badge", "")}</span>
            </div>
            <div style="font-size:16px;font-weight:900;margin-bottom:10px;">{row["selection"]}</div>
            <div class="mini-grid">
                <div class="mini-stat">
                    <div class="mini-label">Odd</div>
                    <div class="mini-value">{safe_float(row.get("best_odd")):.2f}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Prob. Justa</div>
                    <div class="mini-value">{to_percent(safe_float(row.get("fair_prob")))}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Liquidez</div>
                    <div class="mini-value">{to_percent(safe_float(row.get("liquidity")))}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Kelly</div>
                    <div class="mini-value">{to_percent(safe_float(row.get("kelly")))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        bookmaker = row.get("best_bookmaker", "Casa")
        link = row.get("bookmaker_link", "")

        if link:
            st.markdown(f"[🌐 Abrir {bookmaker}]({link})")
        else:
            st.button(f"🌐 Abrir {bookmaker}", key=f"open_{row.name}")

    with col2:
        if st.button("🎯 Apostar", key=f"bet_{row.name}"):
            st.session_state["selected_bet"] = row.to_dict()
            st.success("Aposta enviada para o simulador.")

def render_tripla_card(row: pd.Series, position: int) -> None:
    st.markdown(
        f"""
        <div class="tripla-card">
            <div style="font-size:12px;color:{MUTED_COLOR};margin-bottom:4px;">Seleção {position + 1}</div>
            <div style="font-size:16px;font-weight:900;">{row["event_name"]}</div>
            <div style="margin-top:6px;">{row["selection"]}</div>
            <div style="margin-top:8px;color:{MUTED_COLOR};font-size:13px;">
                {row["market_family"]} · Odd {safe_float(row["best_odd"]):.2f} · EV {safe_float(row["ev_percent"]):.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history_card(row: pd.Series) -> None:
    status = str(row.get("status", "pending")).lower()
    status_color = {
        "green": GREEN_COLOR,
        "red": RED_COLOR,
        "pending": YELLOW_COLOR,
    }.get(status, YELLOW_COLOR)

    st.markdown(
        f"""
        <div class="history-card">
            <div style="font-size:16px;font-weight:900;margin-bottom:6px;">{row.get("evento", "-")}</div>
            <div style="font-size:13px;color:{MUTED_COLOR};margin-bottom:8px;">
                {row.get("mercado", "-")} · {row.get("selecao", "-")}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:10px;">
                <span class="badge badge-market">Odd {safe_float(row.get("odd")):.2f}</span>
                <span class="badge badge-ev">EV {safe_float(row.get("ev_percent")):.2f}%</span>
                <span class="badge" style="background:rgba(255,255,255,0.06);color:#fff;border-color:rgba(255,255,255,0.12);">
                    Kelly {safe_float(row.get("kelly_stake")):.2f}%
                </span>
                <span class="badge" style="background:{status_color}22;color:{status_color};border-color:{status_color}44;">
                    Status {status.upper()}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("🎯 🔥 Filtros Sniper")

    league_name = st.selectbox(
        "Liga",
        list(SPORTS_MAP.keys()),
        index=0,
        key="league_selector_main"
    )

    region = st.selectbox(
        "Região das odds",
        ["eu", "uk", "us", "au"],
        index=0,
        key="region_selector_main"
    )

    ev_min = st.slider(
        "EV mínimo (%)",
        min_value=-2.0,
        max_value=20.0,
        value=1.0,
        step=0.5,
        key="ev_min_slider_main"
    )

    score_min = st.slider(
        "Score mínimo",
        min_value=0,
        max_value=100,
        value=58,
        step=1,
        key="score_min_slider_main"
    )

    selected_families = st.multiselect(
    "Mercados",
    ["1x2", "Escanteios", "Cartões"],
    default=["1x2", "Escanteios", "Cartões"],
)

    st.markdown("---")
    st.markdown("## 🔐 Integrações")
    odds_api_key = st.secrets.get("THE_ODDS_API_KEY", os.getenv("THE_ODDS_API_KEY", ""))
    if odds_api_key:
        st.success("The Odds API conectada")
    else:
        st.warning("Defina THE_ODDS_API_KEY em secrets ou variável de ambiente.")

    if get_supabase_client():
        st.success("Supabase conectado")
    else:
        st.info("Supabase opcional: configure SUPABASE_URL e SUPABASE_KEY.")


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">BOTANO+ Smart Betting Engine</div>
        <div class="hero-sub">Scanner profissional de valor esperado, leitura de contexto, gestão de stake e histórico real.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOAD
# ============================================================
sport_key = SPORTS_MAP[league_name]
with st.spinner("Varredura profissional do mercado em andamento..."):
    events_data = fetch_odds_data(sport_key, odds_api_key, region)
    ranked_df = build_ranked_dataframe(events_data)

api_warning = False
if not odds_api_key:
    api_warning = True
elif not events_data:
    api_warning = True

if api_warning:
    st.warning(
        "Nenhuma oportunidade encontrada agora. Verifique sua API, a liga escolhida ou aguarde atualização do mercado."
    )

if not ranked_df.empty:
    ranked_df = ranked_df[
        (ranked_df["ev_percent"] >= ev_min)
        & (ranked_df["score_botano"] >= score_min)
        & (ranked_df["market_family"].isin(selected_families))
    ].copy()
    ranked_df.sort_values(by=["score_botano", "ev_percent"], ascending=[False, False], inplace=True)
    ranked_df.reset_index(drop=True, inplace=True)

tripla_df = build_tripla_do_dia(ranked_df) if not ranked_df.empty else pd.DataFrame()
history_df = fetch_bet_history(limit=50)
BANKROLL_INICIAL = 1500.0
metrics = compute_dashboard_metrics(history_df, BANKROLL_INICIAL)
roi_df = build_roi_series(history_df, BANKROLL_INICIAL)


# ============================================================
# METRICS
# ============================================================
metric_cols = st.columns(4)
with metric_cols[0]:
    render_metric_card("Oportunidades Ativas", str(len(ranked_df)))
with metric_cols[1]:
    render_metric_card("Banca Atual", format_brl(metrics["bankroll"]))
with metric_cols[2]:
    render_metric_card("ROI Real", f"{metrics['roi']:.2f}%")
with metric_cols[3]:
    render_metric_card("Win Rate", f"{metrics['winrate']:.2f}%")


# ============================================================
# MAIN LAYOUT
# ============================================================
left_col, right_col = st.columns([1.45, 1.0], gap="large")

with left_col:
    st.markdown("## 🔥 Oportunidades com Valor")

    if ranked_df.empty:
        st.info("Nenhuma aposta passou pelos filtros sniper.")
    else:
        max_cards = min(len(ranked_df), 20)
        for idx in range(max_cards):
            row = ranked_df.iloc[idx]
            render_opportunity_card(row)
            if st.button(f"Apostar: {row['selection']}", key=f"bet_card_{idx}"):
                st.session_state["selected_bet"] = row.to_dict()
                st.success(f"Entrada enviada para o simulador: {row['selection']}")

with right_col:
    st.markdown("## 🧠 Gestão & Execução")
    selected_bet = st.session_state.get("selected_bet")
    if selected_bet is None and not ranked_df.empty:
        selected_bet = ranked_df.iloc[0].to_dict()
        st.session_state["selected_bet"] = selected_bet

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Simulador de Aposta")
    if selected_bet:
        st.markdown(
            f"**Entrada selecionada:** {selected_bet.get('event_name', '-')}  \n"
            f"**Mercado:** {selected_bet.get('market_name', '-')}  \n"
            f"**Seleção:** {selected_bet.get('selection', '-')}  \n"
            f"**Odd:** {safe_float(selected_bet.get('best_odd')):.2f}  \n"
            f"**EV:** {safe_float(selected_bet.get('ev_percent')):.2f}%  \n"
            f"**Kelly:** {to_percent(safe_float(selected_bet.get('kelly')))}  \n"
            f"**Confiança:** {confidence_label(safe_float(selected_bet.get('score_botano')))}"
        )

        suggested_stake = round(base_bankroll * safe_float(selected_bet.get("kelly"), 0.0), 2)
        if suggested_stake <= 0:
            suggested_stake = 25.0

        stake_value = st.number_input(
            "Valor da stake (R$)",
            min_value=1.0,
            value=float(suggested_stake),
            step=5.0,
        )

        dynamic_label = f"Apostar: {selected_bet.get('selection', 'Entrada')}"
        if st.button(dynamic_label, key="main_bet_action"):
            payload = {
                "evento": selected_bet.get("event_name"),
                "mercado": selected_bet.get("market_name"),
                "selecao": selected_bet.get("selection"),
                "odd": safe_float(selected_bet.get("best_odd")),
                "ev_percent": round(safe_float(selected_bet.get("ev_percent")), 2),
                "score_botano": round(safe_float(selected_bet.get("score_botano")), 2),
                "kelly_stake": round(safe_float(selected_bet.get("kelly")) * 100, 2),
                "status": "pending",
                "valor_apostado": float(stake_value),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "lucro_prejuizo": 0.0,
            }
            ok, message = insert_bet_record(payload)
            if ok:
                st.success(message)
                fetch_bet_history.clear()
            else:
                st.warning(message)
    else:
        st.info("Selecione uma oportunidade para alimentar o simulador.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### ⚖️ Calculadora de Dutching")
    dutch_mode = st.radio("Número de seleções", [2, 3], horizontal=True)
    dutch_bank = st.number_input("Banca para dutching (R$)", min_value=1.0, value=100.0, step=10.0)

    if dutch_mode == 2:
        col_a, col_b = st.columns(2)
        with col_a:
            odd_a = st.number_input("Odd A", min_value=1.01, value=2.10, step=0.01, key="dutch_a_2")
        with col_b:
            odd_b = st.number_input("Odd B", min_value=1.01, value=3.20, step=0.01, key="dutch_b_2")

        inv_sum = (1 / odd_a) + (1 / odd_b)
        stake_a = dutch_bank * ((1 / odd_a) / inv_sum)
        stake_b = dutch_bank * ((1 / odd_b) / inv_sum)
        retorno = stake_a * odd_a
        lucro = retorno - dutch_bank

        st.markdown(
            f"A: **{format_brl(stake_a)}** · B: **{format_brl(stake_b)}**  \n"
            f"Retorno uniforme: **{format_brl(retorno)}** · Lucro estimado: **{format_brl(lucro)}**"
        )
    else:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            odd_a = st.number_input("Odd A", min_value=1.01, value=2.10, step=0.01, key="dutch_a_3")
        with col_b:
            odd_b = st.number_input("Odd B", min_value=1.01, value=3.20, step=0.01, key="dutch_b_3")
        with col_c:
            odd_c = st.number_input("Odd C", min_value=1.01, value=4.50, step=0.01, key="dutch_c_3")

        inv_sum = (1 / odd_a) + (1 / odd_b) + (1 / odd_c)
        stake_a = dutch_bank * ((1 / odd_a) / inv_sum)
        stake_b = dutch_bank * ((1 / odd_b) / inv_sum)
        stake_c = dutch_bank * ((1 / odd_c) / inv_sum)
        retorno = stake_a * odd_a
        lucro = retorno - dutch_bank

        st.markdown(
            f"A: **{format_brl(stake_a)}** · B: **{format_brl(stake_b)}** · C: **{format_brl(stake_c)}**  \n"
            f"Retorno uniforme: **{format_brl(retorno)}** · Lucro estimado: **{format_brl(lucro)}**"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📈 ROI Real")
    if roi_df.empty:
        st.info("Sem dados suficientes para o gráfico de ROI.")
    else:
        st.line_chart(roi_df.set_index("Aposta"))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Tripla do Dia")
    if tripla_df.empty:
        st.info("A Tripla do Dia será gerada quando houver pelo menos 3 oportunidades elegíveis.")
    else:
        for pos, (_, row) in enumerate(tripla_df.iterrows()):
            render_tripla_card(row, pos)

        combined_odd = 1.0
        for odd in tripla_df["best_odd"].tolist():
            combined_odd *= safe_float(odd, 1.0)

        st.markdown(f"**Odd combinada estimada:** {combined_odd:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📘 Glossário Rápido"):
        st.markdown(
            "**EV (Expected Value):** mostra se a odd está pagando acima do que deveria pagar.  \n"
            "**Fair Probability:** probabilidade justa após remover a margem da casa.  \n"
            "**Kelly Criterion:** sugere quanto da banca apostar com base na vantagem matemática.  \n"
            "**Score Botano:** nota de 0 a 100 que mistura EV, liquidez e risco.  \n"
            "**Smart Money:** alerta visual quando a odd caiu bastante, indicando possível pressão de mercado."
        )


# ============================================================
# RANKING AS CARDS
# ============================================================

# RANKING AS CARDS
st.markdown("## 📋 Ranking das Melhores Apostas")

if ranked_df.empty:
    st.info("Sem ranking para exibir no momento.")
else:
    top_rank = min(len(ranked_df), 6)
    rank_columns = st.columns(2)

    for idx in range(top_rank):
        target_column = rank_columns[idx % 2]
        with target_column:
            render_opportunity_card(ranked_df.iloc[idx])


# ============================================================
# HISTORY
# ============================================================
st.markdown("## 🧾 Histórico Recente")
if history_df.empty:
    st.info("Ainda não há apostas simuladas registradas.")
else:
    history_show = history_df.copy()
    if "created_at" in history_show.columns:
        history_show["created_at"] = pd.to_datetime(history_show["created_at"], errors="coerce")
        history_show.sort_values(by="created_at", ascending=False, inplace=True)

    max_history = min(len(history_show), 8)
    for idx in range(max_history):
        render_history_card(history_show.iloc[idx])


st.markdown(
    '<div class="footer-note">Botano+ V5.1 · Scanner de valor com consenso de mercado, gestão por Kelly, leitura de liquidez, volatilidade e proteção contra falhas externas.</div>',
    unsafe_allow_html=True,
)






