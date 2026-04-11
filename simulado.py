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

# --- 1. VISUAL LIMPO E FORTE (CSS) ---
# Removi excessos para evitar que a tela fique preta
st.markdown("""
    <style>
    /* Forçando o fundo a ser sempre claro */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Forçando toda a fonte a ser preta para não sumir */
    h1, h2, h3, p, label, span, div {
        color: #111111 !important;
    }

    /* Estilizando os blocos de perguntas (Cards) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #F8F9FA !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1px solid #DDDDDD !important;
        margin-bottom: 10px !important;
    }

    /* Botão Verde de Envio */
    .stButton>button {
        width: 100%;
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        height: 3em !important;
        border-radius: 8px !important;
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
        # Tenta pegar a URL da planilha dentro do bloco gsheets
        return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)
    except Exception as e:
        st.error(f"Erro na conexão com Google: {e}")
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

def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    doc.add_paragraph(f'Escola Pe. Constantino de Monte - {datetime.now().strftime("%d/%m/%Y")}')
    
    # Padroniza as colunas (Ex: "enunciado" vira "Enunciado")
    df.columns = [str(c).strip().capitalize() for c in df.columns]

    for i, row in df
