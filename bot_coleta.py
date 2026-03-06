def buscar_jogos_do_ano_atual():
    if not RAPIDAPI_KEY:
        print("Erro: RAPIDAPI_KEY não encontrada!")
        return []
        
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    # Focando na temporada 2026 (ano corrente)
    querystring = {"league": "71", "season": "2026"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    print("Buscando jogos da temporada 2026...")
    response = requests.get(url, headers=headers, params=querystring)
    
    data = response.json()
    return data.get('response', [])
