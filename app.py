# Função de estilo para destacar odds
def destacar_odds(val):
    try:
        # Se a odd for maior ou igual a 2.00, retorna o estilo verde
        if float(val) >= 2.00:
            return 'background-color: #d4edda'
        return ''
    except:
        return ''

# ... (após carregar o df)

# Aplicando a formatação condicional
# Usamos map() que é a forma atualizada do applymap
tabela_estilizada = df[['evento', 'time_casa', 'odd_casa', 'created_at']].style.map(
    destacar_odds, subset=['odd_casa']
)

st.dataframe(tabela_estilizada, use_container_width=True)
