import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64

# 1. CONFIGURAÇÃO DA PÁGINA (Barra lateral inicia recolhida)
st.set_page_config(
    page_title="Portal Simulado - Constantino", 
    layout="wide", 
    page_icon="📝",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÕES DO GITHUB ---
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: Chave 'github_token' não encontrada no Streamlit Secrets.")
    st.stop()

# --- CONEXÃO COM PLANILHA ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO DE UPLOAD PARA GITHUB ---
def upload_to_github(file, filename):
    try:
        path = f"imagens/{filename}"
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
        content = base64.b64encode(file.getvalue()).decode()
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "message": f"Upload: {filename}",
            "content": content,
            "branch": "main"
        }
        res = requests.put(url, json=data, headers=headers)
        if res.status_code in [200, 201]:
            return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}"
        return ""
    except:
        return ""

# --- DESIGN PREMIUM (CSS) ---
st.markdown("""
    <style>
    /* Fundo Mesh Gradient */
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: 
            radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(219, 39, 119, 0.8) 0, transparent 50%), 
            radial-gradient(at 0% 100%, rgba(37, 99, 235, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }
    /* Card Branco */
    .stForm {
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 30px !important;
        border-radius: 25px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    }
    /* Títulos */
    h1, h2, h3, .stSubheader {
        color: white !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
        text-align: center;
    }
    /* Labels em preto */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: black !important;
        font-weight: bold !important;
    }
    /* Botão */
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        font-weight: bold;
        padding: 15px;
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.markdown("<h2 style='color:white;'>Menu</h2>", unsafe_allow_html=True)
pagina = st.sidebar.radio("Escolha a página:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO DE QUESTÕES
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    with st.form("form_professor", clear_on_submit=True):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            prof = st.text_input("Nome do Professor (a):")
            disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"])
        with c2:
            turma = st.text_input("Série e Letra (Ex: 7° A):")
            hab = st.text_input("Habilidade (BNCC):")

        st.markdown("---")
        st.
