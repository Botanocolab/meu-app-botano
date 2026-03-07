import streamlit as st

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="BOTANO+ Smart Betting Engine",
    layout="wide"
)

# =========================================================
# STATE
# =========================================================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "painel"

def abrir_glossario():
    st.session_state["pagina"] = "glossario"

def voltar_painel():
    st.session_state["pagina"] = "painel"

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.stApp{
    background: linear-gradient(180deg, #070707 0%, #111111 100%);
    color: white;
}

html, body, [class*="css"] {
    color: white;
}

h1, h2, h3 {
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
    line-height:1.6;
}

div.stButton > button {
    background: linear-gradient(135deg,#ff5a2a 0%,#ff7a1a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    padding: 0.75rem 1.2rem !important;
    width: 100%;
}

div.stButton > button:hover {
    color: white !important;
    border: none !important;
    opacity: 0.95;
}

label, .stSelectbox label, .stNumberInput label, .stSlider label {
    color: white !important;
    font-weight: 700 !important;
}

input, textarea {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# GLOSSÁRIO
# =========================================================
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

# =========================================================
# PAINEL
# =========================================================
def render_painel():
    col1, col2 = st.columns([8, 1])

    with col1:
        st.title("BOTANO+ Smart Betting Engine")

    with col2:
        st.write("")
        st.write("")
        st.button("📘 Glossário", on_click=abrir_glossario)

    st.markdown("### Scanner e painel principal")

    st.markdown("""
    <div class="card">
        <div class="titulo">Painel BOTANO+</div>
        <div class="texto">
            O glossário está funcionando corretamente.<br><br>
            Agora você pode recolocar aqui o conteúdo real do sistema:
            scanner, ranking, simulador, histórico, métricas e gráfico da banca.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ROTEAMENTO
# =========================================================
try:
    if st.session_state["pagina"] == "glossario":
        render_glossario()
    else:
        render_painel()

except Exception as e:
    st.error("O app encontrou um erro ao renderizar.")
    st.code(str(e))
