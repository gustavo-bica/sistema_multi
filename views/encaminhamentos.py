import streamlit as st
from datetime import datetime
from config.database import get_supabase_client

def render():
    st.title("Formulário de Encaminhamento")

    # 1. Selecionar o Aluno/Pessoa Cadastrado via API Supabase
    try:
        supabase = get_supabase_client()
        res_pessoas = (
            supabase.table("pessoas")
            .select("id, nome, data_nascimento, cpf")
            .eq("tipo_pessoa", "Aluno")
            .order("nome", desc=False)
            .execute()
        )
        pessoas = res_pessoas.data
    except Exception as e:
        st.error(f"Erro ao carregar lista de alunos/pessoas: {e}")
        return

    if not pessoas:
        st.warning("Nenhum estudante cadastrado no sistema. Cadastre primeiro na tela 'Cadastros'.")
        return

    pessoa_sel = st.selectbox(
        "Selecione o Estudante/Pessoa:*",
        options=pessoas,
        index=None,
        placeholder="Selecione",
        format_func=lambda p: f"{p['nome']} (CPF: {p.get('cpf') or 'Não informado'})"
    )

    st.divider()

    # 2. Escolha do Nível de Ensino
    nivel_ensino = st.radio(
        "Selecione o Modelo de Encaminhamento:*",
        options=["Educação Infantil", "Ensino Fundamental"],
        horizontal=True
    )

    with st.form("form_encaminhamento", clear_on_submit=False):
        st.header(f"Ficha de Encaminhamento - {nivel_ensino}")

        # SEÇÃO A: DADOS GERAIS DO ENCAMINHAMENTO
        col1, col2 = st.columns(2)
        with col1:
            escola = st.text_input("Escola:*")
            data_encaminhamento = st.date_input("Data do Encaminhamento:*", format="DD/MM/YYYY")
            turma = st.text_input("Turma:")
            turno = st.selectbox("Turno:", ["Manhã", "Tarde", "Integral", "Noite"])

        with col2:
            profissionais = st.multiselect(
                "Encaminhamento para:*",
                ["Psicólogo(a)", "Assistente Social", "Psicopedagogo(a)", "Fonoaudiólogo(a)"]
            )
            data_ingresso = st.date_input("Data de Ingresso na Escola:", format="DD/MM/YYYY", value=None)
            escola_anterior = st.text_input("Escola Anterior:")
            educadores = st.text_input("Professores / Educadores:")

        st.subheader("Identificação Familiar e Residência")
        col_mae1, col_mae2, col_mae3 = st.columns([2, 1, 1])
        mae_nome = col_mae1.text_input("Nome da Mãe:")
        mae_idade = col_mae2.number_input("Idade da Mãe:", min_value=0, max_value=120, value=0)
        mae_tel = col_mae3.text_input("Telefone da Mãe:")

        col_mae4, col_mae5 = st.columns(2)
        mae_prof = col_mae4.text_input("Profissão da Mãe:")
        mae_local = col_mae5.text_input("Local de Trabalho da Mãe:")

        col_pai1, col_pai2, col_pai3 = st.columns([2, 1, 1])
        pai_nome = col_pai1.text_input("Nome do Pai:")
        pai_idade = col_pai2.number_input("Idade do Pai:", min_value=0, max_value=120, value=0)
        pai_tel = col_pai3.text_input("Telefone do Pai:")

        col_pai4, col_pai5 = st.columns(2)
        pai_prof = col_pai4.text_input("Profissão do Pai:")
        pai_local = col_pai5.text_input("Local de Trabalho do Pai:")

        col_end1, col_end2 = st.columns(2)
        endereco_res = col_end1.text_input("Endereço Residencial:")
        ponto_ref = col_end2.text_input("Ponto de Referência do Domicílio:")
        melhor_turno_visita = st.text_input("Melhor turno/horário para visita domiciliar (se Assistente Social):")

        # SEÇÃO B: COMPOSIÇÃO FAMILIAR
        st.subheader("Composição Familiar")
        st.caption("Adicione até 3 membros residentes na mesma casa:")
        fam_membros = []
        for i in range(1, 4):
            with st.expander(f"Membro Familiar {i}"):
                f_nome = st.text_input(f"Nome {i}:", key=f"fnome_{i}")
                f_col1, f_col2, f_col3 = st.columns(3)
                f_idade = f_col1.number_input(f"Idade {i}:", min_value=0, value=0, key=f"fidade_{i}")
                f_parentesco = f_col2.text_input(f"Grau Parentesco {i}:", key=f"fparent_{i}")
                f_escolaridade = f_col3.text_input(f"Escolaridade {i}:", key=f"fesc_{i}")
                f_trabalho = st.text_input(f"Local de Trabalho {i}:", key=f"ftrab_{i}")
                if f_nome:
                    fam_membros.append({
                        "nome": f_nome,
                        "idade": f_idade,
                        "parentesco": f_parentesco,
                        "escolaridade": f_escolaridade,
                        "trabalho": f_trabalho
                    })

        # SEÇÃO C: QUESTÕES CENTRAIS
        st.subheader("Questões do Encaminhamento")
        motivo = st.text_area("3. Motivo do encaminhamento:*")
        opiniao_pais = st.text_area("4. Opinião dos pais sobre o encaminhamento:")
        situacao_econ = st.text_area("Situação econômica familiar / Benefícios sociais:")
        obs_importantes = st.text_area("Observações importantes sobre a criança/família:")
        acoes_escola = st.text_area("Ações/Intervenções que a escola já adotou:")

        # SEÇÃO D: CAMPOS ESPECÍFICOS DO NÍVEL DE ENSINO
        st.divider()
        if nivel_ensino == "Educação Infantil":
            st.subheader("Observações Específicas - Educação Infantil")
            col_inf1, col_inf2 = st.columns(2)
            alimentacao = col_inf1.text_input("Alimentação:")
            sono = col_inf2.text_input("Sono:")
            chupeta_mamadeira = col_inf1.text_input("Uso de chupeta/mamadeira:")
            esfincteres = col_inf2.text_input("Controle dos esfíncteres:")
            higiene = col_inf1.text_input("Higiene:")
            brincar_social = col_inf2.text_input("Brincar e Socialização:")

            compreende_falam = st.checkbox("Compreende o que lhe é falado?")
            consegue_expressar = st.checkbox("Consegue expressar seus desejos e necessidades?")
            uso_corpo_palavras = st.text_area("Usa palavras/frases ou gestos/corpo?")
            problema_fala = st.text_area("Problemas na articulação da fala:")
            avaliacao_auditiva = st.text_area("Avaliação auditiva / Histórico de otites:")
            psico_ampla = st.text_input("Psicomotricidade Ampla:")
            psico_fina = st.text_input("Psicomotricidade Fina:")
            esquema_corp = st.text_input("Esquema corporal / Lateralidade:")
            saude_posto = st.text_area("Saúde / Acompanhamento / Medicamentos / Posto:")
        else:  # Ensino Fundamental
            st.subheader("Observações Específicas - Ensino Fundamental")
            saude_posto = st.text_area("Saúde / Acompanhamento / Medicamentos / Posto:")
            avaliacao_auditiva = st.text_area("Avaliação auditiva / Histórico de otites:")
            assiduidade = st.text_input("Assiduidade:")
            aprendizagem = st.text_area("Aprendizagem:")
            psicomotricidade = st.text_input("Psicomotricidade:")
            atencao = st.text_input("Atenção:")
            memoria = st.text_input("Memória:")
            interesses_hab = st.text_input("Interesses e Habilidades:")
            chupeta_mamadeira = st.text_input("Uso de chupeta e mamadeira:")

            st.markdown("**Linguagem:**")
            escrita = st.text_input("a) Escrita:")
            leitura = st.text_input("b) Leitura:")
            linguagem_falada = st.text_input("c) Linguagem Falada:")
            raciocinio_logico = st.text_input("Raciocínio Lógico-Matemático:")

            st.markdown("**Socialização:**")
            part_grupos = st.text_input("Participação em grupos:")
            rel_colegas = st.text_input("Relacionamento com colegas:")
            rel_professor = st.text_input("Relacionamento com professor(a):")
            reacao_regras = st.text_input("Como reage às regras:")
            atitudes_aula = st.text_input("Atitudes no trabalho de aula:")
            part_familia = st.text_area("Interesse e participação da família:")
            impressao_familia = st.text_area("Impressão quanto ao ambiente familiar:")

            st.markdown("**Intervenções da Escola:**")
            interv_prof = st.text_area("a) do(a) professor(a):")
            interv_direcao = st.text_area("b) da direção:")
            interv_pedag = st.text_area("c) da equipe pedagógica:")
            outras_obs = st.text_area("Outras observações:")

        # SUBMISSÃO DO FORMULÁRIO
        btn_salvar = st.form_submit_button("Salvar Ficha de Encaminhamento")

        if btn_salvar:
            if not pessoa_sel:
                st.error("Selecione o Estudante/Pessoa antes de salvar a ficha.")
            elif not escola or not motivo or not profissionais:
                st.error("Preencha os campos obrigatórios (*): Escola, Motivo e Profissionais de destino.")
            else:
                try:
                    supabase = get_supabase_client()
                    dt_encam_str = data_encaminhamento.strftime('%Y-%m-%d') if data_encaminhamento else None
                    dt_ingr_str = data_ingresso.strftime('%Y-%m-%d') if data_ingresso else None
                    prof_str = ", ".join(profissionais)

                    # 1. Inserção Principal na Tabela 'encaminhamentos'
                    dados_encaminhamento = {
                        "pessoa_id": pessoa_sel['id'],
                        "status": "Pendente",
                        "nivel_ensino": nivel_ensino,
                        "escola": escola,
                        "data_encaminhamento": dt_encam_str,
                        "profissionais_destino": prof_str,
                        "data_ingresso_escola": dt_ingr_str,
                        "escola_anterior": escola_anterior,
                        "turma": turma,
                        "turno": turno,
                        "educadores_professores": educadores,
                        "mae_nome": mae_nome,
                        "mae_idade": mae_idade if mae_idade > 0 else None,
                        "mae_telefone": mae_tel,
                        "mae_profissao": mae_prof,
                        "mae_local_trabalho": mae_local,
                        "pai_nome": pai_nome,
                        "pai_idade": pai_idade if pai_idade > 0 else None,
                        "pai_telefone": pai_tel,
                        "pai_profissao": pai_prof,
                        "pai_local_trabalho": pai_local,
                        "endereco_residencial": endereco_res,
                        "ponto_referencia": ponto_ref,
                        "melhor_turno_visita_assistente": melhor_turno_visita,
                        "motivo_encaminhamento": motivo,
                        "opiniao_pais": opiniao_pais,
                        "situacao_economica_beneficios": situacao_econ,
                        "observacoes_importantes": obs_importantes,
                        "acoes_intervencoes_escola": acoes_escola
                    }

                    res_principal = supabase.table("encaminhamentos").insert(dados_encaminhamento).select("id").execute()
                    if not res_principal.data:
                        raise Exception("Falha ao obter o ID do encaminhamento inserido.")
                    encaminhamento_id = res_principal.data[0]['id']

                    # 2. Inserção na Tabela 'composicao_familiar'
                    if fam_membros:
                        membros_payload = []
                        for m in fam_membros:
                            membros_payload.append({
                                "encaminhamento_id": encaminhamento_id,
                                "nome": m['nome'],
                                "idade": m['idade'] if m['idade'] > 0 else None,
                                "grau_parentesco": m['parentesco'],
                                "escolaridade": m['escolaridade'],
                                "local_trabalho": m['trabalho']
                            })
                        supabase.table("composicao_familiar").insert(membros_payload).execute()

                    # 3. Inserção na Tabela Específica
                    if nivel_ensino == "Educação Infantil":
                        dados_infantil = {
                            "encaminhamento_id": encaminhamento_id,
                            "alimentacao": alimentacao,
                            "sono": sono,
                            "uso_chupeta_mamadeira": chupeta_mamadeira,
                            "controle_esfincteres": esfincteres,
                            "higiene": higiene,
                            "brincar_socializacao": brincar_social,
                            "compreende_o_que_falam": compreende_falam,
                            "consegue_expressar_desejos": consegue_expressar,
                            "uso_palavras_ou_corpo": uso_corpo_palavras,
                            "problemas_articulacao_fala": problema_fala,
                            "avaliacao_auditiva_otites": avaliacao_auditiva,
                            "psicomotricidade_ampla": psico_ampla,
                            "psicomotricidade_fina": psico_fina,
                            "esquema_corporal_lateralidade": esquema_corp,
                            "saude_medicao_posto": saude_posto
                        }
                        supabase.table("encaminhamento_infantil").insert(dados_infantil).execute()
                    else:
                        dados_fundamental = {
                            "encaminhamento_id": encaminhamento_id,
                            "saude_medicacao_posto": saude_posto,
                            "avaliacao_auditiva_otites": avaliacao_auditiva,
                            "assiduidade": assiduidade,
                            "aprendizagem": aprendizagem,
                            "psicomotricidade": psicomotricidade,
                            "atencao": atencao,
                            "memoria": memoria,
                            "interesses_habilidades": interesses_hab,
                            "uso_chupeta_mamadeira": chupeta_mamadeira,
                            "linguagem_escrita": escrita,
                            "linguagem_leitura": leitura,
                            "linguagem_falada": linguagem_falada,
                            "raciocinio_logico_matematico": raciocinio_logico,
                            "participacao_grupos": part_grupos,
                            "relacionamento_colegas": rel_colegas,
                            "relacionamento_professor": rel_professor,
                            "reacao_regras": reacao_regras,
                            "atitudes_trabalho_aula": atitudes_aula,
                            "interesse_participacao_familia": part_familia,
                            "impressao_ambiente_familiar": impressao_familia,
                            "intervencao_professor": interv_prof,
                            "intervencao_direcao": interv_direcao,
                            "intervencao_equipe_pedagogica": interv_pedag,
                            "outras_observacoes": outras_obs
                        }
                        supabase.table("encaminhamento_fundamental").insert(dados_fundamental).execute()

                    st.success("Encaminhamento salvo com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar encaminhamento: {e}")