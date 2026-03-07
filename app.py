import streamlit as st

st.set_page_config(page_title="BOTANO+ Smart Betting Engine", layout="wide")

# =========================
# CONTROLE DE NAVEGAÇÃO
# =========================
if "pagina" not in st.session_state:
    st.session_state.pagina = "painel"


def ir_para_painel():
    st.session_state.pagina = "painel"


def ir_para_glossario():
    st.session_state.pagina = "glossario"


# =========================
# CSS GLOBAL
# =========================
st.markdown("""
<style>
.stApp{
    background: linear-gradient(180deg, #070707 0%, #111111 100%);
    color: white;
}

h1,h2,h3{
    color:#ff5a2a !important;
    font-weight:800 !important;
}

.card{
    background:#181818;
    border:1px solid #2c2c2c;
    border-left:4px solid #ff5a2a;
    border-radius:18px;
    padding:18px;
    margin-bottom:14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}

.titulo{
    color:#ff5a2a;
    font-size:22px;
    font-weight:800;
    margin-bottom:8px;
}

.texto{
    color:white;
    font-size:16px;
    line-height:1.7;
}

div.stButton > button {
    background: linear-gradient(135deg,#ff5a2a 0%,#ff7a1a 100%);
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    padding: 0.70rem 1.2rem !important;
    font-size: 16px !important;
}

div.stButton > button:hover {
    background: linear-gradient(135deg,#ff6a3d 0%,#ff8c33 100%);
    color: white !important;
}

div.stButton > button:focus:not(:active) {
    color: white !important;
    border: none !important;
    box-shadow: none !important;
}

.bloco-topo {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# PÁGINA PRINCIPAL
# =========================
def render_painel():
    st.title("BOTANO+ Smart Betting Engine")
    st.markdown("### Painel principal")

    st.write("Aqui fica o seu painel principal do BOTANO+.")
    st.write("Use este botão para abrir o glossário sem sair do app:")

    st.button("📘 Abrir Glossário", on_click=ir_para_glossario)

    st.markdown("---")

    # AQUI você cola o restante do conteúdo real do seu painel principal:
    # filtros
    # scanner
    # ranking
    # simulador
    # histórico
    #
    # Exemplo temporário:
    st.markdown("""
    <div class="card">
        <div class="titulo">Painel principal do BOTANO+</div>
        <div class="texto">
            Este espaço deve conter seu scanner de odds, ranking, simulador,
            histórico, métricas e gráficos.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# PÁGINA GLOSSÁRIO
# =========================
def render_glossario():
    st.title("📘 Glossário do BOTANO+")

    st.button("⬅ Voltar para o painel principal", on_click=ir_para_painel)

    st.markdown("""
    <div class="card">
        <div class="titulo">Odd</div>
        <div class="texto">
            É o número que mostra quanto a aposta paga.<br><br>
            Exemplo:<br>
            Odd 2.00 = se acertar, recebe o dobro.<br>
            Odd 3.00 = paga mais.<br><br>
            Forma simples de explicar: <b>é o preço da aposta</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">EV</div>
        <div class="texto">
            EV é a vantagem matemática da aposta.<br><br>
            Quando o EV está positivo, significa que a aposta parece boa pelas contas.<br><br>
            Forma simples de explicar: <b>é se a aposta vale a pena ou não</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Stake</div>
        <div class="texto">
            Stake é quanto do seu dinheiro o sistema recomenda apostar.<br><br>
            Exemplo:<br>
            Se sua banca é R$ 1.500 e a stake for 2%, a aposta sugerida é R$ 30.<br><br>
            Forma simples de explicar: <b>é quanto colocar na aposta com segurança</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Saldo Atual</div>
        <div class="texto">
            É quanto dinheiro você tem agora na simulação.<br><br>
            Forma simples de explicar: <b>é o dinheiro que está no cofrinho neste momento</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Lucro Total</div>
        <div class="texto">
            Mostra quanto você ganhou ou perdeu no total.<br><br>
            Forma simples de explicar: <b>é a conta geral do que entrou e saiu</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">ROI</div>
        <div class="texto">
            ROI mostra se o dinheiro apostado está dando retorno.<br><br>
            Forma simples de explicar: <b>é se o dinheiro investido está rendendo</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Winrate</div>
        <div class="texto">
            É a porcentagem de apostas ganhas.<br><br>
            Forma simples de explicar: <b>é a taxa de acerto</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Green</div>
        <div class="texto">
            Green quer dizer aposta ganha.<br><br>
            Forma simples de explicar: <b>foi acerto</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Red</div>
        <div class="texto">
            Red quer dizer aposta perdida.<br><br>
            Forma simples de explicar: <b>foi erro</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">CLV</div>
        <div class="texto">
            CLV compara a odd que você pegou com a odd que o mercado ficou depois.<br><br>
            Se você pegou uma odd melhor antes dela cair, isso é bom.<br><br>
            Forma simples de explicar: <b>é ver se você pegou um preço bom antes da mudança</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Score BOTANO</div>
        <div class="texto">
            É a nota geral que o sistema dá para a aposta.<br><br>
            Quanto maior o score, melhor a oportunidade parece.<br><br>
            Forma simples de explicar: <b>é a nota da aposta</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="titulo">Evolução da Banca</div>
        <div class="texto">
            É o gráfico que mostra se seu dinheiro está subindo, caindo ou parado.<br><br>
            Forma simples de explicar: <b>é o desenho do seu dinheiro ao longo do tempo</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# ROTEAMENTO
# =========================
if st.session_state.pagina == "painel":
    render_painel()
elif st.session_state.pagina == "glossario":
    render_glossario()
