import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Portal Simulado - Escola Constantino", layout="centered")

# --- 1. VISUAL PREMIUM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9 !important; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Segoe UI', sans-serif; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #ffffff !important;
        padding: 25px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
        margin-bottom: 15px !important;
        border: 1px solid #e2e8f0 !important;
    }
    label p, .stMarkdown p, p {
        color: #1e293b !important;
        font-size: 19px !important;
        font-weight: 600 !important;
    }
    input, textarea, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #059669 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 3.5em !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO CORRIGIDAS ---

def conectar_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Acessando o caminho correto nos seus Secrets
    info_gs = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(info_gs, scopes=scope)
    client = gspread.authorize(creds)
    # Busca a URL que está dentro do bloco gsheets
    return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)

def upload_github(arquivo, nome_arquivo):
    token = st.secrets["github_token"]
    # ⚠️ AJUSTE AQUI SEU USUARIO/REPOSITORIO
    repo = "SEU_USUARIO/SEU_REPOSITORIO" 
    url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
    conteudo = base64.b64encode(arquivo.read()).decode()
    payload = {"message": f"Questão: {nome_arquivo}", "content": conteudo}
    headers = {"Authorization": f"token {token}"}
    res = requests.put(url, json=payload, headers=headers)
    return res.json()['content']['download_url'] if res.status_code in [200, 201] else ""

# --- 3. INTERFACE ---

st.title("📝 Portal de Simulados")
st.write("Escola Padre Constantino de Monte")

with st.container():
    prof = st.text_input("👤 Nome do Professor")
    disciplina = st.selectbox("📚 Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    turmas = st.multiselect("🏫 Para quais turmas?", ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"])

with st.container():
    enunciado = st.text_area("✍️ Enunciado da Questão")
    foto = st.file_uploader("🖼️ Imagem (Máx 10MB)", type=["jpg", "jpeg", "png"])
    if foto and foto.size > 10 * 1024 * 1024:
        st.error("🚨 Imagem muito grande! Escolha uma de até 10MB.")
        foto = None

with st.container():
    st.write("🎯 **Alternativas**")
    c1, c2 = st.columns(2)
    with c1:
        a, b, c = st.text_input("A)"), st.text_input("B)"), st.text_input("C)")
    with c2:
        d, e = st.text_input("D)"), st.text_input("E)")
        gabarito = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])

# --- 4. ENVIO ---

if st.button("🚀 FINALIZAR E LANÇAR"):
    if not prof or not turmas or not enunciado:
        st.warning("⚠️ Preencha os campos obrigatórios!")
    else:
        with st.spinner("Gravando dados..."):
            try:
                url_img = upload_github(foto, f"{datetime.now().timestamp()}.jpg") if foto else ""
                sheet = conectar_google_sheets()
                for t in turmas:
                    linha = [datetime.now().strftime("%d/%m/%Y %H:%M"), prof, disciplina, t, enunciado, url_img, a, b, c, d, e, gabarito]
                    sheet.append_row(linha)
                st.success(f"✅ Enviado para: {', '.join(turmas)}")
                st.balloons()
            except Exception as err:
                st.error(f"❌ Erro: {err}")
