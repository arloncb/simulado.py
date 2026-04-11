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

# --- 1. VISUAL À PROVA DE ERROS (CSS) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    h1, h2, h3, p, label, span, div {
        color: #000000 !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #F3F4F6 !important;
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
        return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def upload_github(arquivo, nome_arquivo):
    try:
        token = st.secrets["github_token"]
        # ⚠️ AJUSTE SEU REPOSITÓRIO AQUI
        repo = "SEU_USUARIO/SEU_REPOSITORIO" 
        url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
        conteudo = base64.b64encode(arquivo.read()).decode()
        payload = {"message": f"Questão: {nome_arquivo}", "content": conteudo}
        headers = {"Authorization": f"token {token}"}
        res = requests.put(url, json=payload, headers=headers)
        return res.json()['content']['download_url'] if res.status_code in [200, 201] else ""
    except:
        return ""

def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    for i, row in df.iterrows():
        doc.add_heading(f'Questão {i+1}', level=2)
        doc.add_paragraph(str(row.get('Enunciado', 'Sem texto')))
        doc.add_paragraph(f"A) {row.get('A', '')} | B) {row.get('B', '')} | C) {row.get('C', '')}")
        doc.add_paragraph(f"D) {row.get('D', '')} | E) {row.get('E', '')}")
        doc.add_paragraph(f"Gabarito: {row.get('Gabarito', '')}")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. ÁREA RESTRITA ---
st.sidebar.header("🔐 Coordenação")
senha = st.sidebar.text_input("Senha", type="password")
acesso_coord = (senha == "constantino2026")

if acesso_coord:
    st.sidebar.success("Acesso Liberado!")
    menu = st.sidebar.radio("Navegação", ["Lançar Questões", "Ver Banco de Questões"])
else:
    menu = "Lançar Questões"

# --- 4. TELA: LANÇAR ---
if menu == "Lançar Questões":
    st.title("📝 Portal de Simulados")
    with st.form("form_lançar"):
        prof = st.text_input("Nome do Professor")
        disc = st.selectbox("Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
        turmas = st.multiselect("Para quais turmas?", ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"])
        enunciado = st.text_area("Enunciado da Questão")
        foto = st.file_uploader("Imagem (Opcional - Máx 10MB)", type=["jpg", "png"])
        
        c1, c2 = st.columns(2)
        with c1: a, b, c = st.text_input("A)"), st.text_input("B)"), st.text_input("C)")
        with c2: d, e, gab = st.text_input("D)"), st.text_input("E)"), st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])
        
        btn_enviar = st.form_submit_button("🚀 SALVAR QUESTÃO")

    if btn_enviar:
        if not prof or not turmas or not enunciado:
            st.warning("Preencha os campos obrigatórios!")
        elif foto and foto.size > 10 * 1024 * 1024:
            st.error("Imagem muito grande! Máximo 10MB.")
        else:
            with st.spinner("Salvando..."):
                url_img = upload_github(foto, f"{datetime.now().timestamp()}.jpg") if foto else ""
                sheet = conectar_google_sheets()
                if sheet:
                    try:
                        for t in turmas:
                            linha = [datetime.now().strftime("%d/%m/%Y %H:%M"), prof, disc, t, enunciado, url_img, a, b, c, d, e, gab]
                            sheet.append_row(linha)
                        st.success(f"✅ Sucesso para as turmas: {', '.join(turmas)}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# --- 5. TELA: VER BANCO (CORRIGIDA) ---
elif menu == "Ver Banco de Questões":
    st.title("📊 Banco de Questões")
    
    with st.spinner("Lendo planilha..."):
        sheet = conectar_google_sheets()
        
    if sheet:
        try:
            dados = sheet.get_all_records()
            if not dados:
                st.info("Planilha vazia.")
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
                
                st.write(f"Encontradas **{len(df_f)}** questões.")
                st.dataframe(df_f)
                
                # Exportação
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("📄 Gerar Word"):
                        doc_p = gerar_word(df_f, "Escola Pe. Constantino")
                        st.download_button("⬇️ Baixar .docx", doc_p, "simulado.docx")
                with c_btn2:
                    csv = df_f.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV", csv, "banco.csv")
        except Exception as e:
            st.error(f"Erro ao processar dados: {e}")
