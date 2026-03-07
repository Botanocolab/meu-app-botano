import math
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
import streamlit as st
from supabase import create_client

# =====================================
# CONFIGURAÇÃO INICIAL
# =====================================
st.set_page_config(
    page_title="BOTANO+ | Smart Betting Engine V5",
    layout="wide"
)

# =====================================
# SECRETS / CONEXÕES
# =====================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
except Exception:
    st.error(
        "Secrets não encontrados. Configure SUPABASE_URL, SUPABASE_KEY e ODDS_API_KEY no Streamlit."
    )
    st.stop()

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro ao conectar no Supabase: {e}")
    st.stop()

# =====================================
# SESSION STATE
# =====================================
if "selecionado_evento" not in st.session_state:
    st.session_state["selecionado_evento"] = ""

if "selecionado_mercado" not in st.session_state:
    st.session_state["selecionado_mercado"] = ""

if "selecionado_odd" not in st.session_state:
    st.session_state["selecionado_odd"] = 1.50

if "selecionado_ev" not in st.session_state:
    st.session_state["selecionado_ev"] = 0.0

if "selecionado_score" not in st.session_state:
    st.session_state["selecionado_score"] = 0.0

if "selecionado_stake" not in st.session_state:
    st.session_state["selecionado_stake"] = 0.5

# =====================================
# CSS
# =====================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0b0b0c 0%, #151515 100%);
        color: #ffffff;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #ff5a2a !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }

    .botano-title-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }

    .botano-subtitle {
        color: #d0d0d0;
        font-size: 18px;
        font-weight: 400;
    }

    .botano-card {
        background: linear-gradient(180deg, #1a1a1a 0%, #171717 100%);
        border: 1px solid #2f2f2f;
        border-left: 4px solid #ff5a2a;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.32);
    }

    .botano-titulo {
        color: #ff5a2a;
        font-size: 1.18rem;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .botano-metric {
        font-size: 0.95rem;
        color: #d0d0d0;
        margin-bottom: 6px;
        line-height: 1.45;
    }

    .botano-strong {
        color: #ffffff;
        font-weight: 700;
    }

    .side-card {
        background: linear-gradient(180deg, #171717 0%, #131313 100%);
        border: 1px solid #292929;
        border-radius: 18px;
        padding: 18px;
        margin-top: 14px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
    }

    .side-label {
        color: #b8b8b8;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .side-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        line-height: 1;
    }

    .badge-alta {
        color: #7CFFB2;
        font-weight: 800;
    }

    .badge-moderada {
        color: #FFD166;
        font-weight: 800;
    }

    .badge-baixa {
        color: #FF8FA3;
        font-weight: 800;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff5a2a 0%, #ff7a1a 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        width: 100% !important;
        font-weight: 800 !important;
        border: none !important;
        padding: 0.72rem 1rem !important;
        box-shadow: 0 8px 20px rgba(255, 90, 42, 0.20);
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

    div[data-testid="stNumberInput"] input {
        background-color: #232323 !important;
        color: white !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }

    .debug-box {
        background: #111111;
        border: 1px solid #2d2d2d;
        border-radius: 14px;
        padding: 14px;
        color: #d8d8d8;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown("""
<div class="botano-title-wrap">
    <h1 style="margin:0;">⚡ BOTANO+</h1>
    <div class="botano-subtitle">Smart Betting Engine V5</div>
</div>
""", unsafe_allow_html=True)

# =====================================
# MAPEAMENTO DE LIGAS
# =====================================
ligas = {
    "Brasileirão Série A": "soccer_brazil_campeonato",
    "Premier League": "soccer_epl",
    "Champions League": "soccer_uefa_champs_league"
}

# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def formatar_decimal_br(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def badge_confianca(confianca: str) -> str:
    if confianca == "Alta":
        return '<span class="badge-alta">Alta</span>'
    if confianca == "Moderada":
        return '<span class="badge-moderada">Moderada</span>'
    return '<span class="badge-baixa">Baixa</span>'


def formatar_data_iso(data_iso: str) -> str:
    if not data_iso:
        return "N/D"
    try:
        dt = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m %H:%M UTC")
    except Exception:
        return data_iso


def construir_mercado(outcome: str) -> str:
    if not outcome:
        return "Seleção"
    if outcome.lower() in ["draw", "empate"]:
        return "Empate"
    return f"Vitória do {outcome}"


def calcular_score_botano(ev_percent: float, fair_prob_percent: float, best_odd: float) -> float:
    score = (ev_percent * 8) + (fair_prob_percent * 0.3) - (best_odd * 1.2)
    return round(score, 2)


def calcular_stake_recomendada(ev_percent: float) -> tuple[float, str]:
    if ev_percent >= 10:
        return 3.0, "Alta"
    if ev_percent >= 7:
        return 2.0, "Alta"
    if ev_percent >= 4:
        return 1.0, "Moderada"
    return 0.5, "Baixa"

# =====================================
# API DE ODDS
# =====================================
@st.cache_data(ttl=60)
def buscar_odds(liga: str) -> tuple[pd.DataFrame, str | None, Any]:
    """
    Busca odds na The Odds API v4.
    Retorna:
    - dataframe bruto
    - mensagem de erro ou None
    - json bruto para debug
    """
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    try:
        response = requests.get(url, params=params, timeout=20)

        if response.status_code == 200:
            data = response.json()

            if not isinstance(data, list):
                return pd.DataFrame(), "Resposta inesperada da API.", data

            if len(data) == 0:
                return (
                    pd.DataFrame(),
                    "API respondeu, mas não existem jogos disponíveis no momento para essa liga.",
                    data
                )

            return pd.DataFrame(data), None, data

        try:
            erro_json = response.json()
        except Exception:
            erro_json = response.text

        return pd.DataFrame(), f"Erro API {response.status_code}: {erro_json}", erro_json

    except requests.exceptions.RequestException as exc:
        return pd.DataFrame(), f"Erro de conexão com a API: {exc}", None

# =====================================
# SCANNER BOTANO+
# =====================================
def extrair_oportunidades_reais(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai oportunidades reais a partir do retorno da Odds API.
    Estratégia:
    - pega odds h2h de vários bookmakers
    - calcula probabilidade implícita por casa
    - normaliza para remover margem
    - calcula fair probability média
    - pega a melhor odd disponível no mercado
    - calcula EV
    """
    oportunidades: list[dict[str, Any]] = []

    if df.empty or "bookmakers" not in df.columns:
        return pd.DataFrame()

    for _, row in df.iterrows():
        home_team = row.get("home_team")
        away_team = row.get("away_team")
        commence_time = row.get("commence_time")
        sport_key = row.get("sport_key")
        bookmakers = row.get("bookmakers", [])

        if not bookmakers:
            continue

        probabilidades_normalizadas_por_book: list[dict[str, float]] = []
        melhores_odds: dict[str, float] = {}
        lista_odds_por_outcome: dict[str, list[float]] = {}
        melhor_bookmaker_por_outcome: dict[str, str] = {}

        for bookmaker in bookmakers:
            book_title = bookmaker.get("title", bookmaker.get("key", "Bookmaker"))
            markets = bookmaker.get("markets", [])

            for market in markets:
                if market.get("key") != "h2h":
                    continue

                outcomes = market.get("outcomes", [])
                if not outcomes:
                    continue

                raw_probs = []
                nomes = []

                for outcome in outcomes:
                    nome = outcome.get("name")
                    price = outcome.get("price")

                    if nome and isinstance(price, (int, float)) and price > 1:
                        nomes.append(nome)
                        raw_probs.append(1 / price)
                        lista_odds_por_outcome.setdefault(nome, []).append(float(price))

                        if nome not in melhores_odds or float(price) > melhores_odds[nome]:
                            melhores_odds[nome] = float(price)
                            melhor_bookmaker_por_outcome[nome] = book_title

                soma = sum(raw_probs)
                if soma > 0 and nomes:
                    probs_norm = {
                        nomes[i]: raw_probs[i] / soma
                        for i in range(len(nomes))
                    }
                    probabilidades_normalizadas_por_book.append(probs_norm)

        if not probabilidades_normalizadas_por_book:
            continue

        todos_outcomes = set()
        for probs in probabilidades_normalizadas_por_book:
            todos_outcomes.update(probs.keys())

        for outcome in todos_outcomes:
            probs_outcome = [
                probs[outcome]
                for probs in probabilidades_normalizadas_por_book
                if outcome in probs
            ]

            if not probs_outcome:
                continue

            fair_prob = sum(probs_outcome) / len(probs_outcome)
            fair_prob_percent = round(fair_prob * 100, 2)

            best_odd = melhores_odds.get(outcome)
            if not best_odd:
                continue

            odds_lista = lista_odds_por_outcome.get(outcome, [best_odd])
            avg_odd = round(sum(odds_lista) / len(odds_lista), 2)

            ev = (fair_prob * best_odd) - 1
            ev_percent = round(ev * 100, 2)

            if best_odd < 1.40:
                continue

            score_botano = calcular_score_botano(
                ev_percent=ev_percent,
                fair_prob_percent=fair_prob_percent,
                best_odd=best_odd
            )

            stake_pct, confianca = calcular_stake_recomendada(ev_percent)

            oportunidades.append({
                "liga_api": sport_key,
                "evento": f"{home_team} x {away_team}",
                "selecao": outcome,
                "mercado": construir_mercado(outcome),
                "best_odd": round(best_odd, 2),
                "avg_odd": avg_odd,
                "fair_prob_percent": fair_prob_percent,
                "ev_percent": ev_percent,
                "score_botano": score_botano,
                "stake_pct": stake_pct,
                "confianca": confianca,
                "inicio": commence_time,
                "melhor_casa": melhor_bookmaker_por_outcome.get(outcome, "N/D")
            })

    if not oportunidades:
        return pd.DataFrame()

    df_op = pd.DataFrame(oportunidades)

    df_op = df_op.sort_values(
        by=["ev_percent", "score_botano", "fair_prob_percent"],
        ascending=False
    ).reset_index(drop=True)

    return df_op

# =====================================
# SUPABASE
# =====================================
def registrar_aposta_supabase(
    liga_exibicao: str,
    oportunidade: dict[str, Any],
    valor_apostado: float,
    origem: str = "auto"
) -> tuple[bool, str]:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "liga": liga_exibicao,
        "evento": oportunidade["evento"],
        "mercado": oportunidade["mercado"],
        "selecao": oportunidade["selecao"],
        "odd": float(oportunidade["best_odd"]),
        "odd_media": float(oportunidade["avg_odd"]),
        "ev_percent": float(oportunidade["ev_percent"]),
        "score_botano": float(oportunidade["score_botano"]),
        "confianca": oportunidade["confianca"],
        "stake_recomendada": float(oportunidade["stake_pct"]),
        "valor_apostado": float(valor_apostado),
        "status": "pendente",
        "resultado": None,
        "lucro_prejuizo": None,
        "origem": origem,
        "melhor_casa": oportunidade["melhor_casa"]
    }

    try:
        supabase.table("apostas_simuladas").insert(payload).execute()
        return True, "Aposta registrada com sucesso no histórico."
    except Exception as exc:
        return False, f"Não foi possível gravar no Supabase: {exc}"


def registrar_aposta_manual_supabase(
    liga_exibicao: str,
    evento: str,
    odd: float,
    valor_apostado: float
) -> tuple[bool, str]:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "liga": liga_exibicao,
        "evento": evento,
        "mercado": "Manual",
        "selecao": "Manual",
        "odd": float(odd),
        "odd_media": None,
        "ev_percent": None,
        "score_botano": None,
        "confianca": None,
        "stake_recomendada": None,
        "valor_apostado": float(valor_apostado),
        "status": "pendente",
        "resultado": None,
        "lucro_prejuizo": None,
        "origem": "manual",
        "melhor_casa": None
    }

    try:
        supabase.table("apostas_simuladas").insert(payload).execute()
        return True, "Aposta manual registrada com sucesso."
    except Exception as exc:
        return False, f"Não foi possível gravar aposta manual: {exc}"


def carregar_historico_supabase() -> pd.DataFrame:
    try:
        resp = (
            supabase
            .table("apostas_simuladas")
            .select("*")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )
        data = resp.data if resp.data else []
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

# =====================================
# MÉTRICAS HISTÓRICO
# =====================================
def calcular_metricas_historico(df_hist: pd.DataFrame) -> dict[str, float]:
    if df_hist.empty:
        return {
            "total_apostas": 0,
            "total_apostado": 0.0,
            "lucro_total": 0.0,
            "roi": 0.0,
            "win_rate": 0.0
        }

    total_apostas = len(df_hist)
    total_apostado = (
        float(df_hist["valor_apostado"].fillna(0).sum())
        if "valor_apostado" in df_hist.columns else 0.0
    )
    lucro_total = (
        float(df_hist["lucro_prejuizo"].fillna(0).sum())
        if "lucro_prejuizo" in df_hist.columns else 0.0
    )

    if "resultado" in df_hist.columns:
        greens = len(df_hist[df_hist["resultado"] == "green"])
        decididas = len(df_hist[df_hist["resultado"].isin(["green", "red", "void"])])
    else:
        greens = 0
        decididas = 0

    roi = (lucro_total / total_apostado * 100) if total_apostado > 0 else 0.0
    win_rate = (greens / decididas * 100) if decididas > 0 else 0.0

    return {
        "total_apostas": total_apostas,
        "total_apostado": round(total_apostado, 2),
        "lucro_total": round(lucro_total, 2),
        "roi": round(roi, 2),
        "win_rate": round(win_rate, 2)
    }

# =====================================
# FILTROS
# =====================================
liga_nome = st.selectbox("Escolha a Liga:", list(ligas.keys()))
liga_api = ligas[liga_nome]

f1, f2, f3 = st.columns(3)

with f1:
    filtro_ev_min = st.number_input("EV mínimo (%)", value=4.0, min_value=0.0, step=0.5)

with f2:
    filtro_odd_min = st.number_input("Odd mínima", value=1.60, min_value=1.01, step=0.05)

with f3:
    filtro_odd_max = st.number_input("Odd máxima", value=3.50, min_value=1.05, step=0.05)

# =====================================
# CARGA DE DADOS
# =====================================
df_odds, erro_api, debug_json = buscar_odds(liga_api)
df_oportunidades = extrair_oportunidades_reais(df_odds)
df_historico = carregar_historico_supabase()
metricas = calcular_metricas_historico(df_historico)

if not df_oportunidades.empty:
    df_scanner = df_oportunidades[
        (df_oportunidades["ev_percent"] >= filtro_ev_min) &
        (df_oportunidades["best_odd"] >= filtro_odd_min) &
        (df_oportunidades["best_odd"] <= filtro_odd_max)
    ].reset_index(drop=True)
else:
    df_scanner = pd.DataFrame()

# =====================================
# LAYOUT PRINCIPAL
# =====================================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Oportunidades com Valor")

    if erro_api:
        st.error(erro_api)
    elif df_scanner.empty:
        st.info("Nenhuma oportunidade encontrada com os filtros atuais.")
    else:
        top_oportunidades = df_scanner.head(12)

        for i, (_, op) in enumerate(top_oportunidades.iterrows()):
            st.markdown(f"""
            <div class="botano-card">
                <div class="botano-titulo">{op['evento']}</div>
                <div class="botano-metric"><span class="botano-strong">Início:</span> {formatar_data_iso(op['inicio'])}</div>
                <div class="botano-metric"><span class="botano-strong">Entrada recomendada:</span> {op['mercado']}</div>
                <div class="botano-metric"><span class="botano-strong">Seleção:</span> {op['selecao']}</div>
                <div class="botano-metric"><span class="botano-strong">Melhor odd:</span> {op['best_odd']} | <span class="botano-strong">Odd média:</span> {op['avg_odd']}</div>
                <div class="botano-metric"><span class="botano-strong">Fair Prob.:</span> {op['fair_prob_percent']}% | <span class="botano-strong">EV:</span> {op['ev_percent']}%</div>
                <div class="botano-metric"><span class="botano-strong">Score Botano:</span> {op['score_botano']} | <span class="botano-strong">Stake:</span> {op['stake_pct']}% da banca</div>
                <div class="botano-metric"><span class="botano-strong">Melhor casa:</span> {op['melhor_casa']} | <span class="botano-strong">Confiança:</span> {badge_confianca(op['confianca'])}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    f"Apostar em: {op['mercado']} | Odd {op['best_odd']}",
                    key=f"apostar_{i}"
                ):
                    valor_sugerido = round(100 * (float(op["stake_pct"]) / 100), 2)

                    ok, msg = registrar_aposta_supabase(
                        liga_exibicao=liga_nome,
                        oportunidade=op.to_dict(),
                        valor_apostado=valor_sugerido,
                        origem="auto"
                    )

                    if ok:
                        st.success(msg)
                        st.session_state["selecionado_evento"] = op["evento"]
                        st.session_state["selecionado_mercado"] = op["mercado"]
                        st.session_state["selecionado_odd"] = float(op["best_odd"])
                        st.session_state["selecionado_ev"] = float(op["ev_percent"])
                        st.session_state["selecionado_score"] = float(op["score_botano"])
                        st.session_state["selecionado_stake"] = float(op["stake_pct"])
                    else:
                        st.error(msg)

            with c2:
                if st.button(
                    f"Carregar no simulador #{i + 1}",
                    key=f"carregar_{i}"
                ):
                    st.session_state["selecionado_evento"] = op["evento"]
                    st.session_state["selecionado_mercado"] = op["mercado"]
                    st.session_state["selecionado_odd"] = float(op["best_odd"])
                    st.session_state["selecionado_ev"] = float(op["ev_percent"])
                    st.session_state["selecionado_score"] = float(op["score_botano"])
                    st.session_state["selecionado_stake"] = float(op["stake_pct"])
                    st.success(f"Entrada carregada: {op['mercado']}")

with col_right:
    st.subheader("🎯 Simulador & Gestão")

    evento_sim = st.session_state.get("selecionado_evento", "")
    mercado_sim = st.session_state.get("selecionado_mercado", "")
    odd_sim = float(st.session_state.get("selecionado_odd", 1.50))
    ev_sim = float(st.session_state.get("selecionado_ev", 0.0))
    score_sim = float(st.session_state.get("selecionado_score", 0.0))
    stake_sim = float(st.session_state.get("selecionado_stake", 0.5))

    if evento_sim:
        st.markdown(f"""
        <div class="side-card">
            <div class="side-label">Entrada carregada</div>
            <div class="botano-metric"><span class="botano-strong">Evento:</span> {evento_sim}</div>
            <div class="botano-metric"><span class="botano-strong">Mercado:</span> {mercado_sim}</div>
            <div class="botano-metric"><span class="botano-strong">EV:</span> {ev_sim}%</div>
            <div class="botano-metric"><span class="botano-strong">Score:</span> {score_sim}</div>
            <div class="botano-metric"><span class="botano-strong">Stake sugerida:</span> {stake_sim}% da banca</div>
        </div>
        """, unsafe_allow_html=True)

    with st.form("sim_form"):
        valor = st.number_input("Valor (R$):", value=10.0, min_value=0.0, step=5.0)
        odd = st.number_input("Odd:", value=odd_sim, min_value=1.01, step=0.01)

        retorno_bruto = round(valor * odd, 2)
        lucro_liquido = round(retorno_bruto - valor, 2)

        st.markdown(f"""
        <div class="side-card">
            <div class="side-label">Retorno Bruto</div>
            <div class="side-value">R$ {formatar_decimal_br(retorno_bruto)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="side-card">
            <div class="side-label">Lucro Líquido</div>
            <div class="side-value">R$ {formatar_decimal_br(lucro_liquido)}</div>
        </div>
        """, unsafe_allow_html=True)

        submit_manual = st.form_submit_button("Registrar Aposta Manual")

        if submit_manual:
            nome_evento = evento_sim if evento_sim else "Aposta manual"
            ok, msg = registrar_aposta_manual_supabase(
                liga_exibicao=liga_nome,
                evento=nome_evento,
                odd=odd,
                valor_apostado=valor
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown(f"""
    <div class="side-card">
        <div class="side-label">ROI Real</div>
        <div class="side-value">{metricas['roi']}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="side-card">
        <div class="side-label">Win Rate Real</div>
        <div class="side-value">{metricas['win_rate']}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="side-card">
        <div class="side-label">Lucro Total</div>
        <div class="side-value">R$ {formatar_decimal_br(metricas['lucro_total'])}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="side-card">
        <div class="side-label">Total de Apostas</div>
        <div class="side-value">{metricas['total_apostas']}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# HISTÓRICO
# =====================================
st.markdown("### 🧾 Histórico Real de Apostas")

if df_historico.empty:
    st.info("Nenhuma aposta registrada ainda no Supabase.")
else:
    colunas_preferidas = [
        "created_at",
        "liga",
        "evento",
        "mercado",
        "selecao",
        "odd",
        "odd_media",
        "ev_percent",
        "score_botano",
        "confianca",
        "stake_recomendada",
        "valor_apostado",
        "status",
        "resultado",
        "lucro_prejuizo",
        "origem",
        "melhor_casa"
    ]
    colunas_existentes = [c for c in colunas_preferidas if c in df_historico.columns]
    st.dataframe(df_historico[colunas_existentes], use_container_width=True)

# =====================================
# DEBUG
# =====================================
with st.expander("🛠 Debug da API"):
    st.markdown('<div class="debug-box">', unsafe_allow_html=True)
    st.write("Liga selecionada:", liga_nome)
    st.write("Liga API:", liga_api)
    st.write("Erro API:", erro_api)
    st.write("Qtd. jogos retornados:", 0 if df_odds.empty else len(df_odds))
    st.write("Colunas df_odds:", list(df_odds.columns) if not df_odds.empty else [])
    st.write("Preview df_odds:")
    st.dataframe(df_odds.head(3), use_container_width=True)
    st.write("Resposta bruta:")
    st.write(debug_json)
    st.markdown('</div>', unsafe_allow_html=True)
