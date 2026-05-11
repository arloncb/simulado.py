import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from docx import Document
from docx.shared import Inches
from io import BytesIO
from datetime import datetime
import os
import requests
import time

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── FUNÇÃO DE TRATAMENTO DE TEXTO (CORREÇÃO DEFINITIVA) ─────────────────────
def limpar_texto(texto):
    if pd.isna(texto) or texto is None:
        return ""
    t = str(texto).strip()
    substituicoes = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...',
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2026': '...'
    }
    for original, novo in substituicoes.items():
        t = t.replace(original, novo)
    return t.encode('latin-1', 'replace').decode('latin-1')

# ─── FUNÇÃO PARA GERAR DOCX (NOVO PADRÃO SOLICITADO) ─────────────────────────
def gerar_docx_questoes(df_export, titulo="Simulado"):
    doc = Document()
    
    for idx, (_, r) in enumerate(df_export.iterrows(), 1):
        # 1. Disciplina
        doc.add_paragraph(f"Disciplina: {r.get('Disciplina')}")
        
        # 2. Habilidade
        doc.add_paragraph(f"Habilidade: {r.get('Habilidade')}")
        
        # 3. Enunciado
        doc.add_paragraph(limpar_texto(r.get("Pergunta")))
        
        # 4. Imagem (se houver)
        link_img = r.get("Link Imagem")
        if pd.notna(link_img) and str(link_img).strip().lower() not in ["", "nan"]:
            try:
                resp = requests.get(link_img, timeout=10)
                if resp.status_code == 200:
                    img_io = BytesIO(resp.content)
                    doc.add_picture(img_io, width=Inches(4.0))
            except:
                pass 
        
        # 5. Alternativas (uma abaixo da outra)
        for letra in ["A", "B", "C", "D", "E"]:
            alt_conteudo = r.get(letra)
            if pd.notna(alt_conteudo):
                doc.add_paragraph(f"({letra}) {limpar_texto(alt_conteudo)}")
        
        # Espaço entre as questões
        doc.add_paragraph("\n")
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ─── CONSTANTES E CONEXÃO ─────────────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Arte", "Ciências", "Educação Física", "Geografia", "História", "Língua Inglesa", "Língua Portuguesa", "Leitura e Produção de texto", "Matemática"]
SENHA_COORD = "coord2026"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def carregar_dados():
    try: return conn.read(ttl=0)
    except: return None

# ─── INTERFACE ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .header-box {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%);
        border-radius: 12px; padding: 25px; color: white; margin-bottom: 20px;
    }
</style>
<div class="header-box">
    <h1>📚 Portal de Simulados</h1>
    <p>Escola Estadual Padre Constantino de Monte — Maracaju/MS</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📚 SIDE")
    perfil = st.radio("Selecione o Acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"])
    st.divider()
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    with st.form("form_prof", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: nome_p = st.text_input("Nome do(a) Professor(a)*")
        with c2: turma_p = st.selectbox("Turma*", LISTA_TURMAS)
        with c3: disc_p = st.selectbox("Disciplina*", sorted(LISTA_DISCS))
        
        st.divider()
        hab_p = st.text_input("Habilidade MS*")
        enun_p = st.text_area("Pergunta*", height=150)
        link_p = st.text_input("🔗 Link da Imagem (opcional)")
        
        ca, cb = st.columns(2)
        with ca:
            a, b, c = st.text_input("Alt A*"), st.text_input("Alt B*"), st.text_input("Alt C*")
        with cb:
            d, e = st.text_input("Alt D*"), st.text_input("Alt E*")
        
        gab_p = st.radio("✅ Alternativa Correta*", ["A", "B", "C", "D", "E"], horizontal=True)
        btn_enviar = st.form_submit_button("🚀 Enviar Questão")

        if btn_enviar:
            if not all([nome_p, hab_p, enun_p, a, b, c, d, e]):
                st.error("⚠️ Por favor, preencha todos os campos.")
            else:
                with st.spinner("🚀 Salvando..."):
                    time.sleep(1.2)
                    df_atual = carregar_dados()
                    nova_q = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Professor (a)": nome_p, "Disciplina": disc_p, "Turma": turma_p,
                        "Habilidade": hab_p, "Pergunta": enun_p, "A": a, "B": b, "C": c, "D": d, "E": e,
                        "Correta": gab_p, "Link Imagem": link_p
                    }])
                    conn.update(data=
