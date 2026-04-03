import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
import base64
import io
import time
from fpdf import FPDF
from docx import Document
from docx.shared import Inches

# 1. CONFIGURAÇÃO INICIAL (Obrigatório ser o primeiro comando)
st.set_page_config(page_title="Portal Constantino", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO E CONFIGURAÇÕES
conn = st.connection("gsheets", type=GSheetsConnection)
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: Chave 'github_token' não encontrada nos Secrets.")
    st.stop()

# --- FUNÇÕES DE APOIO ---
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
    for i, row in df_limpo.reset_index(drop=True).iterrows():
        escrever_texto(f"QUESTAO {i+1} | {row['Disciplina']} - {row['Turma']}", "B", 12)
        escrever_texto(f"Habilidade: {row['Habilidade']}", "I", 10)
        pdf.ln(2)
        escrever_texto(row['Pergunta'], "", 11)
        link_img = row.get('Link Imagem', '')
        if link_img and str(link_img).startswith("http"):
            try:
                response = requests.get(link_img)
                if response.status_code == 200:
                    img_data = io.BytesIO(response.content); pdf.image(img_data, x=15, w=100); pdf.ln(5)
            except: pass
        for letra in ['A', 'B', 'C', 'D', 'E']:
            escrever_texto(f"{letra.lower()}) {row[letra]}", "", 11)
        pdf.ln(10); pdf.set_x(15); pdf.line(15, pdf.get_y(), 195, pdf.get_y()); pdf.ln(8)
    return bytes(pdf.output())

def gerar_docx_bytes(df_limpo):
    doc = Document()
    doc.add_heading('Simulado - Escola Pe. Constantino', 0)
    for i, row in df_limpo.reset_index(drop=True).iterrows():
        doc.add_heading(f"QUESTAO {i+1} | {row['Disciplina']} - {row['Turma']}", level=2)
        p_hab = doc.add_paragraph(); run_hab = p_hab.add_run(f"Habilidade: {row['Habilidade']}"); run_hab.italic = True
        doc.add_paragraph(row['Pergunta'])
        link_img = row.get('Link Imagem', '')
        if link_img and str(link_img).startswith("http"):
            try:
                res = requests.get(link_img)
                if res.status_code == 200:
                    img_io = io.BytesIO(res.content); doc.add_picture(img_io, width=Inches(4))
            except: pass
        for letra in ['A', 'B', 'C', 'D', 'E']: doc.add_paragraph(f"{letra.lower()}) {row[letra]}")
        doc.add_paragraph("-" * 40)
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

# --- DESIGN (Estilo simplificado para evitar erros de aspas) ---
css = """
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%) fixed; }
.stForm { background: white !important; padding: 30px !important; border-radius: 20px !important; }
h1, h2, h3 { color: white !important; text-align: center; }
.stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold; }
.rodape { text-align: center; color: white; padding: 20px; font-weight: bold; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if 'limpar' not in st.session_state: st.session_state.limpar = 0

pagina = st.sidebar.radio("Navegação:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title
