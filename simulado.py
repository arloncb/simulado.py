import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
import base64
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Portal Simulado - Constantino", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÕES GITHUB ---
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: Chave 'github_token' não encontrada nos Secrets.")
    st.stop()

# --- CONEXÃO PLANILHA ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO UPLOAD GITHUB ---
def upload_to_github(file, filename):
    try:
        path = f"imagens/{filename}"
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
        content = base64.b64encode(file.getvalue()).decode()
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        data = {"message": f"Upload: {filename}", "content": content, "branch": "main"}
        res = requests.put(url, json=data, headers=headers)
        return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}" if res.status_code in [200, 201] else ""
    except: return ""

# --- FUNÇÃO GERADORA DE PDF ---
def gerar_pdf_bytes(df_limpo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(15)
    largura_util = 180

    def escrever_texto(t, estilo="", tam=11):
        pdf.set_font("Helvetica", estilo, tam)
        pdf.set_x(15)
        pdf.multi_cell(largura_util, 7, str(t).encode('latin-1', 'replace').decode('latin-1'), align='L')

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(largura_util, 10, "Simulado - Escola Pe. Constantino", ln=True, align="C")
    pdf.ln(10)

    for i, row in df_limpo.iterrows():
        escrever_texto(f"QUESTAO {i+1} | {row['Disciplina']} - {row['Turma']}", "B", 12)
        escrever_texto(f"Codigo da Habilidade (Referencial Curricular de MS): {row['Habilidade']}", "I", 10)
        pdf.ln(2)
        escrever_texto(row['Pergunta'], "", 11)
        pdf.ln(4)
        for letra in ['A', 'B', 'C', 'D', 'E']:
            escrever_texto(f"{letra.lower()}) {row[letra]}", "", 11)
        pdf.ln(10)
        pdf.set_x(15)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)
    return bytes(pdf.output())

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%) fixed; }
    .stForm { background: rgba(255, 255, 255, 0.98) !important; padding: 40px !important; border-radius: 25px !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
    h1, h2, h3, .stSubheader { color: white !important; font-weight: 800 !important; text-align: center; }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; font-size: 16px !important; }
    div.stButton > button:first-child { width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); color: white !important; padding: 15px; border-radius: 12px; font-weight: bold; border: none; }
    .instrucao-foto { color: #1e1b4b; font-weight: bold; margin-bottom: -15px; font-size: 16px; }
    .rodape-final { text-align: center
