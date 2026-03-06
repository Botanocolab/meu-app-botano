import os
from supabase import create_client
import requests
from datetime import datetime

# Busca as chaves direto do cofre do GitHub (as Secrets)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"

def buscar_jogos_do_dia():
    if not RAPIDAPI_KEY:
        print("Erro: RAPIDAPI_KEY não encontrada!")
        return []
        
    # Data de hoje formatada (YYYY-MM-DD)
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    # Buscando jogos do dia no mundo todo sem filtro de liga para garantir retorno
    querystring = {"date": hoje} 
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    print(f"Buscando jogos para a data: {hoje}...")
    response = requests.get(url, headers=headers, params=querystring)
    
    data = response.json()
    return data.get('response', [])

def salvar_no_supabase(jogos):
    if not SUPABASE_KEY:
        print("Erro: SUPABASE_KEY não encontrada!")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Pegamos apenas os 5 primeiros jogos para não sobrecarregar o banco no teste
    for jogo in jogos[:5]:
        nome_home = jogo['teams']['home']['name']
        nome_away = jogo['teams']['away']['name']
        evento = f"{nome_home} x {nome_away}"
        
        dados = {
            "evento": evento,
            "valor_investido": 0,
            "status": "pendente"
        }
        try:
            supabase.table("carteira_simulada").insert(dados).execute()
            print(f"Adicionado com sucesso: {evento}")
        except Exception as e:
            print(f"Erro ao inserir {evento}: {e}")

if __name__ == "__main__":
    jogos = buscar_jogos_do_dia()
    if jogos:
        print(f"Encontrados {len(jogos)} jogos. Salvando no banco...")
        salvar_no_supabase(jogos)
    else:
        print("Nenhum jogo encontrado para hoje.")
