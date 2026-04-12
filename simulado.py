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

# --- CONFIGURAÇÕES BÁSICAS ---
st.set_page_config(page_title="Portal Constantino", layout="centered")

st.markdown("""
    <style>
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
        scope = [
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ]
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
        # ⚠️ MANTENHA SEU REPOSITÓRIO AQUI:
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

# --- GERAR WORD ---
def gerar_word(df, titulo_doc):
    doc = Document()
    
    txt_tit = f'Simulado - {titulo_doc}'
    dt_hoje = datetime.now().strftime("%d/%m/%Y")
    txt_cab = f'Escola Pe. Constantino de Monte - Gerado: {dt_hoje}'
    
    doc.add_heading(txt_tit, 0)
    doc.add_paragraph(txt_cab)

    for i, row in df.iterrows():
        disc = str(row.get('disciplina', '-')).upper()
        txt_q = f'Questão {i+1} - {disc}'
        doc.add_heading(txt_q, level=2)
        
        hab = str(row.get('habilidade', 'Não informada'))
        doc.add_paragraph(f'Habilidade: {hab}')
        
        doc.add_paragraph("") 
        
        enunc = row.get('enunciado', row.get('pergunta', 'Sem texto'))
        doc.add_paragraph(str(enunc))
        
        url_foto = str(row.get('foto', row.get('imagem', ''))).strip()
        if url_foto.startswith('http'):
