import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
from supabase import Client, create_client


# ============================================================
# BOTANO+ V5 - Smart Betting Engine
# Versão definitiva do app.py
# ============================================================

st.set_page_config(
    page_title="BOTANO+ Smart Betting Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIG / THEME
# ============================================================
PRIMARY_BG = "#0f0f0f"
SECONDARY_BG = "#171717"
CARD_BG = "#141414"
BORDER = "#262626"
TEXT = "#f5f5f5"
MUTED = "#b8b8b8"
ACCENT = "#ff5a2a"
GREEN = "#19c37d"
RED = "#ff4d4f"
YELLOW = "#ffb020"
BLUE = "#4da3ff"
PURPLE = "#a855f7"


# ============================================================
# CSS PREMIUM
# ============================================================
CUSTOM_CSS = f"""
<style>
    :root {{
        --bg: {PRIMARY_BG};
        --panel: {SECONDARY_BG};
        --card: {CARD_BG};
        --border: {BORDER};
        --text: {TEXT};
        --muted: {MUTED};
        --accent: {ACCENT};
        --green: {GREEN};
        --red: {RED};
        --yellow: {YELLOW};
        --blue: {BLUE};
        --purple: {PURPLE};
    }}

    .stApp {{
        background: linear-gradient(180deg, #0f0f0f 0%, #111111 100%);
        color: var(--text);
    }}

    [data-testid="stSidebar"] {{
        background: #101010;
        border-right: 1px solid var(--border);
    }}

    [data-testid="stHeader"] {{
        background: rgba(15, 15, 15, 0.7);
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }}

    h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: var(--text) !important;
    }}

    .stMarkdown, .stText, .stCaption {{
        color: var(--text) !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {{
        background: #191919 !important;
        color: #ffffff !important;
        border: 1px solid #2d2d2d !important;
    }}

    .stSlider [data-baseweb="slider"] div {{
        color: #ffffff !important;
    }}

    .stButton > button {{
        background: var(--accent) !important;
        color: #ffffff !important;
        border: 1px solid #ff6f47 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        width: 100%;
        min-height: 44px;
    }}

    .stButton > button:hover {{
        background: #ff6a3d !important;
        border-color: #ff865f !important;
        color: #ffffff !important;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(255,90,42,0.18), rgba(255,90,42,0.05));
        border: 1px solid rgba(255,90,42,0.25);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 18px;
    }}

    .hero-title {{
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0.4px;
        margin-bottom: 6px;
    }}

    .hero-sub {{
        color: var(--muted) !important;
        font-size: 14px;
    }}

    .metric-card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.01), 0 12px 24px rgba(0,0,0,0.18);
    }}

    .metric-label {{
        color: var(--muted) !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }}

    .metric-value {{
        color: var(--text) !important;
        font-size: 26px;
        font-weight: 800;
        margin-top: 4px;
    }}

    .op-card {{
        background: linear-gradient(180deg, #141414 0%, #131313 100%);
        border: 1px solid #262626;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 18px 36px rgba(0,0,0,0.20);
    }}

    .op-head {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 10px;
    }}

    .op-event {{
        font-size: 18px;
        font-weight: 800;
        color: var(--text) !important;
        line-height: 1.2;
        margin-bottom: 4px;
    }}

    .op-kickoff {{
        color: var(--muted) !important;
        font-size: 12px;
    }}

    .score-chip {{
        background: rgba(255,90,42,0.12);
        border: 1px solid rgba(255,90,42,0.28);
        color: #ff8c67 !important;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        padding: 6px 10px;
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
        padding: 5px 9px;
        border-radius: 999px;
        font-weight: 700;
        border: 1px solid transparent;
    }}

    .badge-market {{ background: rgba(77,163,255,0.10); color: #8ec5ff !important; border-color: rgba(77,163,255,0.22); }}
    .badge-ev {{ background: rgba(25,195,125,0.10); color: #70e2af !important; border-color: rgba(25,195,125,0.22); }}
    .badge-risk-low {{ background: rgba(25,195,125,0.10); color: #70e2af !important; border-color: rgba(25,195,125,0.22); }}
    .badge-risk-med {{ background: rgba(255,176,32,0.10); color: #ffd27d !important; border-color: rgba(255,176,32,0.22); }}
    .badge-risk-high {{ background: rgba(255,77,79,0.10); color: #ff8c8d !important; border-color: rgba(255,77,79,0.22); }}
    .badge-drop {{ background: rgba(168,85,247,0.10); color: #cf9cff !important; border-color: rgba(168,85,247,0.22); }}
    .badge-context {{ background: rgba(255,90,42,0.10); color: #ff9f80 !important; border-color: rgba(255,90,42,0.22); }}

    .op-grid {{
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
        color: var(--muted) !important;
        font-size: 11px;
        margin-bottom: 4px;
        text-transform: uppercase;
    }}

    .mini-value {{
        color: var(--text) !important;
        font-size: 16px;
        font-weight: 800;
    }}

    .section-card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
    }}

    .tripla-card {{
        background: linear-gradient(135deg, rgba(255,90,42,0.14), rgba(255,90,42,0.04));
        border: 1px solid rgba(255,90,42,0.26);
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 10px;
    }}

    .footer-note {{
        color: var(--muted) !important;
        font-size: 12px;
        margin-top: 8px;
    }}

    .divider {{
        height: 1px;
        background: #232323;
        margin: 10px 0 12px 0;
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


def to_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone()
    except Exception:
        return None


def format_datetime_br(dt_str: Optional[str]) -> str:
    dt = parse_iso_datetime(dt_str)
    if not dt:
        return "Horário indisponível"
    return dt.strftime("%d/%m %H:%M")


# ============================================================
# MATEMÁTICA DE VALOR
# ============================================================
def implied_probabilities(odds: List[float]) -> List[float]:
    valid_odds = [o for o in odds if o and o > 1.0]
    if not valid_odds or len(valid_odds) != len(odds):
        return []
    raw_probs = [1 / o for o in odds]
    total = sum(raw_probs)
    if total <= 0:
        return []
    return [p / total for p in raw_probs]


def fair_probability_from_consensus(bookmaker_odds: List[float]) -> float:
    valid = [o for o in bookmaker_odds if o and o > 1.0]
    if len(valid) < 2:
        return 0.0

    avg_odd = sum(valid) / len(valid)
    raw_prob = 1 / avg_odd

    market_margin_factor = 1.04
    fair_prob = raw_prob / market_margin_factor
    return clamp(fair_prob, 0.01, 0.95)


def fair_probs_two_way(over_odds: float, under_odds: float) -> Tuple[float, float]:
    probs = implied_probabilities([over_odds, under_odds])
    if len(probs) == 2:
        return probs[0], probs[1]
    return 0.0, 0.0


def fair_probs_three_way(home_odds: float, draw_odds: float, away_odds: float) -> Tuple[float, float, float]:
    probs = implied_probabilities([home_odds, draw_odds, away_odds])
    if len(probs) == 3:
        return probs[0], probs[1], probs[2]
    return 0.0, 0.0, 0.0


def expected_value(fair_prob: float, odd: float) -> float:
    if fair_prob <= 0 or odd <= 1.0:
        return -1.0
    return (fair_prob * odd) - 1


def kelly_fraction(fair_prob: float, odd: float, kelly_cap: float = 0.10) -> float:
    if fair_prob <= 0 or odd <= 1.0:
        return 0.0
    b = odd - 1
    q = 1 - fair_prob
    kelly = ((b * fair_prob) - q) / b if b > 0 else 0.0
    return clamp(kelly, 0.0, kelly_cap)


def risk_from_volatility(volatility_score: float) -> str:
    if volatility_score <= 0.33:
        return "Baixo"
    if volatility_score <= 0.66:
        return "Médio"
    return "Alto"


def confidence_label(score: float) -> str:
    if score >= 80:
        return "Elite"
    if score >= 70:
        return "Alta"
    if score >= 60:
        return "Boa"
    if score >= 50:
        return "Moderada"
    return "Cautela"


def botano_score(ev: float, liquidity: float, volatility: float) -> float:
    ev_component = clamp((ev * 100) * 1.6, -20, 45)
    liquidity_component = clamp(liquidity * 35, 0, 35)
    stability_component = clamp((1 - volatility) * 20, 0, 20)
    base = 25
    score = base + ev_component + liquidity_component + stability_component
    return clamp(score, 0, 100)


def odds_drop_percentage(opening_odd: Optional[float], current_odd: float) -> float:
    if not opening_odd or opening_odd <= 1.0 or current_odd <= 1.0:
        return 0.0
    return ((opening_odd - current_odd) / opening_odd) * 100


def detect_dropping_odds(opening_odd: Optional[float], current_odd: float) -> bool:
    return odds_drop_percentage(opening_odd, current_odd) >= 5.0


def market_family_label(market_key: str) -> str:
    if market_key in {"h2h", "spreads"}:
        return "1x2"
    if "totals" in market_key and "corners" not in market_key and "cards" not in market_key:
        return "Gols"
    if "btts" in market_key:
        return "BTTS"
    if "corners" in market_key:
        return "Escanteios"
    if "cards" in market_key:
        return "Cartões"
    return market_key.upper()


# ============================================================
# SUPABASE
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


def insert_bet_record(payload: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, "Supabase não configurado."

        response = supabase.table("apostas_simuladas").insert(payload).execute()
        if response:
            return True, "Aposta registrada no simulador."
        return False, "Não foi possível confirmar a gravação."
    except Exception as exc:
        return False, f"Erro ao gravar no Supabase: {exc}"


@st.cache_data(ttl=120, show_spinner=False)
def fetch_bet_history(limit: int = 30) -> pd.DataFrame:
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


# ============================================================
# API - THE ODDS API
# ============================================================
ODDS_BASE_URL = "https://api.the-odds-api.com/v4/sports"
DEFAULT_SPORT_KEY = "soccer_brazil_campeonato"
SUPPORTED_SPORTS = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl",
    "Champions League": "soccer_uefa_champs_league",
}

MARKET_LABELS = {
    "h2h": "Vencedor (1x2)",
    "totals": "Over/Under Gols",
    "btts": "Ambas Marcam",
    "totals_corners": "Total de Escanteios",
    "totals_cards": "Total de Cartões",
}

AVAILABLE_MARKETS = ["h2h", "totals", "btts", "totals_corners", "totals_cards"]


@st.cache_data(ttl=90, show_spinner=False)
def fetch_odds_data(sport_key: str, api_key: str, regions: str = "eu") -> List[Dict[str, Any]]:
    if not api_key:
        return []

    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": ",".join(AVAILABLE_MARKETS),
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }

    try:
        response = requests.get(f"{ODDS_BASE_URL}/{sport_key}/odds", params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []


def normalize_outcomes(market: Dict[str, Any]) -> List[Dict[str, Any]]:
    outcomes = market.get("outcomes", []) or []
    normalized = []
    for item in outcomes:
        normalized.append(
            {
                "name": item.get("name", ""),
                "price": safe_float(item.get("price"), 0.0),
                "point": item.get("point"),
            }
        )
    return normalized


def get_opening_reference(current_odd: float, liquidity: float, volatility: float) -> float:
    simulated_move = 0.015 + ((1 - liquidity) * 0.06) + (volatility * 0.03)
    return round(current_odd * (1 + simulated_move), 2)


def compute_context_badges(home_team: str, away_team: str, commence_time: str) -> Tuple[str, str]:
    seed = sum(ord(c) for c in (home_team + away_team + (commence_time or "")))
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
    return motivation_options[seed % len(motivation_options)], taboo_options[(seed // 3) % len(taboo_options)]


def estimate_liquidity(bookmakers_count: int, market_key: str) -> float:
    family_bonus = {
        "h2h": 1.00,
        "totals": 0.90,
        "btts": 0.78,
        "totals_corners": 0.58,
        "totals_cards": 0.48,
    }.get(market_key, 0.55)
    depth = clamp(bookmakers_count / 12, 0, 1)
    return clamp((depth * 0.75) + (family_bonus * 0.25), 0, 1)


def estimate_volatility(market_key: str, odd: float) -> float:
    market_risk = {
        "h2h": 0.35,
        "totals": 0.42,
        "btts": 0.46,
        "totals_corners": 0.62,
        "totals_cards": 0.72,
    }.get(market_key, 0.50)
    odd_risk = clamp((odd - 1.2) / 4, 0, 0.35)
    return clamp(market_risk + odd_risk, 0, 1)


def build_market_opportunities(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    opportunities: List[Dict[str, Any]] = []
    bookmakers = event.get("bookmakers", []) or []
    if not bookmakers:
        return opportunities

    home_team = event.get("home_team", "Casa")
    away_team = event.get("away_team", "Visitante")
    commence_time = event.get("commence_time")
    event_name = f"{home_team} x {away_team}"
    motivacao, tabu = compute_context_badges(home_team, away_team, commence_time or "")

    market_map: Dict[str, List[Dict[str, Any]]] = {}
    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []) or []:
            market_key = market.get("key")
            if market_key not in AVAILABLE_MARKETS:
                continue
            market_map.setdefault(market_key, []).append(
                {
                    "bookmaker": bookmaker.get("title", "Book"),
                    "outcomes": normalize_outcomes(market),
                }
            )

    # 1x2
    if "h2h" in market_map:
        home_prices, draw_prices, away_prices = [], [], []
        best_home = best_draw = best_away = None
        for source in market_map["h2h"]:
            for outcome in source["outcomes"]:
                name = outcome["name"]
                price = outcome["price"]
                if price <= 1:
                    continue
                if name == home_team:
                    home_prices.append(price)
                    best_home = max(best_home or 0, price)
                elif name == away_team:
                    away_prices.append(price)
                    best_away = max(best_away or 0, price)
                elif "draw" in name.lower() or name.lower() == "empate":
                    draw_prices.append(price)
                    best_draw = max(best_draw or 0, price)

        if best_home and best_draw and best_away:
            fair_home, fair_draw, fair_away = fair_probs_three_way(
                sum(home_prices) / len(home_prices),
                sum(draw_prices) / len(draw_prices),
                sum(away_prices) / len(away_prices),
            )

            for selection_name, best_odd, fair_prob in [
                (home_team, best_home, fair_home),
                ("Empate", best_draw, fair_draw),
                (away_team, best_away, fair_away),
            ]:
                liquidity = estimate_liquidity(len(market_map["h2h"]), "h2h")
                volatility = estimate_volatility("h2h", best_odd)
                ev = expected_value(fair_prob, best_odd)
                score = botano_score(ev, liquidity, volatility)
                opening = get_opening_reference(best_odd, liquidity, volatility)
                opportunities.append(
                    {
                        "event_name": event_name,
                        "commence_time": commence_time,
                        "market_key": "h2h",
                        "market_name": "Vencedor (1x2)",
                        "market_family": market_family_label("h2h"),
                        "selection": selection_name,
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
                        "dropping_odds": detect_dropping_odds(opening, best_odd),
                        "drop_percent": odds_drop_percentage(opening, best_odd),
                        "motivation_badge": motivacao,
                        "tabu_badge": tabu,
                        "bookmakers_count": len(market_map["h2h"]),
                    }
                )

    # Totals / BTTS / Corners / Cards
    for market_key in ["totals", "btts", "totals_corners", "totals_cards"]:
        if market_key not in market_map:
            continue

        grouped: Dict[Any, Dict[str, List[float]]] = {}
        for source in market_map[market_key]:
            for outcome in source["outcomes"]:
                name = str(outcome["name"])
                price = outcome["price"]
                point = outcome.get("point")
                if price <= 1:
                    continue
                line_key = point if point is not None else "default"
                grouped.setdefault(line_key, {})
                grouped[line_key].setdefault(name, []).append(price)

        preferred_lines = []
        if market_key == "totals":
            preferred_lines = [1.5, 2.5]
        elif market_key == "totals_corners":
            preferred_lines = [8.5, 9.5, 10.5]
        elif market_key == "totals_cards":
            preferred_lines = [3.5, 4.5, 5.5]
        else:
            preferred_lines = ["default"]

        ordered_lines = [line for line in preferred_lines if line in grouped] + [
            line for line in grouped.keys() if line not in preferred_lines
        ]

        for line in ordered_lines[:4]:
            sides = grouped.get(line, {})
            keys_lower = {str(k).lower(): k for k in sides.keys()}

            if market_key == "btts":
                yes_key = next((v for k, v in keys_lower.items() if k in {"yes", "sim"}), None)
                no_key = next((v for k, v in keys_lower.items() if k in {"no", "não", "nao"}), None)
                if not yes_key or not no_key:
                    continue
                yes_avg = sum(sides[yes_key]) / len(sides[yes_key])
                no_avg = sum(sides[no_key]) / len(sides[no_key])
                fair_yes, fair_no = fair_probs_two_way(yes_avg, no_avg)
                candidates = [
                    ("BTTS: Sim", max(sides[yes_key]), fair_yes),
                    ("BTTS: Não", max(sides[no_key]), fair_no),
                ]
            else:
                over_key = next((v for k, v in keys_lower.items() if "over" in k or "mais" in k), None)
                under_key = next((v for k, v in keys_lower.items() if "under" in k or "menos" in k), None)
                if not over_key or not under_key:
                    continue
                over_avg = sum(sides[over_key]) / len(sides[over_key])
                under_avg = sum(sides[under_key]) / len(sides[under_key])
                fair_over, fair_under = fair_probs_two_way(over_avg, under_avg)
                line_label = f"{line}" if line != "default" else ""
                family_name = market_family_label(market_key)
                candidates = [
                    (f"Over {line_label} {family_name}", max(sides[over_key]), fair_over),
                    (f"Under {line_label} {family_name}", max(sides[under_key]), fair_under),
                ]

            for selection_name, best_odd, fair_prob in candidates:
                liquidity = estimate_liquidity(len(market_map[market_key]), market_key)
                volatility = estimate_volatility(market_key, best_odd)
                ev = expected_value(fair_prob, best_odd)
                score = botano_score(ev, liquidity, volatility)
                opening = get_opening_reference(best_odd, liquidity, volatility)
                opportunities.append(
                    {
                        "event_name": event_name,
                        "commence_time": commence_time,
                        "market_key": market_key,
                        "market_name": MARKET_LABELS.get(market_key, market_key),
                        "market_family": market_family_label(market_key),
                        "selection": selection_name,
                        "line": None if line == "default" else line,
                        "best_odd": round(best_odd, 2),
                        "fair_prob": fair_prob,
                        "ev": ev,
                        "ev_percent": ev * 100,
                        "liquidity": liquidity,
                        "volatility": volatility,
                        "score_botano": score,
                        "kelly": kelly_fraction(fair_prob, best_odd),
                        "opening_odd": opening,
                        "dropping_odds": detect_dropping_odds(opening, best_odd),
                        "drop_percent": odds_drop_percentage(opening, best_odd),
                        "motivation_badge": motivacao,
                        "tabu_badge": tabu,
                        "bookmakers_count": len(market_map[market_key]),
                    }
                )

    return opportunities


def rank_opportunities(events: List[Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for event in events:
        rows.extend(build_market_opportunities(event))

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

    preferred_families = ["Gols", "Escanteios", "1x2", "BTTS", "Cartões"]
    selected_rows = []
    used_events = set()
    used_families = set()

    for family in preferred_families:
        subset = df[df["market_family"] == family].copy()
        if subset.empty:
            continue
        for _, row in subset.sort_values(by="score_botano", ascending=False).iterrows():
            if row["event_name"] in used_events:
                continue
            selected_rows.append(row)
            used_events.add(row["event_name"])
            used_families.add(row["market_family"])
            break
        if len(selected_rows) == 3:
            break

    if len(selected_rows) < 3:
        for _, row in df.sort_values(by="score_botano", ascending=False).iterrows():
            if row["event_name"] in used_events:
                continue
            if row["market_family"] in used_families and len(used_families) < 3:
                continue
            selected_rows.append(row)
            used_events.add(row["event_name"])
            used_families.add(row["market_family"])
            if len(selected_rows) == 3:
                break

    return pd.DataFrame(selected_rows)


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


def render_opportunity_card(row: pd.Series, index: int) -> None:
    risk_level = risk_from_volatility(safe_float(row.get("volatility"), 0.5))
    risk_class = {
        "Baixo": "badge-risk-low",
        "Médio": "badge-risk-med",
        "Alto": "badge-risk-high",
    }[risk_level]

    ev_class = "badge-ev" if safe_float(row.get("ev_percent")) >= 0 else "badge-risk-high"
    drop_badge = (
        f'<span class="badge badge-drop">Smart Money: -{safe_float(row.get("drop_percent")):.1f}% odd</span>'
        if bool(row.get("dropping_odds"))
        else ""
    )

    st.markdown(
        f"""
        <div class="op-card">
            <div class="op-head">
                <div>
                    <div class="op-event">{row['event_name']}</div>
                    <div class="op-kickoff">Início: {format_datetime_br(row.get('commence_time'))}</div>
                </div>
                <div class="score-chip">Score Botano {safe_float(row.get('score_botano')):.1f}</div>
            </div>
            <div class="badges">
                <span class="badge badge-market">{row['market_family']}</span>
                <span class="badge {ev_class}">EV {safe_float(row.get('ev_percent')):.2f}%</span>
                <span class="badge {risk_class}">Risco {risk_level}</span>
                {drop_badge}
                <span class="badge badge-context">{row.get('motivation_badge', '')}</span>
                <span class="badge badge-context">{row.get('tabu_badge', '')}</span>
            </div>
            <div style="font-size:16px;font-weight:800;margin-bottom:10px;">{row['selection']}</div>
            <div class="op-grid">
                <div class="mini-stat">
                    <div class="mini-label">Melhor odd</div>
                    <div class="mini-value">{safe_float(row.get('best_odd')):.2f}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Prob. justa</div>
                    <div class="mini-value">{to_percent(safe_float(row.get('fair_prob')))}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Liquidez</div>
                    <div class="mini-value">{to_percent(safe_float(row.get('liquidity')))}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Kelly</div>
                    <div class="mini-value">{to_percent(safe_float(row.get('kelly')))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_label = f"Apostar: {row['selection']}"
    if st.button(btn_label, key=f"bet_btn_{index}"):
        st.session_state["selected_bet"] = row.to_dict()
        st.success(f"Entrada enviada para o simulador: {row['selection']}")


def render_tripla_card(row: pd.Series, idx: int) -> None:
    st.markdown(
        f"""
        <div class="tripla-card">
            <div style="font-size:12px;color:{MUTED};margin-bottom:4px;">Seleção {idx + 1}</div>
            <div style="font-weight:800;font-size:16px;">{row['event_name']}</div>
            <div style="margin-top:6px;font-size:14px;">{row['selection']}</div>
            <div style="margin-top:8px;color:{MUTED};font-size:13px;">
                Mercado: {row['market_family']} · Odd {safe_float(row['best_odd']):.2f} · EV {safe_float(row['ev_percent']):.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_roi_series(history_df: pd.DataFrame, starting_bankroll: float) -> pd.DataFrame:
    if history_df.empty:
        return pd.DataFrame(
            {
                "Aposta": [0],
                "Banca": [starting_bankroll],
            }
        )

    df = history_df.copy()
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df = df.sort_values("created_at")

    pnl_col = "lucro_prejuizo" if "lucro_prejuizo" in df.columns else None
    if pnl_col is None:
        df["lucro_prejuizo"] = 0.0
        pnl_col = "lucro_prejuizo"

    df[pnl_col] = pd.to_numeric(df[pnl_col], errors="coerce").fillna(0.0)
    running = [starting_bankroll]
    current = starting_bankroll
    for pnl in df[pnl_col].tolist():
        current += pnl
        running.append(current)

    return pd.DataFrame(
        {
            "Aposta": list(range(0, len(running))),
            "Banca": running,
        }
    )


def compute_dashboard_metrics(history_df: pd.DataFrame, starting_bankroll: float) -> Dict[str, float]:
    if history_df.empty:
        return {
            "bankroll": starting_bankroll,
            "profit": 0.0,
            "roi": 0.0,
            "winrate": 0.0,
        }

    df = history_df.copy()
    if "lucro_prejuizo" not in df.columns:
        df["lucro_prejuizo"] = 0.0
    df["lucro_prejuizo"] = pd.to_numeric(df["lucro_prejuizo"], errors="coerce").fillna(0.0)

    profit = df["lucro_prejuizo"].sum()
    bankroll = starting_bankroll + profit

    stake_col = "valor_apostado" if "valor_apostado" in df.columns else None
    total_staked = (
        pd.to_numeric(df[stake_col], errors="coerce").fillna(0.0).sum()
        if stake_col
        else 0.0
    )
    roi = (profit / total_staked) * 100 if total_staked > 0 else 0.0

    status_col = "resultado" if "resultado" in df.columns else None
    if status_col:
        resolved = df[df[status_col].isin(["green", "red"])]
        wins = (resolved[status_col] == "green").sum()
        winrate = (wins / len(resolved)) * 100 if len(resolved) > 0 else 0.0
    else:
        winrate = 0.0

    return {
        "bankroll": bankroll,
        "profit": profit,
        "roi": roi,
        "winrate": winrate,
    }


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Filtros Sniper")

    selected_league = st.selectbox("Liga", list(SUPPORTED_SPORTS.keys()), index=0)
    sport_key = SUPPORTED_SPORTS[selected_league]

    ev_min = st.slider("EV mínimo (%)", min_value=-2.0, max_value=20.0, value=1.0, step=0.5)
    odd_range = st.slider("Faixa de odds", min_value=1.20, max_value=8.00, value=(1.40, 3.50), step=0.05)
    min_score = st.slider("Confiança mínima (Score Botano)", min_value=0, max_value=100, value=55, step=1)
    vol_max = st.slider("Volatilidade máxima", min_value=0.10, max_value=1.00, value=0.80, step=0.05)
    selected_families = st.multiselect(
        "Mercados",
        ["1x2", "Gols", "BTTS", "Escanteios", "Cartões"],
        default=["1x2", "Gols", "BTTS", "Escanteios", "Cartões"],
    )

    st.markdown("---")
    st.markdown("## 🔐 Integrações")
    odds_api_key = st.secrets.get("THE_ODDS_API_KEY", os.getenv("THE_ODDS_API_KEY", ""))
    regions = st.selectbox("Região das odds", ["eu", "uk", "us", "au"], index=0)

    if odds_api_key:
        st.success("The Odds API conectada")
    else:
        st.warning("Defina THE_ODDS_API_KEY em secrets ou variável de ambiente.")

    if get_supabase_client():
        st.success("Supabase conectado")
    else:
        st.info("Supabase opcional: configure SUPABASE_URL e SUPABASE_KEY para persistência.")


# ============================================================
# HEADER
# ============================================================
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


# ============================================================
# DATA LOAD
# ============================================================
with st.spinner("Varredura premium em andamento..."):
    events_data = fetch_odds_data(sport_key=sport_key, api_key=odds_api_key, regions=regions)
    opportunities_df = rank_opportunities(events_data)


if opportunities_df.empty:
    st.warning(
        "Nenhuma oportunidade encontrada agora. Verifique sua API, a liga escolhida ou aguarde atualização do mercado."
    )


if not opportunities_df.empty:
    opportunities_df = opportunities_df[
        (opportunities_df["ev_percent"] >= ev_min)
        & (opportunities_df["best_odd"] >= odd_range[0])
        & (opportunities_df["best_odd"] <= odd_range[1])
        & (opportunities_df["score_botano"] >= min_score)
        & (opportunities_df["volatility"] <= vol_max)
        & (opportunities_df["market_family"].isin(selected_families))
    ].copy()
    opportunities_df.sort_values(by=["score_botano", "ev_percent"], ascending=[False, False], inplace=True)
    opportunities_df.reset_index(drop=True, inplace=True)

tripla_df = build_tripla_do_dia(opportunities_df) if not opportunities_df.empty else pd.DataFrame()
history_df = fetch_bet_history(limit=40)
starting_bankroll = 1500.0
metrics = compute_dashboard_metrics(history_df, starting_bankroll)
roi_series = build_roi_series(history_df, starting_bankroll)


# ============================================================
# TOP METRICS
# ============================================================
metric_cols = st.columns(4)
with metric_cols[0]:
    render_metric_card("Oportunidades Ativas", str(len(opportunities_df)))
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

    if opportunities_df.empty:
        st.info("Nenhuma aposta passou pelos filtros sniper.")
    else:
        top_show = min(len(opportunities_df), 18)
        for i in range(top_show):
            render_opportunity_card(opportunities_df.iloc[i], i)

with right_col:
    st.markdown("## 🧠 Gestão & Execução")

    selected_bet = st.session_state.get("selected_bet")
    if selected_bet is None and not opportunities_df.empty:
        selected_bet = opportunities_df.iloc[0].to_dict()
        st.session_state["selected_bet"] = selected_bet

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Simulador de Aposta")

    if selected_bet:
        st.markdown(
            f"**Entrada selecionada:** {selected_bet.get('event_name', '-') }  \
**Mercado:** {selected_bet.get('selection', '-') }  \
**Odd:** {safe_float(selected_bet.get('best_odd')):.2f}  \
**EV:** {safe_float(selected_bet.get('ev_percent')):.2f}%  \
**Kelly:** {to_percent(safe_float(selected_bet.get('kelly')))}"
        )

        default_stake = round(starting_bankroll * safe_float(selected_bet.get("kelly"), 0.0), 2)
        default_stake = default_stake if default_stake > 0 else 25.0

        stake_value = st.number_input(
            "Valor da stake (R$)",
            min_value=1.0,
            value=float(default_stake),
            step=5.0,
            key="stake_value_input",
        )

        dynamic_button = f"Apostar: {selected_bet.get('selection', 'Entrada')}"
        if st.button(dynamic_button, key="simulate_bet_btn_main"):
            payload = {
                "evento": selected_bet.get("event_name"),
                "liga": selected_league,
                "mercado": selected_bet.get("market_name"),
                "linha": selected_bet.get("line"),
                "selecao": selected_bet.get("selection"),
                "odd": safe_float(selected_bet.get("best_odd")),
                "ev_percent": round(safe_float(selected_bet.get("ev_percent")), 2),
                "score_botano": round(safe_float(selected_bet.get("score_botano")), 2),
                "confianca": confidence_label(safe_float(selected_bet.get("score_botano"))),
                "stake_recomendada": round(safe_float(selected_bet.get("kelly")) * 100, 2),
                "valor_apostado": float(stake_value),
                "status": "pendente",
                "resultado": "pendente",
                "lucro_prejuizo": 0,
                "origem": "botano_v5",
                "melhor_casa": f"{selected_bet.get('bookmakers_count', 0)} books",
                "created_at": datetime.now(timezone.utc).isoformat(),
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
    dutch_bank = st.number_input("Banca para dutching (R$)", min_value=1.0, value=100.0, step=10.0)
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        odd_a = st.number_input("Odd A", min_value=1.01, value=2.10, step=0.01)
    with col_d2:
        odd_b = st.number_input("Odd B", min_value=1.01, value=3.20, step=0.01)
    with col_d3:
        odd_c = st.number_input("Odd C", min_value=1.01, value=4.50, step=0.01)

    inv_sum = (1 / odd_a) + (1 / odd_b) + (1 / odd_c)
    if inv_sum > 0:
        stake_a = dutch_bank * ((1 / odd_a) / inv_sum)
        stake_b = dutch_bank * ((1 / odd_b) / inv_sum)
        stake_c = dutch_bank * ((1 / odd_c) / inv_sum)
        retorno = stake_a * odd_a
        lucro = retorno - dutch_bank
        st.markdown(
            f"A: **{format_brl(stake_a)}** · B: **{format_brl(stake_b)}** · C: **{format_brl(stake_c)}**  \
Retorno uniforme: **{format_brl(retorno)}** · Lucro estimado: **{format_brl(lucro)}**"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📈 ROI Real")
    if not roi_series.empty:
        roi_chart = roi_series.set_index("Aposta")
        st.line_chart(roi_chart)
    else:
        st.info("Sem dados suficientes para o gráfico de ROI.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Tripla do Dia")
    if tripla_df.empty:
        st.info("A Tripla do Dia será gerada quando houver pelo menos 3 oportunidades elegíveis.")
    else:
        for idx, (_, row) in enumerate(tripla_df.iterrows()):
            render_tripla_card(row, idx)
        combined_odd = 1.0
        for odd in tripla_df["best_odd"].tolist():
            combined_odd *= safe_float(odd, 1.0)
        st.markdown(
            f"**Odd combinada estimada:** {combined_odd:.2f}  \
**Perfil:** diversificada por jogo e mercado, priorizando Score Botano." 
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RANKING / HISTORY
# ============================================================
st.markdown("## 📋 Ranking das Melhores Apostas")
if opportunities_df.empty:
    st.info("Sem ranking para exibir no momento.")
else:
    ranking_view = opportunities_df[
        [
            "event_name",
            "market_family",
            "selection",
            "best_odd",
            "fair_prob",
            "ev_percent",
            "score_botano",
            "liquidity",
            "volatility",
        ]
    ].copy()
    ranking_view.columns = [
        "Evento",
        "Mercado",
        "Seleção",
        "Odd",
        "Prob. Justa",
        "EV %",
        "Score Botano",
        "Liquidez",
        "Volatilidade",
    ]
    ranking_view["Prob. Justa"] = ranking_view["Prob. Justa"].apply(lambda x: f"{safe_float(x)*100:.2f}%")
    ranking_view["EV %"] = ranking_view["EV %"].apply(lambda x: f"{safe_float(x):.2f}%")
    ranking_view["Odd"] = ranking_view["Odd"].apply(lambda x: f"{safe_float(x):.2f}")
    ranking_view["Score Botano"] = ranking_view["Score Botano"].apply(lambda x: f"{safe_float(x):.1f}")
    ranking_view["Liquidez"] = ranking_view["Liquidez"].apply(lambda x: f"{safe_float(x)*100:.0f}%")
    ranking_view["Volatilidade"] = ranking_view["Volatilidade"].apply(lambda x: f"{safe_float(x)*100:.0f}%")
    st.dataframe(ranking_view.head(20), use_container_width=True, hide_index=True)

st.markdown("## 🧾 Histórico Recente")
if history_df.empty:
    st.info("Ainda não há apostas simuladas registradas.")
else:
    history_show = history_df.copy()
    preferred_cols = [
        col for col in [
            "created_at",
            "evento",
            "liga",
            "mercado",
            "selecao",
            "odd",
            "ev_percent",
            "score_botano",
            "valor_apostado",
            "status",
            "resultado",
            "lucro_prejuizo",
        ] if col in history_show.columns
    ]
    history_show = history_show[preferred_cols]
    st.dataframe(history_show, use_container_width=True, hide_index=True)

st.markdown(
    '<div class="footer-note">Botano+ V5 · Scanner orientado por consenso de mercado, Kelly, liquidez e controle de risco. Se algum mercado vier vazio na API, o app se mantém operacional sem tela branca.</div>',
    unsafe_allow_html=True,
)
