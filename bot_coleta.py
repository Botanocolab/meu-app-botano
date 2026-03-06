import os
from supabase import create_client
import requests

# Busca as chaves direto do cofre do GitHub (as Secrets)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"

def buscar_jogos_historicos():
    if not RAPIDAPI_KEY:
        print("Erro: RAPIDAPI_KEY não encontrada!")
        return []
        
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    # Buscando a liga 71 (Brasileirão) da temporada 2025 para garantir retorno de dados
    querystring = {"league": "71", "season": "2025"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    print("Buscando jogos da temporada 2025...")
    response = requests.get(url, headers=headers, params=querystring)
    
    data = response.json()
    return data.get('response', [])

def salvar_no_supabase(jogos):
    if not SUPABASE_KEY:
        print("Erro: SUPABASE_KEY não encontrada!")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Pegamos os primeiros 5 jogos da lista
    for jogo in jogos[:5]:
        nome_home = jogo['teams']['home']['name']
        nome_away = jogo['teams']['away']['name']
        evento = f"{nome_home} x {nome_away}"
        
        dados = {
            "evento": evento,
            "valor_investido": 1.0, # Valor fixo para teste
            "status": "pendente"
        }
        try:
            print(f"Tentando inserir: {evento}")
            supabase.table("carteira_simulada").insert(dados).execute()
            print(f"Adicionado com sucesso: {evento}")
        except Exception as e:
            print(f"ERRO AO INSERIR {evento}: {e}")

if __name__ == "__main__":
    jogos = buscar_jogos_historicos()
    if jogos:
        print(f"Encontrados {len(jogos)} jogos. Salvando no banco...")
        salvar_no_supabase(jogos)
    else:
        print("Nenhum jogo encontrado.")
