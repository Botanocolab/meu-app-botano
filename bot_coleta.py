import requests
import os
from supabase import create_client

# Configurações
SUPABASE_URL = "https://yovylzbqqulaiqfvugdg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdnlsemJxcXVsYWlxZnZ1Z2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3ODY2MjAsImV4cCI6MjA4ODM2MjYyMH0.7yRMk-vNTjDHSYRB0HUKaUbTP2mT3U3f8UnTsZl_ceE" # A chave que você já usa no app.py
RAPIDAPI_KEY = "fc9bfc38fcmshf7416ba4768fc22p17a086jsn93f3e730128b"    # A chave que você acabou de pegar

def buscar_jogos_ao_vivo():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"live":"all"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json().get('response', [])

def salvar_no_supabase(jogos):
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    for jogo in jogos[:3]:  # Vamos pegar só os 3 primeiros para testar
        evento = f"{jogo['teams']['home']['name']} x {jogo['teams']['away']['name']}"
        
        # Dados para salvar
        dados = {
            "evento": evento,
            "valor_investido": 0, # Valor padrão para novas entradas
            "status": "pendente"
        }
        
        # Insere se ainda não existir (simples)
        supabase.table("carteira_simulada").insert(dados).execute()
        print(f"Adicionado: {evento}")

# Execução
if __name__ == "__main__":
    print("Buscando jogos...")
    jogos_ao_vivo = buscar_jogos_ao_vivo()
    if jogos_ao_vivo:
        salvar_no_supabase(jogos_ao_vivo)
    else:
        print("Nenhum jogo ao vivo encontrado agora.")
