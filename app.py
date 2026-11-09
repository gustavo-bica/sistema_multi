import streamlit as st
from views import cadastros, encaminhamentos, relatorios

st.set_page_config(
    page_title="Sistema Multi",
    page_icon="🏫",
    layout="wide"
)

# Inicializa o estado da página ativa no session_state
if "pagina_ativa" not in st.session_state:
    st.session_state.pagina_ativa = "Cadastros"

# Injeção de CSS para estilizar a barra lateral e os botões do menu
st.markdown("""
    <style>
    /* 1. Reduz a largura da barra lateral (Sidebar) */
    [data-testid="stSidebar"] {
        min-width: 180px !important;
        max-width: 180px !important;
    }

    /* 2. Estilização completa dos botões para parecerem itens de menu clicáveis */
    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        background-color: transparent !important;
        color: inherit !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 8px 12px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }

    /* Efeito ao passar o mouse por cima do item do menu */
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(150, 150, 150, 0.15) !important;
    }

    /* Estilo para o item ativo/selecionado */
    [data-testid="stSidebar"] div.stButton > button:focus:not(:active),
    [data-testid="stSidebar"] div.stButton > button:active {
        background-color: rgba(150, 150, 150, 0.25) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Menu Lateral utilizando st.button sem os radio buttons
with st.sidebar:
    if st.button("Cadastros", key="btn_cadastros"):
        st.session_state.pagina_ativa = "Cadastros"
    
    if st.button("Encaminhamentos", key="Encaminhamentos"):
        st.session_state.pagina_ativa = "Encaminhamentos"
    
    if st.button("Relatórios", key="btn_relatorios"):
        st.session_state.pagina_ativa = "Relatórios"

# Roteamento de Telas
menu = st.session_state.pagina_ativa

if menu == "Cadastros":
    cadastros.render()
elif menu == "Encaminhamentos":
    encaminhamentos.render()
elif menu == "Relatórios":
    relatorios.render()