import streamlit as st
from datetime import date, datetime
from config.database import get_supabase_client

def render():
    st.title("Registro de Atendimentos")

    try:
        supabase = get_supabase_client()

        # Busca os estudantes cadastrados
        res_estudantes = (
            supabase.table("pessoas")
            .select("id, nome, cpf")
            .eq("tipo_pessoa", "Aluno")
            .order("nome", desc=False)
            .execute()
        )
        estudantes = res_estudantes.data

        # Busca profissionais cadastrados da Equipe Multi
        res_profs = (
            supabase.table("pessoas")
            .select("id, nome, tipo_pessoa")
            .eq("tipo_pessoa", "Equipe Multi")
            .order("nome", desc=False)
            .execute()
        )
        profissionais_cadastrados = res_profs.data

    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}")
        return

    with st.expander("➕ Novo Atendimento", expanded=True):
        # Selectbox inicia com "Selecione" (index=None) e permite digitar para filtrar
        estudante_sel = st.selectbox(
            "Selecione o Estudante:*",
            options=estudantes,
            index=None,
            placeholder="Selecione",
            format_func=lambda p: f"{p['nome']} (CPF: {p.get('cpf') or 'Não informado'})"
        )

        # Verifica em tempo real se o estudante selecionado possui encaminhamento 'Aceito'
        encaminhamento_aprovado = None
        if estudante_sel is not None:
            try:
                res_enc = (
                    supabase.table("encaminhamentos")
                    .select("id, escola, profissionais_destino, status")
                    .eq("pessoa_id", estudante_sel["id"])
                    .eq("status", "Aceito")
                    .order("id", desc=True)
                    .execute()
                )
                if res_enc.data:
                    encaminhamento_aprovado = res_enc.data[0]
                else:
                    st.warning(
                        f"⚠️ O estudante **{estudante_sel['nome']}** não possui encaminhamento aprovado no sistema."
                    )
            except Exception as e:
                st.error(f"Erro ao verificar situação do encaminhamento: {e}")

        with st.form("form_atendimento", clear_on_submit=True):
            c1, c2, c3 = st.columns([1.2, 2, 1.8])
            data_atend = c1.date_input("Data do Atendimento:*", value=date.today(), format="DD/MM/YYYY")

            prof_sel = c2.selectbox(
                "Profissional Responsável:*",
                options=profissionais_cadastrados,
                index=None,
                placeholder="Selecione",
                format_func=lambda p: p["nome"]
            )

            tipo_prof = c3.selectbox(
                "Especialidade / Tipo de Profissional:*",
                ["Psicólogo(a)", "Assistente Social", "Psicopedagogo(a)", "Fonoaudiólogo(a)", "Outro"]
            )

            evolucao = st.text_area("Evolução / Relato do Atendimento:*", height=160)

            if st.form_submit_button("Salvar Atendimento"):
                if estudante_sel is None:
                    st.error("Selecione um estudante antes de salvar.")
                elif encaminhamento_aprovado is None:
                    st.error(
                        f"Não é possível registrar atendimento: **{estudante_sel['nome']}** não possui encaminhamento aprovado no sistema."
                    )
                elif prof_sel is None:
                    st.error("Selecione o profissional responsável.")
                elif not evolucao.strip():
                    st.error("Preencha o campo de Evolução / Relato do Atendimento.")
                else:
                    try:
                        # Validação dupla no momento de salvar
                        check = (
                            supabase.table("encaminhamentos")
                            .select("id")
                            .eq("pessoa_id", estudante_sel["id"])
                            .eq("status", "Aceito")
                            .execute()
                        )
                        if not check.data:
                            st.error(
                                f"Operação bloqueada: **{estudante_sel['nome']}** não possui encaminhamento aprovado no sistema."
                            )
                            st.stop()

                        supabase.table("atendimentos").insert({
                            "data_atendimento": data_atend.strftime("%Y-%m-%d"),
                            "estudante_id": estudante_sel["id"],
                            "profissional_id": prof_sel["id"],
                            "tipo_profissional": tipo_prof,
                            "evolucao": evolucao
                        }).execute()

                        st.success("Atendimento registrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar atendimento: {e}")

    st.divider()
    st.subheader("Histórico de Atendimentos Realizados")
    try:
        res_hist = (
            supabase.table("atendimentos")
            .select("*")
            .order("data_atendimento", desc=True)
            .execute()
        )
        historico = res_hist.data

        if historico:
            # Mapeia IDs de pessoas para nomes para evitar conflito de FK no PostgREST
            res_todas_pessoas = supabase.table("pessoas").select("id, nome").execute()
            mapa_nomes = {p["id"]: p["nome"] for p in (res_todas_pessoas.data or [])}

            for item in historico:
                nome_est = mapa_nomes.get(item["estudante_id"], f"ID {item['estudante_id']}")
                nome_prof = mapa_nomes.get(item["profissional_id"], f"ID {item['profissional_id']}")

                try:
                    dt_br = datetime.strptime(item["data_atendimento"], "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    dt_br = item["data_atendimento"]

                with st.expander(f"{dt_br} — {nome_est} | {item['tipo_profissional']} ({nome_prof})"):
                    st.write(f"**Profissional:** {nome_prof} ({item['tipo_profissional']})")
                    st.write(f"**Evolução:** {item['evolucao']}")
        else:
            st.info("Nenhum atendimento registrado até o momento.")
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")