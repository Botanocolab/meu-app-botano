st.divider()
st.subheader("🎯 Simulador de Apostas")

# Formulário para registrar a simulação
with st.form("simulador_form"):
    evento_escolhido = st.selectbox("Escolha o jogo:", df['evento'].unique())
    valor = st.number_input("Valor da aposta (R$):", min_value=1.0, step=1.0)
    odd = st.number_input("Odd escolhida:", min_value=1.0, step=0.1)
    
    btn_enviar = st.form_submit_button("Simular Aposta")

    if btn_enviar:
        # Dados para salvar no Supabase
        dados_simulacao = {
            "evento": evento_escolhido,
            "valor_apostado": valor,
            "odd": odd,
            "status": "pendente"
        }
        # Inserção no Supabase (precisa existir a tabela 'apostas_simuladas')
        supabase.table("apostas_simuladas").insert(dados_simulacao).execute()
        st.success(f"Simulação de R${valor} no jogo {evento_escolhido} registrada!")
