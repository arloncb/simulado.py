import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime
import pandas as pd
from docx import Document
from io import BytesIO

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Portal Escola Constantino", layout="centered")

# --- 1. VISUAL À PROVA DE ERROS (CSS FORÇADO) ---
st.markdown("""
    <style>
    /* Força fundo branco e texto preto em qualquer modo (claro/escuro) */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, li, div {
        color: #000000 !important;
    }
    /* Estilo dos blocos (Cards) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #F0F2F6 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
        margin-bottom: 10px !important;
    }
    /* Botão Verde */
    .stButton>button {
        width: 100%;
        background-color: #16A34A !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 3.5em !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO ---

def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Acessa exatamente o caminho que você tem nos seus Secrets
        info_gs = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(info_gs, scopes=scope)
        client = gspread.authorize(creds)
        # Pega a URL da planilha que está dentro do bloco gsheets
        return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def upload_github(arquivo, nome_arquivo):
    try:
        token = st.secrets["github_token"]
        # ⚠️ AJUSTE SEU REPOSITÓRIO AQUI:
        repo = "SEU_USUARIO/SEU_REPOSITORIO" 
        url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
        conteudo = base64.b64encode(arquivo.read()).decode()
        payload = {"message": f"Questão: {nome_arquivo}", "content": conteudo}
        headers = {"Authorization": f"token {token}"}
        res = requests.put(url, json=payload, headers=headers)
        return res.json()['content']['download_url'] if res.status_code in [200, 201] else ""
    except:
        return ""

def gerar_word
