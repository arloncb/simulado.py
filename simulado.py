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
    /* Fundo mais claro e limpo */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Cards brancos com sombra para os campos */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }

    /* Títulos e Labels maiores */
    h1 { color: #1e3a8a; font-size: 42px !important; }
    label p { font-size: 20px !important; font-weight: bold; color: #334155; }
    
    /* Customização do Botão */
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        height: 3em;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE APOIO ---

def conectar_google_sheets():
    # Usa os secrets do Streamlit para o Google
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    # Coloque o nome EXATO da sua planilha aqui
    return client.open("NOME_DA_SUA_PLANILHA").get_worksheet(0)

def upload_imagem_github(arquivo, nome_arquivo):
    # Usa o token sem expiração que você gerou
    token = st.secrets["github_token"]
    repo = "SEU_USUARIO/SEU_REPOSITORIO" # Ex: Arlon/ImagensSimulado
    path = f"imagens/{nome_arquivo}"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    
    conteudo = base64.b64encode(arquivo.read()).decode()
    
    payload = {
        "message": f"Upload imagem: {nome_arquivo}",
        "content": conteudo
    }
    headers = {"Authorization": f"token {token}"}
    
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code in [201, 200]:
        return response.json()['content']['download_url']
    return None

# --- 3. INTERFACE DO USUÁRIO ---

st.title("📝 Lançador de Questões")
st.subheader("Portal de Simulados - Escola Pe. Constantino")

with st.container():
    nome_professor = st.text_input("Nome do Professor")
    disciplina = st.selectbox("Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    
    # --- MUDANÇA: MULTISELEÇÃO DE TURMAS ---
    turmas = st.multiselect(
        "Para quais turmas é esta questão?",
        ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"]
    )

st.markdown("---")

with st.container():
    enunciado = st.text_area("Enunciado da Questão", height=150)
    
    # --- MUDANÇA: LIMITE DE 10MB ---
    foto = st.file_uploader("Opcional: Imagem da questão (Máx 10MB)", type=["jpg", "jpeg", "png"])
    
    if foto is not None:
        if foto.size > 10 * 1024 * 1024:
            st.error("🚨 A imagem ultrapassa 10MB! Por favor, reduza o tamanho da foto.")
            foto = None

st.markdown("---")

# Opções de resposta
col1, col2 = st.columns(2)
with col1:
    alt_a = st.text_input("Alternativa A")
    alt_b = st.text_input("Alternativa B")
    alt_c = st.text_input("Alternativa C")
with col2:
    alt_d = st.text_input("Alternativa D")
    alt_e = st.text_input("Alternativa E")
    correta = st.selectbox("Qual a alternativa correta?", ["A", "B", "C", "D", "E"])

# --- 4. LÓGICA DE ENVIO ---

if st.button("🚀 LANÇAR QUESTÃO"):
    if not nome_professor or not turmas or not enunciado:
        st.error("Por favor, preencha o nome, selecione as turmas e digite o enunciado!")
    else:
        with st.spinner("Gravando no sistema... aguarde."):
            try:
                # 1. Faz upload da imagem se houver
                url_foto = ""
                if foto:
                    nome_img = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.name}"
                    url_foto = upload_imagem_github(foto, nome_img)
                
                # 2. Conecta ao Sheets
                sheet = conectar_google_sheets()
                
                # 3. MUDANÇA: SALVAR UMA LINHA PARA CADA TURMA
                for turma in turmas:
                    dados = [
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        nome_professor,
                        disciplina,
                        turma,
                        enunciado,
                        url_foto,
                        alt_a, alt_b, alt_c, alt_d, alt_e,
                        correta
                    ]
                    sheet.append_row(dados)
                
                st.success(f"✅ Sucesso! Questão lançada para {len(turmas)} turmas.")
                st.balloons()
                
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
