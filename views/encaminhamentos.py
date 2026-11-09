import streamlit as st
from datetime import datetime
from config.database import get_db_connection

def render():
    st.title("Formulário de Encaminhamento")

    # 1. Selecionar o Aluno / Pessoa Cadastrado
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, data_nascimento, cpf FROM pessoas ORDER BY nome ASC")
        pessoas = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao carregar lista de alunos/pessoas: {e}")
        return

    if not pessoas:
        st.warning("Nenhuma pessoa cadastrada no sistema. Cadastre primeiro na tela 'Cadastros'.")
        return

    pessoa_sel = st.selectbox(
        "Selecione o Estudante/Pessoa:*",
        options=pessoas,
        format_func=lambda p: f"{p['nome']} (CPF: {p['cpf'] or 'Não informado'})"
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

        # --- SEÇÃO A: DADOS GERAIS DO ENCAMINHAMENTO ---
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

        # --- SEÇÃO B: COMPOSIÇÃO FAMILIAR ---
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
                        "nome": f_nome, "idade": f_idade, 
                        "parentesco": f_parentesco, "escolaridade": f_escolaridade, 
                        "trabalho": f_trabalho
                    })

        # --- SEÇÃO C: QUESTÕES CENTRAIS ---
        st.subheader("Questões do Encaminhamento")
        motivo = st.text_area("3. Motivo do encaminhamento:*")
        opiniao_pais = st.text_area("4. Opinião dos pais sobre o encaminhamento:")
        situacao_econ = st.text_area("Situação econômica familiar / Benefícios sociais:")
        obs_importantes = st.text_area("Observações importantes sobre a criança/família:")
        acoes_escola = st.text_area("Ações/Intervenções que a escola já adotou:")

        # --- SEÇÃO D: CAMPOS ESPECÍFICOS DO NÍVEL DE ENSINO ---
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

        else: # Ensino Fundamental
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

        # --- SUBMISSÃO DO FORMULÁRIO ---
        btn_salvar = st.form_submit_button("Salvar Ficha de Encaminhamento")

        if btn_salvar:
            if not escola or not motivo or not profissionais:
                st.error("Preencha os campos obrigatórios (*): Escola, Motivo e Profissionais de destino.")
            else:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    # 1. Insert Principal em 'encaminhamentos'
                    sql_principal = """
                        INSERT INTO encaminhamentos (
                            pessoa_id, nivel_ensino, escola, data_encaminhamento, profissionais_destino,
                            data_ingresso_escola, escola_anterior, turma, turno, educadores_professores,
                            mae_nome, mae_idade, mae_telefone, mae_profissao, mae_local_trabalho,
                            pai_nome, pai_idade, pai_telefone, pai_profissao, pai_local_trabalho,
                            endereco_residencial, ponto_referencia, melhor_turno_visita_assistente,
                            motivo_encaminhamento, opiniao_pais, situacao_economica_beneficios,
                            observacoes_importantes, acoes_intervencoes_escola
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    prof_str = ", ".join(profissionais)
                    cursor.execute(sql_principal, (
                        pessoa_sel['id'], nivel_ensino, escola, data_encaminhamento, prof_str,
                        data_ingresso, escola_anterior, turma, turno, educadores,
                        mae_nome, mae_idade, mae_tel, mae_prof, mae_local,
                        pai_nome, pai_idade, pai_tel, pai_prof, pai_local,
                        endereco_res, ponto_ref, melhor_turno_visita,
                        motivo, opiniao_pais, situacao_econ, obs_importantes, acoes_escola
                    ))
                    encaminhamento_id = cursor.lastrowid

                    # 2. Insert na Composição Familiar
                    for m in fam_membros:
                        cursor.execute("""
                            INSERT INTO composicao_familiar 
                            (encaminhamento_id, nome, idade, grau_parentesco, escolaridade, local_trabalho)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (encaminhamento_id, m['nome'], m['idade'], m['parentesco'], m['escolaridade'], m['trabalho']))

                    # 3. Insert na Tabela Específica
                    if nivel_ensino == "Educação Infantil":
                        cursor.execute("""
                            INSERT INTO encaminhamento_infantil (
                                encaminhamento_id, alimentacao, sono, uso_chupeta_mamadeira,
                                controle_esfincteres, higiene, brincar_socializacao,
                                compreende_o_que_falam, consegue_expressar_desejos,
                                uso_palavras_ou_corpo, problemas_articulacao_fala,
                                avaliacao_auditiva_otites, psicomotricidade_ampla,
                                psicomotricidade_fina, esquema_corporal_lateralidade, saude_medicao_posto
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            encaminhamento_id, alimentacao, sono, chupeta_mamadeira,
                            esfincteres, higiene, brincar_social,
                            compreende_falam, consegue_expressar,
                            uso_corpo_palavras, problema_fala,
                            avaliacao_auditiva, psico_ampla,
                            psico_fina, esquema_corp, saude_posto
                        ))
                    else:
                        cursor.execute("""
                            INSERT INTO encaminhamento_fundamental (
                                encaminhamento_id, saude_medicacao_posto, avaliacao_auditiva_otites,
                                assiduidade, aprendizagem, psicomotricidade, atencao, memoria,
                                interesses_habilidades, uso_chupeta_mamadeira, linguagem_escrita,
                                linguagem_leitura, linguagem_falada, raciocinio_logico_matematico,
                                participacao_grupos, relacionamento_colegas, relacionamento_professor,
                                reacao_regras, atitudes_trabalho_aula, interesse_participacao_familia,
                                impressao_ambiente_familiar, intervencao_professor, intervencao_direcao,
                                intervencao_equipe_pedagogica, outras_observacoes
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            encaminhamento_id, saude_posto, avaliacao_auditiva,
                            assiduidade, aprendizagem, psicomotricidade, atencao, memoria,
                            interesses_hab, chupeta_mamadeira, escrita,
                            leitura, linguagem_falada, raciocinio_logico,
                            part_grupos, rel_colegas, rel_professor,
                            reacao_regras, atitudes_aula, part_familia,
                            impressao_familia, interv_prof, interv_direcao,
                            interv_pedag, outras_obs
                        ))

                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Encaminhamento salvo com sucesso no banco de dados!")
                except Exception as e:
                    st.error(f"Erro ao salvar encaminhamento: {e}")

