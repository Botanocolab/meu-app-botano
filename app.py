O que estava acontecendo na prática
Caso 1 — sucesso

Retornava algo assim:

DataFrame(...)
Caso 2 — erro

Retornava algo assim:

(DataFrame(...), "Erro API: 404")

Então esta linha quebrava:

df, erro = buscar_odds(ligas[liga_nome])

Porque o formato mudava conforme a resposta.

Seu bloco corrigido

Substitua somente esta parte:

@st.cache_data(ttl=60)
def buscar_odds(liga):
    api_key = st.secrets.get("ODDS_API_KEY")
    if not api_key: return pd.DataFrame(), "Chave da API não encontrada."
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        r = requests.get(url, params=params, timeout=10)
        return pd.DataFrame(r.json()) if r.status_code == 200 else (pd.DataFrame(), f"Erro API: {r.status_code}")
    except Exception as e: return pd.DataFrame(), f"Erro: {str(e)}"

por isto:

@st.cache_data(ttl=60)
def buscar_odds(liga):
    api_key = st.secrets.get("ODDS_API_KEY")

    if not api_key:
        return pd.DataFrame(), "Chave da API não encontrada."

    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json()
            return pd.DataFrame(data), None

        try:
            erro_api = r.json()
        except Exception:
            erro_api = r.text

        return pd.DataFrame(), f"Erro API {r.status_code}: {erro_api}"

    except Exception as e:
        return pd.DataFrame(), f"Erro: {str(e)}"
Melhoria extra que recomendo

No simulador manual, você pode evitar erro futuro se checar também as colunas:

if not df.empty and "home_team" in df.columns and "away_team" in df.columns:

em vez de apenas:

if not df.empty:
Outro ponto que vale ajustar

Na sua função extrair_oportunidades, hoje o EV está fixo:

"ev_%": 5.5

Então o painel ainda está mais visual do que inteligente.
Funciona para teste, mas não é uma oportunidade real calculada. Para agora tudo bem, mas depois precisamos trocar isso pela lógica real.

Resumo
Erro real

A função buscar_odds() retorna:

às vezes 1 valor

às vezes 2 valores

Correção

Fazer ela retornar sempre:

return df, erro

Depois dessa troca, esse ValueError deve sumir.
Me manda o próximo print depois de aplicar essa correção que eu sigo com vocês no próximo ajuste.
