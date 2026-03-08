import os
from supabase import create_client
from dotenv import load_dotenv

# Carrega as chaves do seu arquivo .env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# USANDO APENAS COLUNAS QUE APARECEM NA SUA IMAGEM (2.PNG)
dados_teste = {
    "evento": "TESTE BOTANO V5",
    "time_casa": "BOTANO_TESTE",
    "margem": 99.9
}

try:
    # Enviando para a tabela 'apostas'
    response = supabase.table('apostas').insert(dados_teste).execute()
    print("✅ SUCESSO TOTAL! O dado entrou no banco.")
    print("Agora olhe o seu navegador (localhost:8501).")
except Exception as e:
    print(f"❌ Erro de coluna: {e}")