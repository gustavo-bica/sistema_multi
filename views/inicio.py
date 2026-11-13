import streamlit as st
from datetime import date, timedelta
from config.database import get_supabase_client

def render():
    # Estilo limpo dos cards (borda sutil, sombra leve, texto centralizado, sem efeitos coloridos)
    st.markdown("""
        <style>
        .kpi-card {
            background-color: var(--secondary-background-color, #ffffff);
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 10px;
            padding: 28px 18px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            margin-bottom: 16px;
        }
        .kpi-titulo {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        .kpi-valor {
            font-size: 36px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 8px;
        }
        .kpi-subtitulo {
            font-size: 13px;
            opacity: 0.65;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        supabase = get_supabase_client()

        # 1. Consulta todos os encaminhamentos (Pendente, Aceito, Recusado, Inativo)
        res_enc = supabase.table("encaminhamentos").select("id, pessoa_id, status").execute()
        encaminhamentos = res_enc.data or []

        total_pedidos = len(encaminhamentos)

        # Estudantes únicos atualmente em atendimento (critério: status == 'Aceito')
        estudantes_ativos = {
            e["pessoa_id"] for e in encaminhamentos if e.get("status") == "Aceito"
        }
        total_estudantes_atendidos = len(estudantes_ativos)

        # 2. Consulta atendimentos realizados nos últimos 30 dias
        data_limite = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        res_atend = (
            supabase.table("atendimentos")
            .select("id")
            .gte("data_atendimento", data_limite)
            .execute()
        )
        atendimentos_30_dias = len(res_atend.data or [])

    except Exception as e:
        st.error(f"Erro ao carregar indicadores da tela inicial: {e}")
        return

    st.write("")  # Espaçamento superior

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-titulo">Total Pedidos de Encaminhamento</div>
                <div class="kpi-valor">{total_pedidos}</div>
                <div class="kpi-subtitulo">Todos os status registrados</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-titulo">Atendimentos</div>
                <div class="kpi-valor">{atendimentos_30_dias}</div>
                <div class="kpi-subtitulo">Últimos 30 dias</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-titulo">Total Estudantes Atendidos</div>
                <div class="kpi-valor">{total_estudantes_atendidos}</div>
                <div class="kpi-subtitulo">Encaminhamentos ativos</div>
            </div>
        """, unsafe_allow_html=True)