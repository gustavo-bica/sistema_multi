import streamlit as st
from datetime import datetime
from config.database import get_supabase_client

@st.dialog("Detalhes da Solicitação de Encaminhamento", width="large")
def modal_detalhes_encaminhamento(enc):
    supabase = get_supabase_client()
    pessoa = enc.get("pessoas") or {}
    st.subheader(f"Estudante: {pessoa.get('nome', 'Não identificado')}")
    
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Escola:** {enc.get('escola') or '-'}")
    c2.write(f"**Nível:** {enc.get('nivel_ensino') or '-'}")
    c3.write(f"**Turma/Turno:** {enc.get('turma') or '-'} ({enc.get('turno') or '-'})")
    
    st.write(f"**Profissionais Solicitados:** {enc.get('profissionais_destino') or '-'}")
    st.write(f"**Data do Encaminhamento:** {enc.get('data_encaminhamento') or '-'}")
    
    st.divider()
    st.markdown("**Motivo do Encaminhamento:**")
    st.info(enc.get("motivo_encaminhamento") or "Não informado.")
    
    if enc.get("acoes_intervencoes_escola"):
        st.markdown("**Ações/Intervenções já adotadas pela escola:**")
        st.write(enc.get("acoes_intervencoes_escola"))
        
    if enc.get("observacoes_importantes"):
        st.markdown("**Observações Importantes:**")
        st.write(enc.get("observacoes_importantes"))

    # Exibe composição familiar e ficha específica em expander para não poluir a tela
    with st.expander("📄 Ver Ficha Completa (Família e Observações Específicas)", expanded=False):
        st.write(f"**Mãe:** {enc.get('mae_nome') or '-'} | **Tel:** {enc.get('mae_telefone') or '-'}")
        st.write(f"**Pai:** {enc.get('pai_nome') or '-'} | **Tel:** {enc.get('pai_telefone') or '-'}")
        st.write(f"**Endereço:** {enc.get('endereco_residencial') or '-'} (Ref: {enc.get('ponto_referencia') or '-'})")

        try:
            res_fam = supabase.table("composicao_familiar").select("*").eq("encaminhamento_id", enc["id"]).execute()
            if res_fam.data:
                st.markdown("**Composição Familiar:**")
                for m in res_fam.data:
                    st.write(f"- {m.get('nome')} ({m.get('grau_parentesco') or '-'}, {m.get('idade') or '-'} anos)")

            if enc.get("nivel_ensino") == "Educação Infantil":
                res_esp = supabase.table("encaminhamento_infantil").select("*").eq("encaminhamento_id", enc["id"]).execute()
            else:
                res_esp = supabase.table("encaminhamento_fundamental").select("*").eq("encaminhamento_id", enc["id"]).execute()

            if res_esp.data:
                st.markdown(f"**Dados Específicos ({enc.get('nivel_ensino')}):**")
                detalhes = res_esp.data[0]
                for chave, valor in detalhes.items():
                    if chave not in ("id", "encaminhamento_id") and valor not in (None, "", False):
                        label = chave.replace("_", " ").capitalize()
                        st.write(f"**{label}:** {'Sim' if valor is True else valor}")
        except Exception as e:
            st.warning(f"Não foi possível carregar os detalhes complementares: {e}")

    st.divider()
    st.subheader("Avaliação da Solicitação")
    
    status_atual = enc.get("status", "Pendente")
    st.write(f"**Status Atual:** {status_atual}")
    
    parecer = st.text_area(
        "Parecer / Justificativa da Equipe Multi:",
        value=enc.get("parecer_equipe") or "",
        placeholder="Descreva o motivo do aceite, agendamento inicial ou justificativa da recusa...",
        key=f"parecer_{enc['id']}"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    
    if col_btn1.button("✅ Aceitar Encaminhamento", type="primary", use_container_width=True, key=f"aceitar_{enc['id']}"):
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

    if col_btn2.button("❌ Recusar Encaminhamento", use_container_width=True, key=f"recusar_{enc['id']}"):
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


def render():
    st.title("📋 Solicitações de Encaminhamento")
    
    filtro_status = st.radio(
        "Filtrar por Status:",
        options=["Pendente", "Aceito", "Recusado", "Todos"],
        horizontal=True
    )
    
    st.divider()
    
    try:
        supabase = get_supabase_client()
        query = supabase.table("encaminhamentos").select("*, pessoas(nome, cpf)").order("id", desc=True)
        
        if filtro_status != "Todos":
            query = query.eq("status", filtro_status)
            
        res = query.execute()
        solicitacoes = res.data
        
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
            else:
                c4.warning("Pendente")
                
            if c5.button("🔍 Avaliar", key=f"btn_eval_{enc['id']}"):
                modal_detalhes_encaminhamento(enc)
                
    except Exception as e:
        st.error(f"Erro ao carregar solicitações: {e}")