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

# --- 1. VISUAL REFORÇADO (CSS) ---
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

# --- 3. FUNÇÃO DO WORD (COM SEPARAÇÃO DE LINHA) ---
def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    doc.add_paragraph(f'Escola Pe. Constantino de Monte - Gerado em: {datetime.now().strftime("%d/%m/%Y")}')
    
    # Padroniza os nomes das colunas
    df.columns = [str(c).strip().lower() for c in df.columns]

    for i, row in df.iterrows():
        # Disciplina
        disc = str(row.get('disciplina', '-')).upper()
        doc.add_heading(f'Questão {i+1} - {disc}', level=2)
        
        # Habilidade
        hab = str(row.get('habilidade', 'Não informada'))
        doc.add_paragraph(f'
