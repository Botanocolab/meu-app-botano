# Função para registrar no Supabase
def registrar_aposta_supabase(evento, selecao, mercado, odd, ev, score, valor):
    try:
        dados = {
            "evento": evento,
            "selecao": selecao,
            "mercado": mercado,
            "odd": float(odd),
            "ev_percent": float(ev),
            "score_botano": float(score),
            "valor_apostado": float(valor),
            "status": "pendente"
        }
        # Envia para a tabela 'apostas_simuladas' no Supabase
        supabase.table("apostas_simuladas").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")
        return False
