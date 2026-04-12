import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime
import pandas as pd
from docx import Document
from docx.shared import Inches
from io import BytesIO

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Portal Escola Constantino", layout="centered")

# --- 1. VISUAL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, label { color: #111111 !important; }
    .stButton>button {
        width: 100%;
        background-color: #16A34A !important;
        color: white !important;
        font-weight: bold;
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
        st.error(f"Erro de Conexão Google: {e}")
        return None

def upload_github(arquivo, nome_arquivo):
    try:
        token = st.secrets["github_token"]
        # ⚠️ AJUSTE SEU REPOSITÓRIO AQUI:
        repo = "SEU_USUARIO/SEU_REPOSITORIO" 
        url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
        conteudo = base64.b64encode(arquivo.read()).decode()
        payload = {"message": f"Upload: {nome_arquivo}", "content": conteudo}
        headers = {"Authorization": f"token {token}"}
        res = requests.put(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            return res.json()['content']['download_url']
        return ""
    except:
        return ""

# --- 3. GERADOR DE WORD (FOCO EM IMAGENS E ESTRUTURA) ---
def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    doc.add_paragraph(f'Escola Pe. Constantino de Monte - {datetime.now().strftime("%d/%m/%Y")}')
    
    # Padronização de colunas para evitar erros de busca
    df.columns = [str(c).strip().lower() for c in df.columns]

    for i, row in df.iterrows():
        # Cabeçalho: Disciplina
        disc_nome = str(row.get('disciplina', '-')).upper()
        doc.add_heading(f'Questão {i+1} - {disc_nome}', level=2)
        
        # Habilidade
        habilidade_txt = str(row.get('habilidade', 'Não informada'))
        doc.add_paragraph(f'Habilidade: {habilidade_txt}')
        
        # Espaço entre habilidade e enunciado
        doc.add_paragraph("")
        
        # Enunciado
        enunciado_base = row.get('enunciado', row.get('pergunta', 'Sem texto'))
        doc.add_paragraph(str(enunciado_base))
        
        # --- LÓGICA DE IMAGEM ---
        # Busca link na coluna 'foto' ou 'imagem'
        link_foto = str(row.get('foto', row.get('imagem', ''))).strip()
        if link_foto.startswith('http'):
            try:
                r = requests.get(link_foto, timeout=10)
                if r.status_code == 200:
                    img_stream = BytesIO(r.content)
                    doc.add_picture(img_stream, width=Inches(3.5))
            except:
                doc.add_paragraph("[Imagem não disponível para este arquivo]")

        # Alternativas Empilhadas
        doc.add_paragraph(f"A) {row.get('a', '')}")
        doc.add_paragraph(f"B) {row.get('b', '')}")
        doc.add_paragraph(f"C) {row.get('c', '')}")
        doc.add_paragraph(f"D) {row.get('d', '')}")
        doc.add_paragraph(f"E) {row.get('e', '')}")
        
        doc.add_paragraph("-" * 40)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. INTERFACE ---
st.sidebar.header("🔐 Área Restrita")
senha = st.sidebar.text_input("Senha", type="password")
acesso_coord = (senha == "constantino2026")

menu = st.sidebar.radio("Navegação", ["Lançar Questões", "Ver Banco"]) if acesso_coord else "Lançar Questões"

if menu == "Lançar Questões":
    st.title("📝 Lançador de Simulados")
    with st.form("form_lancar"):
        prof = st.text_input("Nome do Professor")
        c_p1, c_p2 = st.columns(2)
        with c_p1: 
            d_sel = st.selectbox("Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
        with c_p2: 
            h_in = st.text_input("Habilidade (BNCC)")
            
        t_sel = st.multiselect("Turmas", ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"])
        enunc = st.text_area("Enunciado")
        foto_up = st.file_uploader("Imagem (Opcional)", type=["jpg", "png", "jpeg"])
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            alt_a, alt_b, alt_c = st.text_input("A)"), st.text_input("B)"), st.text_input("C)")
        with col_a2:
            alt_d, alt_e = st.text_input("D)"), st.text_input("E)")
            gab_in = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])
        
        btn_save = st.form_submit_button("🚀 SALVAR QUESTÃO")

    if btn_save:
        if not prof or not t_sel or not enunc:
            st.warning("Preencha os campos obrigatórios!")
        else:
            with st.spinner("Processando..."):
                sheet = conectar_google_sheets()
                if sheet:
                    url_i = upload_github(foto_up, f"{datetime.now().timestamp()}.jpg") if foto_up else ""
                    dh = datetime.now().strftime("%d/%m/%Y %H:%M")
                    for t in t_sel:
                        # Ordem: Data, Professor, Disciplina, Habilidade, Turma, Enunciado, Foto, A, B, C, D, E, Gabarito
                        linha = [dh, prof, d_sel, h_in, t, enunc, url_i, alt_a, alt_b, alt_c, alt_d, alt_e, gab_in]
                        sheet.append_row(linha)
                    st.success("✅ Questão e Imagem salvas!")

elif menu == "Ver Banco":
    st.title("📊 Banco de Questões")
    sheet = conectar_google_sheets()
    if sheet:
        df_banco = pd.DataFrame(sheet.get_all_records())
        if not df_banco.empty:
            st.dataframe(df_banco)
            if st.button("📄 Gerar Word com Imagens"):
                doc_file = gerar_word(df_banco, "Escola Constantino")
                st.download_button("⬇️ Baixar Docx", doc_file, "simulado.docx")
