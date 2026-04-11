import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime
import pandas as pd
from docx import Document
from io import BytesIO

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Portal Escola Constantino", layout="centered")

# --- 1. VISUAL REFORÇADO (CSS) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span, div { color: #000000 !important; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #F8F9FA !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #16A34A !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO ---

def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        info_gs = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(info_gs, scopes=scope)
        client = gspread.authorize(creds)
        # Busca o link da planilha dentro do bloco connections.gsheets
        return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

# --- 3. FUNÇÃO DO WORD (REVISADA E EMPILHADA) ---
def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    doc.add_paragraph(f'Escola Pe. Constantino de Monte - Gerado em: {datetime.now().strftime("%d/%m/%Y")}')
    
    # TRUQUE MÁGICO: Remove espaços e padroniza os nomes das colunas da planilha
    df.columns = [str(c).strip().lower() for c in df.columns]

    for i, row in df.iterrows():
        # Busca o enunciado de forma flexível (aceita 'enunciado', 'questão', etc)
        texto_questao = row.get('enunciado', row.get('pergunta', row.get('questão', 'Sem texto na planilha')))
        
        doc.add_heading(f'Questão {i+1}', level=2)
        doc.add_paragraph(str(texto_questao))
        
        # MUDANÇA: Alternativas uma sobre a outra (parágrafos separados)
        doc.add_paragraph(f"A) {row.get('a', '')}")
        doc.add_paragraph(f"B) {row.get('b', '')}")
        doc.add_paragraph(f"C) {row.get('c', '')}")
        doc.add_paragraph(f"D) {row.get('d', '')}")
        doc.add_paragraph(f"E) {row.get('e', '')}")
        
        doc.add_paragraph(f"Gabarito: {row.get('gabarito', '')}")
        doc.add_paragraph("-" * 40)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. ÁREA RESTRITA ---
st.sidebar.header("🔐 Coordenação")
senha = st.sidebar.text_input("Senha", type="password")
acesso_coord = (senha == "constantino2026")

if acesso_coord:
    st.sidebar.success("Acesso Liberado!")
    menu = st.sidebar.radio("Navegação", ["Lançar Questões", "Ver Banco de Questões"])
else:
    menu = "Lançar Questões"

# --- 5. TELA: LANÇAR ---
if menu == "Lançar Questões":
    st.title("📝 Lançador de Simulados")
    with st.form("form_lançar"):
        prof = st.text_input("Nome do Professor")
        disc = st.selectbox("Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
        turmas = st.multiselect("Para quais turmas?", ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"])
        enunciado = st.text_area("Enunciado da Questão")
        
        c1, c2 = st.columns(2)
        with c1: a, b, c = st.text_input("Alternativa A"), st.text_input("Alternativa B"), st.text_input("Alternativa C")
        with c2: d, e, gab = st.text_input("Alternativa D"), st.text_input("Alternativa E"), st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])
        
        btn_enviar = st.form_submit_button("🚀 SALVAR QUESTÃO")

    if btn_enviar:
        if not prof or not turmas or not enunciado:
            st.warning("⚠️ Preencha Nome, Turmas e Enunciado!")
        else:
            with st.spinner("Salvando..."):
                sheet = conectar_google_sheets()
                if sheet:
                    try:
                        for t in turmas:
                            # Ordem das colunas: Data, Professor, Disciplina, Turma, Enunciado, Foto, A, B, C, D, E, Gabarito
                            linha = [datetime.now().strftime("%d/%m/%Y %H:%M"), prof, disc, t, enunciado, "", a, b, c, d, e, gab]
                            sheet.append_row(linha)
                        st.success(f"✅ Sucesso para as turmas: {', '.join(turmas)}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# --- 6. TELA: VER BANCO ---
elif menu == "Ver Banco de Questões":
    st.title("📊 Gestão de Questões")
    
    with st.spinner("Lendo banco de dados..."):
        sheet = conectar_google_sheets()
        
    if sheet:
        try:
            dados = sheet.get_all_records()
            if not dados:
                st.info("Nenhuma questão encontrada na planilha.")
            else:
                df = pd.DataFrame(dados)
                
                # Filtros
                st.write("🔍 **Filtros**")
                col_f1, col_f2 = st.columns(2)
                with col_f1: f_t = st.multiselect("Filtrar Turma", options=list(df['Turma'].unique()))
                with col_f2: f_d = st.multiselect("Filtrar Disciplina", options=list(df['Disciplina'].unique()))
                
                df_f = df.copy()
                if f_t: df_f = df_f[df_f['Turma'].isin(f_t)]
                if f_d: df_f = df_f[df_f['Disciplina'].isin(f_d)]
                
                st.write(f"Questões filtradas: **{len(df_f)}**")
                st.dataframe(df_f)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📄 Gerar Word (Empilhado)"):
                        doc_p = gerar_word(df_f, "Escola Pe. Constantino")
                        st.download_button("⬇️ Baixar .docx", doc_p, "simulado_escolar.docx")
                with c2:
                    csv = df_f.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV", csv, "banco.csv")
        except Exception as e:
            st.error(f"Erro ao processar dados: {e}")
