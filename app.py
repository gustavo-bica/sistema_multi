import streamlit as st
from views import cadastros, encaminhamentos, solicitacoes_encaminhamento, relatorios, atendimentos

st.set_page_config(
    page_title="Sistema Multi",
    page_icon="🏫",
    layout="wide"
)

# Inicializa os estados no session_state
if "pagina_ativa" not in st.session_state:
    st.session_state.pagina_ativa = "Cadastros"

if "menu_encaminhamentos_aberto" not in st.session_state:
    st.session_state.menu_encaminhamentos_aberto = False

# Injeção de CSS para estilizar a barra lateral e os botões do menu
st.markdown("""
    <style>
    /* 1. Largura da barra lateral (Sidebar) ajustada para comportar os submenus */
    [data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 220px !important;
    }

    /* 2. Estilização dos botões principais para parecerem itens de menu clicáveis */
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

    /* 3. Estilização específica para os subitens do submenu (recuo e fonte menor) */
    [data-testid="stSidebar"] div.st-key-btn_novo_encaminhamento button,
    [data-testid="stSidebar"] div.st-key-btn_solicitacoes_encaminhamento button {
        padding-left: 26px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Menu Lateral utilizando st.button e controle de estado para o dropdown
with st.sidebar:
    if st.button("Cadastros", key="btn_cadastros"):
        st.session_state.pagina_ativa = "Cadastros"

    # Botão principal do Dropdown com indicador visual de estado (▸ / ▾)
    icone_seta = "▾" if st.session_state.menu_encaminhamentos_aberto else "▸"
    if st.button(f"Encaminhamentos {icone_seta}", key="btn_encaminhamentos"):
        st.session_state.menu_encaminhamentos_aberto = not st.session_state.menu_encaminhamentos_aberto
        st.rerun()

    # Submenu retrátil exibido apenas quando aberto
    if st.session_state.menu_encaminhamentos_aberto:
        if st.button("Novo encaminhamento", key="btn_novo_encaminhamento"):
            st.session_state.pagina_ativa = "Novo encaminhamento"

        if st.button("Solicitações de Encaminhamento", key="btn_solicitacoes_encaminhamento"):
            st.session_state.pagina_ativa = "Solicitações de Encaminhamento"

    if st.button("Atendimentos", key="btn_atendimentos"):
        st.session_state.pagina_ativa = "Atendimentos"

    if st.button("Relatórios", key="btn_relatorios"):
        st.session_state.pagina_ativa = "Relatórios"

# Roteamento de Telas
menu = st.session_state.pagina_ativa

if menu == "Cadastros":
    cadastros.render()
elif menu == "Novo encaminhamento":
    encaminhamentos.render()
elif menu == "Solicitações de Encaminhamento":
    solicitacoes_encaminhamento.render()
elif menu == "Atendimentos":
    atendimentos.render()
elif menu == "Relatórios":
    relatorios.render()