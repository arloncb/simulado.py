import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime
import pandas as pd
from docx import Document
from docx.shared import Inches  # <--- NOVA FERRAMENTA PARA IMAGENS
from io import BytesIO

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Portal Escola Constantino", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span, div { color: #000000 !important; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #F8F9FA !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
        margin-bottom: 10px !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #16A34A !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO ---
def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        info_gs = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(info_gs, scopes=scope)
        client = gspread.authorize(creds)
        url_plan = info_gs["spreadsheet"]
        return client.open_by_url(url_plan).get_worksheet(0)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def upload_github(arquivo, nome_arquivo):
    try:
        token = st.secrets["github_token"]
        repo = "SEU_USUARIO/SEU_REPOSITORIO" # ⚠️ AJUSTE AQUI SE NECESSÁRIO
        url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
        conteudo = base64.b64encode(arquivo.read()).decode()
        payload = {"message": f"Upload: {nome_arquivo}", "content": conteudo}
        headers = {"Authorization": f"token {token}"}
        res = requests.put(url, json=payload, headers=headers)
        return res.json()['content']['download_url'] if res.status_code in [200, 201] else ""
    except:
        return ""

# --- GERAR WORD (AGORA COM IMAGENS) ---
def gerar_word(df, titulo_doc):
    doc = Document()
    
    txt_tit = f'Simulado - {titulo_doc}'
    dt_hoje = datetime.now().strftime("%d/%m/%Y")
    txt_cab = f'Escola Pe. Constantino de Monte - Gerado: {dt_hoje}'
    
    doc.add_heading(txt_tit, 0)
    doc.add_paragraph(txt_cab)
    
    df.columns = [str(c).strip().lower() for c in df.columns]

    for i, row in df.iterrows():
        disc = str(row.get('disciplina', '-')).upper()
        txt_q = f'Questão {i+1} - {disc}'
        doc.add_heading(txt_q, level=2)
        
        hab = str(row.get('habilidade', 'Não informada'))
        doc.add_paragraph(f'Habilidade: {hab}')
        doc.add_paragraph("") 
        
        enunc = row.get('enunciado', row.get('pergunta', 'Sem texto'))
        doc.add_paragraph(str(enunc))
        
        # ---> MÁGICA DA IMAGEM <---
        url_foto = str(row.get('foto', row.get('imagem', ''))).strip()
        if url_foto.startswith('http'):
            try:
                # Baixa a imagem da internet
                req_img = requests.get(url_foto, timeout=5)
                if req_img.status_code == 200:
                    img_io = BytesIO(req_img.content)
                    # Cola no Word com 3.5 polegadas de largura
                    doc.add_picture(img_io, width=Inches(3.5)) 
            except:
                doc.add_paragraph("[Erro ao carregar a imagem da questão]")
        
        doc.add_paragraph(f"A) {row.get('a', '')}")
        doc.add_paragraph(f"B) {row.get('b', '')}")
        doc.add_paragraph(f"C) {row.get('c', '')}")
        doc.add_paragraph(f"D) {row.get('d', '')}")
        doc.add_paragraph(f"E) {row.get('e', '')}")
        
        doc.add_paragraph("-" * 40)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- MENU LATERAL ---
st.sidebar.header("🔐 Coordenação")
senha = st.sidebar.text_input("Senha", type="password")
acesso_coord = (senha == "constantino2026")

if acesso_coord:
    st.sidebar.success("Acesso Liberado!")
    menu = st.sidebar.radio("Navegação", ["Lançar", "Banco"])
else:
    menu = "Lançar"

# --- TELA: LANÇAR ---
if menu == "Lançar":
    st.title("📝 Lançador de Simulados")
    with st.form("form_lancar"):
        prof = st.text_input("Nome do Professor")
        c_f1, c_f2 = st.columns(2)
        
        l_disc = ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"]
        with c_f1:
            disc = st.selectbox("Disciplina", l_disc)
        with c_f2:
            hab_in = st.text_input("Habilidade (Ex: EF06MA01)")
            
        l_turmas = ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"]
        turmas = st.multiselect("Para quais turmas?", l_turmas)
        
        enunc = st.text_area("Enunciado da Questão")
        foto = st.file_uploader("Imagem da Questão (Máx 10MB)", type=["jpg", "png", "jpeg"])
        
        c1, c2 = st.columns(2)
        with c1: 
            a = st.text_input("Alternativa A")
            b = st.text_input("Alternativa B")
            c = st.text_input("Alternativa C")
        with c2: 
            d = st.text_input("Alternativa D")
            e = st.text_input("Alternativa E")
            gab = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])
        
        btn_env = st.form_submit_button("🚀 SALVAR QUESTÃO")

    if btn_env:
        if not prof or not turmas or not enunc:
            st.warning("⚠️ Preencha Nome, Turmas e Enunciado!")
        else:
            with st.spinner("Enviando foto e salvando dados..."):
                sheet = conectar_google_sheets()
                if sheet:
                    try:
                        # Faz o upload da foto se ela existir
                        url_i = upload_github(foto, f"{datetime.now().timestamp()}.jpg") if foto else ""
                        dh = datetime.now().strftime("%d/%m/%Y %H:%M")
                        
                        for t in turmas:
                            # A url da foto (url_i) agora é salva na coluna correta (Coluna F)
                            linha = [dh, prof, disc, hab_in, t, enunc, url_i, a, b, c, d, e, gab]
                            sheet.append_row(linha)
                        
                        st.success("✅ Salvo com sucesso!")
                        st.balloons()
                    except Exception as err:
                        st.error(f"Erro: {err}")

# --- TELA: BANCO ---
elif menu == "Banco":
    st.title("📊 Gestão de Questões")
    
    with st.spinner("Lendo banco de dados..."):
        sheet = conectar_google_sheets()
        
    if sheet:
        try:
            dados = sheet.get_all_records()
            if not dados:
                st.info("Nenhuma questão encontrada.")
            else:
                df = pd.DataFrame(dados)
                
                st.write("🔍 **Filtros**")
                cf1, cf2 = st.columns(2)
                
                opc_t = list(df['Turma'].unique())
                with cf1: 
                    f_t = st.multiselect("Turma", options=opc_t)
                    
                opc_d = list(df['Disciplina'].unique())
                with cf2: 
                    f_d = st.multiselect("Disciplina", options=opc_d)
                
                df_f = df.copy()
                if f_t: df_f = df_f[df_f['Turma'].isin(f_t)]
                if f_d: df_f = df_f[df_f['Disciplina'].isin
