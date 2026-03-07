def render_glossario():
    st.title("📘 Glossário do BOTANO+")

    st.button("⬅ Voltar para o painel principal", on_click=voltar_painel)

    cards = [
        ("Odd", "É o número que mostra quanto a aposta paga.<br><br>"
                "Exemplo:<br>"
                "Odd 2.00 = se acertar, recebe o dobro.<br>"
                "Odd 3.00 = paga mais.<br><br>"
                "Forma simples de explicar: <b>é o preço da aposta</b>."),
        ("EV", "EV é a vantagem matemática da aposta.<br><br>"
               "Quando o EV está positivo, significa que a aposta parece boa pelas contas.<br><br>"
               "Forma simples de explicar: <b>é se a aposta vale a pena ou não</b>."),
        ("Stake", "Stake é quanto do seu dinheiro o sistema recomenda apostar.<br><br>"
                  "Exemplo:<br>"
                  "Se sua banca é R$ 1.500 e a stake for 2%, a aposta sugerida é R$ 30.<br><br>"
                  "Forma simples de explicar: <b>é quanto colocar na aposta com segurança</b>."),
        ("Saldo Atual", "É quanto dinheiro você tem agora na simulação.<br><br>"
                        "Forma simples de explicar: <b>é o dinheiro que está no cofrinho neste momento</b>."),
        ("Lucro Total", "Mostra quanto você ganhou ou perdeu no total.<br><br>"
                        "Forma simples de explicar: <b>é a conta geral do que entrou e saiu</b>."),
        ("ROI", "ROI mostra se o dinheiro apostado está dando retorno.<br><br>"
                "Forma simples de explicar: <b>é se o dinheiro investido está rendendo</b>."),
        ("Winrate", "É a porcentagem de apostas ganhas.<br><br>"
                    "Forma simples de explicar: <b>é a taxa de acerto</b>."),
        ("Green", "Green quer dizer aposta ganha.<br><br>"
                  "Forma simples de explicar: <b>foi acerto</b>."),
        ("Red", "Red quer dizer aposta perdida.<br><br>"
                "Forma simples de explicar: <b>foi erro</b>."),
        ("CLV", "CLV compara a odd que você pegou com a odd que o mercado ficou depois.<br><br>"
                "Se você pegou uma odd melhor antes dela cair, isso é bom.<br><br>"
                "Forma simples de explicar: <b>é ver se você pegou um preço bom antes da mudança</b>."),
        ("Score BOTANO", "É a nota geral que o sistema dá para a aposta.<br><br>"
                         "Quanto maior o score, melhor a oportunidade parece.<br><br>"
                         "Forma simples de explicar: <b>é a nota da aposta</b>."),
        ("Evolução da Banca", "É o gráfico que mostra se seu dinheiro está subindo, caindo ou parado.<br><br>"
                              "Forma simples de explicar: <b>é o desenho do seu dinheiro ao longo do tempo</b>."),
    ]

    for titulo, texto in cards:
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{titulo}</div>
            <div class="texto">{texto}</div>
        </div>
        """, unsafe_allow_html=True)
