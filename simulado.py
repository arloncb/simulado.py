import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime
import pandas as pd
from docx import Document
from io import BytesIO

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Portal Escola Constantino", layout="centered")

# --- 1. VISUAL ESTABILIZADO (CSS) ---
st.markdown("""
    <style>
    /* Fundo claro padrão */
    .stApp { background-color: white; }
    
    /* Forçar textos principais para Preto */
    h1, h2, h3, h4, p, label { color: #111111 !important; }
    
    /* Estilo dos Cards de Pergunta */
    .st-emotion-cache-1ky8h6r { 
        background-color: #f1f3f5; 
        padding: 20px; 
        border-radius: 10px; 
    }
    
    /* Botão de Enviar */
    .stButton>button {
        width: 100%;
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO ---

def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Pega a chave dos secrets
        info_gs = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(info_gs, scopes=scope)
        client = gspread.authorize(creds)
        # Abre a planilha pelo link salvo nos secrets
        return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)
    except Exception as e:
        st.error(f"Erro ao conectar com a Planilha: {e}")
        return None

def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    # Padroniza nomes das colunas
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    for i, row in df.iterrows():
        doc.add_heading(f'Questão {i+1}', level=2)
        doc.add_paragraph(str(row.get('Enunciado', 'Sem texto')))
        doc.add_paragraph(f"A) {row.get('A', '')} | B) {row.get('B', '')} | C) {row.get('C', '')}")
        doc.add_paragraph(f"D) {row.get('D', '')} | E) {row.get('E', '')}")
        doc.add_paragraph(f"Gabarito: {row.get('Gabarito', '')}")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. MENU LATERAL ---
st.sidebar.header("🔐 Área Restrita")
senha = st.sidebar.text_input("Senha da Coordenação", type="password")
acesso_coord = (senha == "constantino2026")

if acesso_coord:
    st.sidebar.success("Acesso Liberado!")
    menu = st.sidebar.radio("Navegação", ["Lançar Questões", "Ver Banco de Questões"])
else:
    menu = "Lançar Questões"

# --- 4. TELA: LANÇAR QUESTÕES ---
if menu == "Lançar Questões":
    st.title("📝 Lançador de Simulados")
    
    with st.form("form_questoes"):
        prof = st.text_input("Nome do Professor")
        disc = st.selectbox("Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
        turmas = st.multiselect("Para quais turmas?", ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"])
        enunciado = st.text_area("Enunciado da Questão")
        
        col1, col2 = st.columns(2)
        with col1:
            a, b, c = st.text_input("A)"), st.text_input("B)"), st.text_input("C)")
        with col2:
            d, e = st.text_input("D)"), st.text_input("E)")
            correta = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])
        
        enviar = st.form_submit_button("🚀 SALVAR QUESTÃO")

    if enviar:
        if not prof or not turmas or not enunciado:
            st.warning("Preencha os campos obrigatórios!")
        else:
            sheet = conectar_google_sheets()
            if sheet:
                try:
                    for t in turmas:
                        linha = [datetime.now().strftime("%d/%m/%Y %H:%M"), prof, disc, t, enunciado, "", a, b, c, d, e, correta]
                        sheet.append_row(linha)
                    st.success("✅ Questão salva!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

# --- 5. TELA: VER BANCO (COORDENAÇÃO) ---
elif menu == "Ver Banco de Questões":
    st.title("📊 Banco de Questões")
    
    # Checkpoint 1: Conexão
    with st.spinner("Buscando dados na planilha..."):
        sheet = conectar_google_sheets()
        
    if sheet:
