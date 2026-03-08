import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
from supabase import Client, create_client


st.set_page_config(
    page_title="BOTANO+ Smart Betting Engine V5.1",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
    "totals",
    "btts",
    "totals_corners",
    "totals_cards",
]

MARKET_NAMES = {
    "h2h": "Vencedor (1x2)",
    "totals": "Over/Under Gols",
    "btts": "Ambas Marcam",
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


def render_tripla_card(row: pd.Series, position: int) -> None:
    st.markdown(
        f"""
        <div class="tripla-card">
            <div style="font-size:12px;color:{MUTED_COLOR};margin-bottom:4px;">Seleção {position + 1}</div>
            <div style="font-size:16px;font-weight:900;">{row["selection"]}</div>
            <div style="font-size:13px;color:{MUTED_COLOR};">{row["event_name"]}</div>
            <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:14px;font-weight:900;color:{ACCENT_COLOR};">Odd {safe_float(row.get("best_odd")):.2f}</span>
                <span style="font-size:11px;background:rgba(255,255,255,0.05);padding:3px 8px;border-radius:6px;">{row["market_family"]}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history_card(row: pd.Series) -> None:
    status = str(row.get("status", "Pendente")).strip().lower()
    color = GREEN_COLOR if status == "green" else (RED_COLOR if status == "red" else MUTED_COLOR)
    
    st.markdown(
        f"""
        <div class="history-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div style="font-size:15px;font-weight:900;">{row.get('selecao', 'N/A')}</div>
                <span style="font-size:10px;font-weight:800;text-transform:uppercase;color:{color};border:1px solid {color};padding:2px 8px;border-radius:999px;">
                    {status.upper()}
                </span>
            </div>
            <div style="font-size:12px;color:{MUTED_COLOR};margin-bottom:10px;">{row.get('evento', 'N/A')}</div>
            <div class="mini-grid">
                <div class="mini-stat">
                    <div class="mini-label">Valor</div>
                    <div class="mini-value">{format_brl(safe_float(row.get('valor_apostado')))}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Odd</div>
                    <div class="mini-value">{safe_float(row.get('odd_fechamento')):.2f}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Retorno</div>
                    <div class="mini-value" style="color:{color};">{format_brl(safe_float(row.get('lucro_prejuizo')))}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-label">Data</div>
                    <div class="mini-value">{row.get('created_at', '')[:10]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================
    # TAB OPORTUNIDADES
    # ========================================

    with tab_ops:

        selected_sports = st.multiselect(
            "Filtrar Ligas",
            list(SPORTS_MAP.keys()),
            default=list(SPORTS_MAP.keys())
        )

        all_events = []

        with st.spinner("Escaneando mercados..."):
            for sport_name in selected_sports:
                sport_key = SPORTS_MAP[sport_name]

                data = fetch_odds_data(
                    sport_key=sport_key,
                    api_key=api_key,
                    region=region,
                )

                if data:
                    all_events.extend(data)

        if not all_events:

            st.warning(
                "Nenhum dado encontrado. Verifique sua API Key ou as ligas selecionadas."
            )

        else:

            df_ops = build_ranked_dataframe(all_events)

            if df_ops.empty:

                st.info(
                    "Nenhuma oportunidade encontrada com os critérios atuais."
                )

            else:

                for _, row in df_ops.iterrows():

                    render_opportunity_card(row)

                    with st.expander(
                        f"Simular Aposta: {row['selection']} @ {safe_float(row.get('best_odd', 0)):.2f}"
                    ):

                        suggested_stake = (
                            metrics["bankroll"]
                            * safe_float(row.get("kelly", 0))
                            * kelly_pct
                        )

                        if suggested_stake <= 0:
                            suggested_stake = 25.0

                        stake = st.number_input(
                            "Valor da Aposta (R$)",
                            value=float(round(suggested_stake, 2)),
                            key=f"stake_{row['event_name']}_{row['selection']}"
                        )

                        if st.button(
                            "Confirmar Registro",
                            key=f"btn_{row['event_name']}_{row['selection']}"
                        ):

                            payload = {
                                "evento": row["event_name"],
                                "mercado": row["market_name"],
                                "selecao": row["selection"],
                                "odd_fechamento": safe_float(row.get("best_odd", 0)),
                                "valor_apostado": float(stake),
                                "status": "pendente",
                                "lucro_prejuizo": 0.0,
                                "created_at": datetime.now(timezone.utc).isoformat()
                            }

                            ok, msg = insert_bet_record(payload)

                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)