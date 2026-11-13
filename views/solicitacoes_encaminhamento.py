import streamlit as st
from datetime import datetime
from config.database import get_supabase_client

@st.dialog("Detalhes da Solicitação de Encaminhamento", width="large")
def modal_detalhes_encaminhamento(enc):
    supabase = get_supabase_client()
    pessoa = enc.get("pessoas") or {}
    st.subheader(f"Estudante: {pessoa.get('nome', 'Não identificado')}")
    
    # Dados Gerais
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Escola:** {enc.get('escola') or '-'}")
    c2.write(f"**Nível:** {enc.get('nivel_ensino') or '-'}")
    c3.write(f"**Turma/Turno:** {enc.get('turma') or '-'} ({enc.get('turno') or '-'})")
    
    c4, c5 = st.columns(2)
    c4.write(f"**Profissionais Solicitados:** {enc.get('profissionais_destino') or '-'}")
    c5.write(f"**Data do Encaminhamento:** {enc.get('data_encaminhamento') or '-'}")
    
    c6, c7, c8 = st.columns(3)
    c6.write(f"**Ingresso na Escola:** {enc.get('data_ingresso_escola') or '-'}")
    c7.write(f"**Escola Anterior:** {enc.get('escola_anterior') or '-'}")
    c8.write(f"**Educadores:** {enc.get('educadores_professores') or '-'}")

    st.divider()

    # Identificação Familiar e Residência
    st.subheader("Identificação Familiar e Residência")
    f1, f2 = st.columns(2)
    with f1:
        st.write(f"**Mãe:** {enc.get('mae_nome') or '-'} ({enc.get('mae_idade') or '-'} anos)")
        st.write(f"**Telefone Mãe:** {enc.get('mae_telefone') or '-'}")
        st.write(f"**Profissão/Trabalho Mãe:** {enc.get('mae_profissao') or '-'} / {enc.get('mae_local_trabalho') or '-'}")
    with f2:
        st.write(f"**Pai:** {enc.get('pai_nome') or '-'} ({enc.get('pai_idade') or '-'} anos)")
        st.write(f"**Telefone Pai:** {enc.get('pai_telefone') or '-'}")
        st.write(f"**Profissão/Trabalho Pai:** {enc.get('pai_profissao') or '-'} / {enc.get('pai_local_trabalho') or '-'}")

    st.write(f"**Endereço Residencial:** {enc.get('endereco_residencial') or '-'} | **Ponto de Referência:** {enc.get('ponto_referencia') or '-'}")
    if enc.get("melhor_turno_visita_assistente"):
        st.write(f"**Melhor turno/horário para visita domiciliar:** {enc.get('melhor_turno_visita_assistente')}")

    # Composição Familiar
    try:
        res_fam = supabase.table("composicao_familiar").select("*").eq("encaminhamento_id", enc["id"]).execute()
        if res_fam.data:
            st.markdown("**Composição Familiar:**")
            for m in res_fam.data:
                st.write(
                    f"- **{m.get('nome')}** | Parentesco: {m.get('grau_parentesco') or '-'} | "
                    f"Idade: {m.get('idade') or '-'} | Escolaridade: {m.get('escolaridade') or '-'} | "
                    f"Trabalho: {m.get('local_trabalho') or '-'}"
                )
    except Exception as e:
        st.warning(f"Não foi possível carregar a composição familiar: {e}")

    st.divider()

    # Questões do Encaminhamento
    st.subheader("Questões do Encaminhamento")
    st.markdown("**Motivo do Encaminhamento:**")
    st.info(enc.get("motivo_encaminhamento") or "Não informado.")
    
    if enc.get("opiniao_pais"):
        st.markdown("**Opinião dos pais sobre o encaminhamento:**")
        st.write(enc.get("opiniao_pais"))

    if enc.get("situacao_economica_beneficios"):
        st.markdown("**Situação econômica familiar / Benefícios sociais:**")
        st.write(enc.get("situacao_economica_beneficios"))

    if enc.get("acoes_intervencoes_escola"):
        st.markdown("**Ações/Intervenções já adotadas pela escola:**")
        st.write(enc.get("acoes_intervencoes_escola"))
        
    if enc.get("observacoes_importantes"):
        st.markdown("**Observações Importantes:**")
        st.write(enc.get("observacoes_importantes"))

    # Dados Específicos do Nível de Ensino
    try:
        if enc.get("nivel_ensino") == "Educação Infantil":
            res_esp = supabase.table("encaminhamento_infantil").select("*").eq("encaminhamento_id", enc["id"]).execute()
        else:
            res_esp = supabase.table("encaminhamento_fundamental").select("*").eq("encaminhamento_id", enc["id"]).execute()

        if res_esp.data:
            st.divider()
            st.subheader(f"Observações Específicas - {enc.get('nivel_ensino')}")
            detalhes = res_esp.data[0]
            for chave, valor in detalhes.items():
                if chave not in ("id", "encaminhamento_id") and valor not in (None, ""):
                    label = chave.replace("_", " ").capitalize()
                    if isinstance(valor, bool):
                        st.write(f"**{label}:** {'Sim' if valor else 'Não'}")
                    else:
                        st.write(f"**{label}:** {valor}")
    except Exception as e:
        st.warning(f"Não foi possível carregar os dados específicos do nível de ensino: {e}")

    st.divider()

    # Avaliação / Movimentação de Status da Solicitação
    st.subheader("Avaliação e Situação do Encaminhamento")
    
    status_atual = enc.get("status", "Pendente")
    st.write(f"**Status Atual:** {status_atual}")
    
    parecer = st.text_area(
        "Parecer / Justificativa da Equipe Multi:",
        value=enc.get("parecer_equipe") or "",
        placeholder="Descreva o motivo do aceite, justificativa da recusa ou motivo da inativação (alta, mudança de cidade, etc.)...",
        key=f"parecer_{enc['id']}"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    if col_btn1.button("✅ Aceitar", type="primary", use_container_width=True, key=f"aceitar_{enc['id']}"):
        try:
            supabase.table("encaminhamentos").update({
                "status": "Aceito",
                "parecer_equipe": parecer,
                "data_avaliacao": datetime.now().isoformat()
            }).eq("id", enc["id"]).execute()
            st.success("Encaminhamento ACEITO! O estudante já está liberado para atendimentos.")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar status: {e}")

    if col_btn2.button("❌ Recusar", use_container_width=True, key=f"recusar_{enc['id']}"):
        if not parecer.strip():
            st.warning("Informe uma justificativa no campo de parecer antes de recusar.")
        else:
            try:
                supabase.table("encaminhamentos").update({
                    "status": "Recusado",
                    "parecer_equipe": parecer,
                    "data_avaliacao": datetime.now().isoformat()
                }).eq("id", enc["id"]).execute()
                st.warning("Encaminhamento RECUSADO.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar status: {e}")

    if col_btn3.button("🚫 Inativar", use_container_width=True, key=f"inativar_{enc['id']}"):
        if not parecer.strip():
            st.warning("Informe o motivo da inativação (ex.: alta, mudança de cidade) no campo de parecer.")
        else:
            try:
                supabase.table("encaminhamentos").update({
                    "status": "Inativo",
                    "parecer_equipe": parecer,
                    "data_avaliacao": datetime.now().isoformat()
                }).eq("id", enc["id"]).execute()
                st.info("Encaminhamento marcado como INATIVO.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar status: {e}")


def render():
    st.title("📋 Solicitações de Encaminhamento")
    
    try:
        supabase = get_supabase_client()
        # Busca todos os encaminhamentos para calcular os indicadores e filtrar
        res = supabase.table("encaminhamentos").select("*, pessoas(nome, cpf)").order("id", desc=True).execute()
        todas_solicitacoes = res.data or []

        # Contadores para controle de alunos atendidos atualmente (critério: status == 'Aceito')
        total_solicitacoes = len(todas_solicitacoes)
        total_ativos = sum(1 for s in todas_solicitacoes if s.get("status") == "Aceito")
        total_pendentes = sum(1 for s in todas_solicitacoes if s.get("status") == "Pendente")
        total_inativos = sum(1 for s in todas_solicitacoes if s.get("status") == "Inativo")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Solicitações", total_solicitacoes)
        m2.metric("Em Atendimento (Aceitos)", total_ativos)
        m3.metric("Pendentes", total_pendentes)
        m4.metric("Inativos", total_inativos)

        st.divider()

        filtro_status = st.radio(
            "Filtrar por Status:",
            options=["Pendente", "Aceito", "Recusado", "Inativo", "Todos"],
            horizontal=True
        )
        
        st.divider()
        
        if filtro_status == "Todos":
            solicitacoes = todas_solicitacoes
        else:
            solicitacoes = [s for s in todas_solicitacoes if s.get("status") == filtro_status]
        
        if not solicitacoes:
            st.info(f"Nenhuma solicitação encontrada com o status '{filtro_status}'.")
            return
            
        # Cabeçalho da listagem
        h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 1.5, 1.5])
        h1.write("**Estudante**")
        h2.write("**Escola**")
        h3.write("**Destino**")
        h4.write("**Status**")
        h5.write("**Ação**")
        
        for enc in solicitacoes:
            pessoa = enc.get("pessoas") or {}
            nome_estudante = pessoa.get("nome", "Desconhecido")
            status = enc.get("status", "Pendente")
            
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1.5, 1.5])
            c1.write(nome_estudante)
            c2.write(enc.get("escola") or "-")
            c3.write(enc.get("profissionais_destino") or "-")
            
            if status == "Aceito":
                c4.success("Aceito")
            elif status == "Recusado":
                c4.error("Recusado")
            elif status == "Inativo":
                c4.info("Inativo")
            else:
                c4.warning("Pendente")
                
            if c5.button("Avaliar/Editar", key=f"btn_eval_{enc['id']}"):
                modal_detalhes_encaminhamento(enc)
                
    except Exception as e:
        st.error(f"Erro ao carregar solicitações: {e}")