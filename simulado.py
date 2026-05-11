import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from docx import Document
from docx.shared import Inches # Para redimensionar a imagem no Word
from io import BytesIO
from datetime import datetime
import os
import urllib.request
import requests # Necessário para baixar a imagem para o Word
import time

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── TRATAMENTO DE TEXTO (EVITAR O ?) ────────────────────────────────────────
def limpar_texto(texto):
    if pd.isna(texto) or texto is None:
        return ""
    t = str(texto).strip()
    substituicoes = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...',
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"'
    }
    for original, novo in substituicoes.items():
        t = t.replace(original, novo)
    return t

# ─── FUNÇÃO PARA GERAR DOCX (BANCO COMPLETO) ─────────────────────────────────
def gerar_docx_banco(df_filtrado):
    doc = Document()
    doc.add_heading('SIDE — Banco de Questões', 0)
    doc.add_paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    for idx, (_, r) in enumerate(df_filtrado.iterrows(), 1):
        doc.add_heading(f"QUESTÃO {idx:02d}", level=1)
        doc.add_paragraph(f"Disciplina: {r.get('Disciplina')} | Turma: {r.get('Turma')}")
        doc.add_paragraph(f"Habilidade: {r.get('Habilidade')}")
        
        # Enunciado
        p = doc.add_paragraph()
        p.add_run(limpar_texto(r.get("Pergunta"))).bold = True
        
        # Lógica da Imagem (Insere a imagem real e remove o 'nan')
        link_img = r.get("Link Imagem")
        if pd.notna(link_img) and str(link_img).strip().lower() not in ["", "nan"]:
            try:
                response = requests.get(link_img, timeout=10)
                if response.status_code == 200:
                    img_bytes = BytesIO(response.content)
                    doc.add_picture(img_bytes, width=Inches(4.0)) # Define largura de ~10cm
                else:
                    doc.add_paragraph(f"(Link de imagem inacessível: {link_img})")
            except:
                doc.add_paragraph("(Erro ao processar imagem)")
            
        for l in ["A", "B", "C", "D", "E"]:
            doc.add_paragraph(f"({l}) {limpar_texto(r[l])}")
        
        doc.add_paragraph(f"Gabarito: {r.get('Correta')}")
        doc.add_paragraph("-" * 25)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ─── CONSTANTES ───────────────────────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Educação Física", "Leitura e Produção de texto"]
SENHA_COORD = "coord2026"

# ─── CONEXÃO ──────────────────────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def carregar_dados():
    try: return conn.read(ttl=0)
    except: return None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 SIDE")
    perfil = st.radio("Acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"], label_visibility="collapsed")
    st.divider()
    st.caption(f"📍 Maracaju/MS | {datetime.now().strftime('%d/%m/%Y')}")

st.markdown('<div class="page-header" style="background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%); border-radius: 12px; padding: 24px; color: white;"><h1>📚 Portal de Simulados</h1><p>Escola Estadual Padre Constantino de Monte — SIDE</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DO PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    with st.form("form_simulado", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: nome_prof = st.text_input("Nome do(a) Professor(a)*")
        with c2: turma_p = st.selectbox("Turma*", LISTA_TURMAS)
        with c3: disc_p = st.selectbox("Disciplina*", LISTA_DISCS)
        
        st.divider()
        hab = st.text_input("Habilidade MS*")
        enun = st.text_area("Pergunta*", height=150)
        img = st.text_input("🔗 Link da Imagem (opcional)")
        
        ca, cb = st.columns(2)
        with ca:
            a, b, c = st.text_input("Alt A*"), st.text_input("Alt B*"), st.text_input("Alt C*")
        with cb:
            d, e = st.text_input("Alt D*"), st.text_input("Alt E*")
        
        gab = st.radio("✅ Correta*", ["A", "B", "C", "D", "E"], horizontal=True)
        btn = st.form_submit_button("🚀 Cadastrar Questão")

        if btn:
            if not all([nome_prof, hab, enun, a, b, c, d, e]):
                st.error("⚠️ Preencha todos os campos obrigatórios.")
            else:
                with st.spinner("🚀 Enviando para o banco de dados..."):
                    time.sleep(1.2)
                    df_at = carregar_dados()
                    nova = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Professor (a)": nome_prof, "Disciplina": disc_p, "Turma": turma_p,
                        "Habilidade": hab, "Pergunta": enun, "A": a, "B": b, "C": c, "D": d, "E": e,
                        "Correta": gab, "Link Imagem": img
                    }])
                    conn.update(data=pd.concat([df_at, nova], ignore_index=True))
                    st.balloons()
                    st.toast("Sucesso!", icon='✅')
                    st.success("✨ Questão salva com sucesso!")

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DA COORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Área da Coordenação")
    senha = st.text_input("Senha de acesso:", type="password")

    if senha == SENHA_COORD:
        df = carregar_dados()
        if df is not None and not df.empty:
            st.markdown("### 🔍 Filtros")
            f1, f2, f3 = st.columns(3)
            with f1: sel_turma = st.multiselect("Filtrar Turma:", sorted(df["Turma"].unique()))
            with f2: sel_disc = st.multiselect("Filtrar Disciplina:", sorted(df["Disciplina"].unique()))
            with f3: sel_prof = st.multiselect("Filtrar Professor(a):", sorted(df["Professor (a)"].unique()))
            
            df_v = df.copy()
            if sel_turma: df_v = df_v[df_v["Turma"].isin(sel_turma)]
            if sel_disc: df_v = df_v[df_v["Disciplina"].isin(sel_disc)]
            if sel_prof: df_v = df_v[df_v["Professor (a)"].isin(sel_prof)]

            st.metric("Questões Filtradas", len(df_v))
            st.dataframe(df_v, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### ⬇️ Gerar Documentos")
            exp1, exp2 = st.columns(2)
            
            with exp1:
                if st.button("📄 Exportar para PDF", use_container_width=True):
                    # Mantive o PDF apenas com texto limpo para evitar problemas de caractere
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, "BANCO DE QUESTÕES - SIDE", ln=True, align="C")
                    pdf.ln(5)
                    for i, (_, r) in enumerate(df_v.iterrows(), 1):
                        pdf.set_font("Arial", "B", 11)
                        pdf.multi_cell(0, 6, limpar_texto(f"QUESTÃO {i:02d} - {r['Turma']} ({r['Disciplina']})"))
                        pdf.set_font("Arial", "", 11)
                        pdf.multi_cell(0, 6, limpar_texto(r['Pergunta']))
                        pdf.ln(2)
                        for l in ["A", "B", "C", "D", "E"]:
                            pdf.multi_cell(0, 6, limpar_texto(f"({l}) {r[l]}"))
                        pdf.ln(4)
                    st.download_button("⬇️ Baixar PDF", data=pdf.output(dest='S').encode('latin-1', 'replace'), file_name="simulado_side.pdf", use_container_width=True)

            with exp2:
                # O Docx agora baixa e insere a imagem automaticamente
                with st.spinner("Preparando arquivo Word com imagens..."):
                    docx_banco = gerar_docx_banco(df_v)
                st.download_button(
                    label="⬇️ Baixar Banco em Word (Docx)",
                    data=docx_banco,
                    file_name=f"Banco_SIDE_Completo.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
