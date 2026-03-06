import os
from supabase import create_client
import requests

# Busca as chaves direto do cofre do GitHub (as Secrets)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"

def buscar_jogos_ao_vivo():
    if not RAPIDAPI_KEY:
        print("Erro: RAPIDAPI_KEY não encontrada!")
        return []
        
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"live":"all"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json().get('response', [])

def salvar_no_supabase(jogos):
    if not SUPABASE_KEY:
        print("Erro: SUPABASE_KEY não encontrada!")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    for jogo in jogos[:3]:
        evento = f"{jogo['teams']['home']['name']} x {jogo['teams']['away']['name']}"
        dados = {
            "evento": evento,
            "valor_investido": 0,
            "status": "pendente"
        }
        supabase.table("carteira_simulada").insert(dados).execute()
        print(f"Adicionado: {evento}")

if __name__ == "__main__":
    print("Buscando jogos...")
    jogos = buscar_jogos_ao_vivo()
    if jogos:
        salvar_no_supabase(jogos)
    else:
        print("Nenhum jogo ao vivo encontrado.")
