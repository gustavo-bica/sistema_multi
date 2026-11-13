import streamlit as st
from datetime import datetime
from config.database import get_supabase_client


def render():
    st.title("🩺 Gestão de Atendimentos")

    tab1, tab2 = st.tabs(["➕ Novo Atendimento", "🔍 Consultar Atendimentos"])

    # -------------------------------------------------------------------------
    # ABA 1: NOVO ATENDIMENTO
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Registar Novo Atendimento")

        try:
            supabase = get_supabase_client()

            # Busca estudantes (Tipo Aluno) via API Supabase
            res_estudantes = supabase.table("pessoas").select("id, nome, cpf").eq("tipo_pessoa", "Aluno").order("nome", desc=False).execute()
            estudantes = res_estudantes.data

            # Busca profissionais (Tipo Equipe Multi) via API Supabase
            res_profissionais = supabase.table("pessoas").select("id, nome").eq("tipo_pessoa", "Equipe Multi").order("nome", desc=False).execute()
            profissionais = res_profissionais.data

        except Exception as e:
            st.error(f"Erro ao carregar dados do Supabase: {e}")
            return

        if not estudantes:
            st.warning("Nenhum estudante (Aluno) encontrado no sistema. Cadastre-os primeiro na tela 'Cadastros'.")
            return

        if not profissionais:
            st.warning("Nenhum profissional da 'Equipe Multi' encontrado. Cadastre um profissional com o tipo 'Equipe Multi' na tela 'Cadastros'.")
            return

        with st.form("form_atendimento", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                data_atendimento = st.date_input("Data do Atendimento*", format="DD/MM/YYYY")

                estudante_sel = st.selectbox(
                    "Estudante*",
                    options=estudantes,
                    format_func=lambda e: f"{e['nome']} (CPF: {e.get('cpf') or 'Não informado'})"
                )

            with col2:
                profissional_sel = st.selectbox(
                    "Profissional*",
                    options=profissionais,
                    format_func=lambda p: p['nome']
                )

                tipo_profissional = st.selectbox(
                    "Tipo de Profissional*",
                    options=["Fonoaudiólogo", "Assistente Social", "Psicólogo", "Psicopedagogo"]
                )

            st.markdown("**Evolução*:**")
            evolucao = st.text_area("Descreva a evolução do atendimento:", height=200)

            btn_salvar = st.form_submit_button("Salvar Atendimento")

            if btn_salvar:
                if not evolucao.strip():
                    st.warning("Preencha o campo de evolução do atendimento.")
                else:
                    try:
                        supabase = get_supabase_client()

                        data_formatada = data_atendimento.strftime('%Y-%m-%d')

                        # Inserção no Supabase (Porta 443)
                        supabase.table("atendimentos").insert({
                            "data_atendimento": data_formatada,
                            "estudante_id": estudante_sel['id'],
                            "profissional_id": profissional_sel['id'],
                            "tipo_profissional": tipo_profissional,
                            "evolucao": evolucao
                        }).execute()

                        st.success("Atendimento registado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar atendimento: {e}")

    # -------------------------------------------------------------------------
    # ABA 2: CONSULTAR ATENDIMENTOS
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("🔍 Atendimentos Registados")
        try:
            supabase = get_supabase_client()

            # Busca os atendimentos trazendo os dados das tabelas relacionadas (JOIN)
            query = """
                id,
                data_atendimento,
                tipo_profissional,
                evolucao,
                estudante:pessoas!atendimentos_estudante_id_fkey(nome),
                profissional:pessoas!atendimentos_profissional_id_fkey(nome)
            """
            res_atendimentos = supabase.table("atendimentos").select(query).order("data_atendimento", desc=True).order("id", desc=True).execute()
            lista_atendimentos = res_atendimentos.data

            if lista_atendimentos:
                for at in lista_atendimentos:
                    dt_str = at.get('data_atendimento')
                    if dt_str:
                        try:
                            dt_obj = datetime.strptime(dt_str, '%Y-%m-%d')
                            dt_formatada = dt_obj.strftime('%d/%m/%Y')
                        except Exception:
                            dt_formatada = dt_str
                    else:
                        dt_formatada = "-"

                    estudante_nome = at.get('estudante', {}).get('nome', 'Estudante Desconhecido')
                    profissional_nome = at.get('profissional', {}).get('nome', 'Profissional Desconhecido')

                    with st.expander(f"🩺 {estudante_nome} - {at['tipo_profissional']} ({dt_formatada})"):
                        st.write(f"**Profissional:** {profissional_nome} ({at['tipo_profissional']})")
                        st.write(f"**Data:** {dt_formatada}")
                        st.markdown("**Evolução:**")
                        st.info(at['evolucao'])
            else:
                st.info("Nenhum atendimento registado até ao momento.")
        except Exception as e:
            st.error(f"Erro ao consultar atendimentos: {e}")