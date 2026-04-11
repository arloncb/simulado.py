import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Portal Simulado - Escola Constantino", layout="centered")

# --- 1. VISUAL PREMIUM COM CONTRASTE FORÇADO (CSS) ---
st.markdown("""
    <style>
    /* Fundo da página - Cinza bem clarinho para dar contraste */
    .stApp {
        background-color: #f8f9fa !important;
    }
    
    /* Títulos Principais - Azul Marinho Forte */
    h1, h2, h3 {
        color: #1e3a8a !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Cards Brancos com Sombra Forte */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #ffffff !important;
        padding: 25px !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        margin-bottom: 15px !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* FORÇANDO COR DO TEXTO (Labels e Parágrafos) */
    label p, .stMarkdown p, p {
        color: #1e293b !important; /* Azul acinzentado bem escuro */
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* Estilizando os Campos de Entrada (Inputs) para não sumirem */
    input, textarea, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 2px solid #cbd5e1 !important; /* Borda cinza definida */
        border-radius: 10px !important;
    }

    /* Botão de Enviar - Verde Vibrante */
    .stButton>button {
        width: 100%;
        background-color: #16a34a !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 3.5em !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3) !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #15803d !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO (Mantenha as suas credenciais aqui) ---

def conectar_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    # Substitua pelo nome exato da sua planilha
    return client.open("NOME_DA_SUA_PLANILHA").get_worksheet(0)

def upload_github(arquivo, nome_arquivo):
    token = st.secrets["github_token"]
    repo = "SEU_USUARIO/SEU_REPOSITORIO" 
    path = f"imagens/{nome_arquivo}"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    conteudo = base64.b64encode(arquivo.read()).decode()
    payload = {"message": f"Upload: {nome_arquivo}", "content": conteudo}
    headers = {"Authorization": f"token {token}"}
    res = requests.put(url, json=payload, headers=headers)
    return res.json()['content']['download_url'] if res.status_code in [200, 201] else None

# --- 3. INTERFACE ---

st.title("📝 Lançador de Questões")
st.write("Preencha os dados abaixo para compor o simulado.")

# Container 1: Identificação
with st.container():
    nome_prof = st.text_input("👤 Nome do Professor", placeholder="Ex: Arlon")
    disciplina = st.selectbox("📚 Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    
    # MULTISELEÇÃO DE TURMAS
    turmas_selecionadas = st.multiselect(
        "🏫 Selecione a(s) Turma(s)", 
        ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"],
        help="Você pode marcar várias turmas de uma vez!"
    )

# Container 2: Conteúdo
with st.container():
    enunciado = st.text_area("✍️ Enunciado da Questão", placeholder="Digite aqui o texto da pergunta...")
    
    # LIMITE DE 10MB
    foto = st.file_uploader("🖼️ Adicionar Imagem (Opcional - Máx 10MB)", type=["jpg", "jpeg", "png"])
    
    if foto:
        if foto.size > 10 * 1024 * 1024:
            st.error("🚨 Imagem muito grande! O limite é 10MB.")
            foto = None
        else:
            st.info(f"Tamanho da imagem: {foto.size / 1024 / 1024:.2f} MB")

# Container 3: Alternativas
with st.container():
    st.write("🎯 **Alternativas de Resposta**")
    c1, c2 = st.columns(2)
    with c1:
        a = st.text_input("A)")
        b = st.text_input("B)")
        c = st.text_input("C)")
    with c2:
        d = st.text_input("D)")
        e = st.text_input("E)")
        correta = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])

# --- 4. BOTÃO DE ENVIO ---
if st.button("🚀 FINALIZAR E LANÇAR QUESTÃO"):
    if not nome_prof or not turmas_selecionadas or not enunciado:
        st.warning("⚠️ Por favor, preencha todos os campos obrigatórios!")
    else:
        with st.spinner("Processando..."):
            try:
                url_img = upload_github(foto, f"{datetime.now().timestamp()}.jpg") if foto else ""
                sheet = conectar_google_sheets()
                
                # Salva uma linha para cada turma selecionada
                for t in turmas_selecionadas:
                    linha = [datetime.now().strftime("%d/%m/%Y %H:%M"), nome_prof, disciplina, t, enunciado, url_img, a, b, c, d, e, correta]
                    sheet.append_row(linha)
                
                st.success(f"✅ Questão enviada com sucesso para as turmas: {', '.join(turmas_selecionadas)}")
                st.balloons()
            except Exception as error:
                st.error(f"❌ Erro ao salvar: {error}")
