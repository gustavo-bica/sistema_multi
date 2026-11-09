import streamlit as st
import requests
import base64
import re
from datetime import datetime
from config.database import get_db_connection, get_supabase_client

# Função para mascarar o CPF com escape de Markdown (\*) para não sumir no st.write
def formatar_cpf_mascarado(cpf):
    if not cpf:
        return "-"
    
    # Extrai apenas os dígitos numéricos
    apenas_numeros = re.sub(r'\D', '', str(cpf))
    
    # Se possuir 11 dígitos
    if len(apenas_numeros) == 11:
        p1 = apenas_numeros[:3]
        p2 = apenas_numeros[-2:]
        # Usa '\*' para evitar que o Streamlit interprete os asteriscos como formatação de texto
        return f"{p1}.\\*\\*\\*.\\*\\*\\*-{p2}"
    
    return str(cpf)

# Função para renderizar PDF corretamente via Base64 em HTML
def render_pdf_embed(pdf_url, height=500):
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            base64_pdf = base64.b64encode(response.content).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="{height}px" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Erro ao carregar o arquivo PDF do servidor.")
    except Exception as e:
        st.error(f"Erro ao processar visualização do PDF: {e}")

# Modal (Janela sobreposta) para Anexos do Estudante / Pessoa
@st.dialog("Anexos do Estudante / Pessoa", width="large")
def modal_anexos(pessoa):
    st.write(f"**Pessoa selecionada:** {pessoa['nome']} ({pessoa['tipo_pessoa']})")
    
    # Seção 1: Upload de Novos PDFs
    st.subheader("📎 Enviar Novo PDF")
    uploaded_files = st.file_uploader(
        "Selecione um ou mais arquivos PDF", 
        type=["pdf"], 
        accept_multiple_files=True,
        key=f"uploader_{pessoa['id']}"
    )
    
    if uploaded_files and st.button("Salvar Anexos", key=f"btn_upload_{pessoa['id']}"):
        try:
            supabase = get_supabase_client()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            NOME_BUCKET = "documentos-estudantes"
            
            for pdf in uploaded_files:
                bytes_data = pdf.read()
                file_path = f"pessoa_{pessoa['id']}/{pdf.name}"
                
                # Upload no Supabase Storage
                supabase.storage.from_(NOME_BUCKET).upload(
                    file_path, 
                    bytes_data, 
                    file_options={"upsert": "true", "content-type": "application/pdf"}
                )
                
                # Obter URL pública
                public_url = supabase.storage.from_(NOME_BUCKET).get_public_url(file_path)
                
                # Gravação no MySQL
                cursor.execute(
                    "INSERT INTO arquivos (pessoa_id, nome, url) VALUES (%s, %s, %s)",
                    (pessoa['id'], pdf.name, public_url)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            st.success("PDF(s) salvo(s) com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar arquivo: {e}")
            
    st.divider()
    
    # Seção 2: Listagem e Exibição de Anexos Cadastrados
    st.subheader("📚 Anexos Cadastrados")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM arquivos WHERE pessoa_id = %s ORDER BY id DESC", (pessoa['id'],))
        arquivos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if arquivos:
            pdf_sel = st.selectbox(
                "Selecione para visualizar:",
                options=arquivos,
                format_func=lambda a: a['nome']
            )
            if pdf_sel:
                render_pdf_embed(pdf_sel['url'], height=550)
        else:
            st.info("Nenhum anexo encontrado para esta pessoa.")
    except Exception as e:
        st.error(f"Erro ao carregar anexos: {e}")


def render():
    st.title("Cadastros de Pessoas")

    # Formulário de Novo Cadastro
    with st.expander("➕ Novo Cadastro de Pessoa", expanded=False):
        with st.form("form_pessoa", clear_on_submit=True):
            nome = st.text_input("Nome Completo*")
            tipo = st.selectbox("Tipo de Pessoa*", ["Aluno", "Professor", "Equipe Multi"])
            
            # Campo de data formatado no padrão brasileiro (DD/MM/AAAA)
            data_nasc = st.date_input(
                "Data de Nascimento",
                format="DD/MM/YYYY",
                value=None
            )
            
            cpf = st.text_input("CPF (apenas números ou formatado)*")
            
            if st.form_submit_button("Salvar Cadastramento"):
                if nome and cpf:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        data_formatada_mysql = data_nasc.strftime('%Y-%m-%d') if data_nasc else None
                        
                        query = "INSERT INTO pessoas (nome, tipo_pessoa, data_nascimento, cpf) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (nome, tipo, data_formatada_mysql, cpf))
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Pessoa '{nome}' cadastrada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                else:
                    st.warning("Preencha os campos obrigatórios (Nome e CPF).")

    st.divider()

    # Tabela de Pessoas Cadastradas
    st.subheader("Pessoas Cadastradas")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pessoas ORDER BY nome ASC")
        pessoas = cursor.fetchall()
        cursor.close()
        conn.close()

        if pessoas:
            # Cabeçalho da Tabela
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            c1.write("**Nome**")
            c2.write("**Tipo**")
            c3.write("**Data Nasc.**")
            c4.write("**CPF**")
            c5.write("**Arquivos**")

            for p in pessoas:
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
                col1.write(p['nome'])
                col2.write(p['tipo_pessoa'])
                
                # Formata a data recebida do MySQL para o padrão BR (DD/MM/AAAA) ao exibir
                dt_nasc = p.get('data_nascimento')
                data_exibicao = dt_nasc.strftime('%d/%m/%Y') if dt_nasc else "-"
                col3.write(data_exibicao)
                
                # Aplicação da máscara visual do CPF com escape de Markdown
                col4.write(formatar_cpf_mascarado(p['cpf']))
                
                if col5.button("📎 Anexos", key=f"btn_anexos_{p['id']}"):
                    modal_anexos(p)
        else:
            st.info("Nenhuma pessoa cadastrada.")
    except Exception as e:
        st.error(f"Erro ao buscar pessoas: {e}")