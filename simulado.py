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

# ─── FUNÇÃO DE TRATAMENTO DE TEXTO (CORREÇÃO DE CARACTERES) ──────────────────
def limpar_texto(texto):
    if pd.isna(texto) or texto is None:
        return ""
    t = str(texto).strip()
    # Mapeamento de caracteres Unicode que costumam quebrar o FPDF/Word
    substituicoes = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...',
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2026': '...'
    }
    for original, novo in substituicoes.items():
        t = t.replace(original, novo)
    return t

# ─── FUNÇÕES DE EXPORTAÇÃO (DOCX) ─────────────────────────────────────────────
def gerar_docx_questoes(df_para_exportar, titulo_doc="Banco de Questões"):
    doc = Document()
    doc.add_heading(f'SIDE — {titulo_doc}', 0)
    doc.add_paragraph(f"Escola Estadual Padre Constantino de Monte")
    doc.add_paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    for idx, (_, r) in enumerate(df_para_exportar.iterrows(), 1):
        doc.add_heading(f"QUESTÃO {idx:02d}", level=1)
        doc.add_paragraph(f"Disciplina: {r.get('Disciplina')} | Turma: {r.get('Turma')}")
        doc.add_paragraph(f"Habilidade: {r.get('Habilidade')}")
        
        # Pergunta
        p = doc.add_paragraph()
        p.add_run(limpar_texto(r.get("Pergunta"))).bold = True
        
        # Imagem Real (Tratamento para não sair 'nan' e inserir a foto)
        link_img = r.get("Link Imagem")
        if pd.notna(link_img) and str(link_img).strip().lower() not in ["", "nan"]:
            try:
                resp = requests.get(link_img, timeout=10)
                if resp.status_code == 200:
                    img_io = BytesIO(resp.content)
                    doc.add_picture(img_io, width=Inches(4.0))
            except:
                pass # Pula silenciosamente se o link for inválido
            
        for letra in ["A", "B", "C", "D", "E"]:
            doc.add_paragraph(f"({letra}) {limpar_texto(r.get(letra))}")
        
        doc.add_paragraph(f"Gabarito: {r.get('Correta')}")
        doc.add_paragraph("-" * 25)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ─── CONSTANTES E CONEXÃO ─────────────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
# "Ensino Religioso" removido conforme solicitado
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
    
    with st.form("form_professor", clear_on_submit=True):
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
        
        submit_p = st.form_submit_button("🚀 Enviar Questão")
        
        if submit_p:
            if not all([nome_p, hab_p, enun_p, a, b, c, d, e]):
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
            else:
                with st.spinner("🚀 Sincronizando com o banco de dados..."):
                    time.sleep(1.5) # Efeito visual
                    df_atual = carregar_dados()
                    nova_q = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Professor (a)": nome_p, "Disciplina": disc_p, "Turma": turma_p,
                        "Habilidade": hab_p, "Pergunta": enun_p, "A": a, "B": b, "C": c, "D": d, "E": e,
                        "Correta": gab_p, "Link Imagem": link_p
                    }])
                    conn.update(data=pd.concat([df_atual, nova_q], ignore_index=True))
                    st.balloons()
                    st.toast("Questão salva com sucesso!", icon='✅')
                    st.success("✨ Excelente! A questão foi registrada.")
    
    # Exportação individual (Docx) para o professor
    if enun_p:
        st.divider()
        st.caption("📄 Deseja uma cópia desta questão?")
        temp_df = pd.DataFrame([{
            "Professor (a)": nome_p, "Disciplina": disc_p, "Turma": turma_p,
            "Habilidade": hab_p, "Pergunta": enun_p, "A": a, "B": b, "C": c, "D": d, "E": e,
            "Correta": gab_p, "Link Imagem": link_p
        }])
        doc_prof = gerar_docx_questoes(temp_df, "Cópia de Questão")
        st.download_button("⬇️ Baixar esta Questão (.docx)", doc_prof, "Minha_Questao.docx", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL COORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Portal da Coordenação")
    senha = st.text_input("Chave de Acesso:", type="password")
    
    if senha == SENHA_COORD:
        df = carregar_dados()
        if df is not None and not df.empty:
            st.markdown("### 🔍 Filtros Estratégicos")
            f1, f2, f3 = st.columns(3)
            with f1: turmas_f = st.multiselect("Filtrar Turmas:", sorted(df["Turma"].unique()))
            with f2: discs_f = st.multiselect("Filtrar Disciplinas:", sorted(df["Disciplina"].unique()))
            with f3: profs_f = st.multiselect("Filtrar Professor(a):", sorted(df["Professor (a)"].unique()))
            
            df_v = df.copy()
            if turmas_f: df_v = df_v[df_v["Turma"].isin(turmas_f)]
            if discs_f: df_v = df_v[df_v["Disciplina"].isin(discs_f)]
            if profs_f: df_v = df_v[df_v["Professor (a)"].isin(profs_f)]
            
            st.metric("Total de Questões Selecionadas", len(df_v))
            st.dataframe(df_v, use_container_width=True, hide_index=True)
            
            st.divider()
            st.markdown("### ⬇️ Exportação de Arquivos")
            exp1, exp2 = st.columns(2)
            
            with exp1:
                if st.button("📄 Gerar Banco em PDF", use_container_width=True):
                    try:
                        pdf = FPDF()
                        pdf.set_auto_page_break(auto=True, margin=20)
                        pdf.add_page()
                        
                        # Fix para o erro de espaço horizontal:
                        w_util = pdf.w - 2 * pdf.l_margin
                        
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(w_util, 10, "BANCO DE QUESTÕES - SIDE", ln=True, align="C")
                        pdf.ln(5)
                        
                        for i, (_, r) in enumerate(df_v.iterrows(), 1):
                            pdf.set_font("Arial", "B", 11)
                            pdf.multi_cell(w_util, 6, limpar_texto(f"QUESTÃO {i:02d} - {r['Turma']} ({r['Disciplina']})"))
                            pdf.set_font("Arial", "", 11)
                            pdf.multi_cell(w_util, 6, limpar_texto(r.get('Pergunta')))
                            pdf.ln(2)
                            for l in ["A", "B", "C", "D", "E"]:
                                pdf.multi_cell(w_util, 6, limpar_texto(f"({l}) {r.get(l)}"))
                            pdf.ln(4)
                            pdf.set_draw_color(220, 220, 220)
                            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin, pdf.get_y())
                            pdf.ln(4)
                        
                        st.download_button("⬇️ Baixar Banco PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "Banco_SIDE.pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"Erro ao processar PDF: {e}")

            with exp2:
                with st.spinner("Processando imagens e gerando Word..."):
                    doc_banco = gerar_docx_questoes(df_v, "Banco de Simulados")
                    st.download_button("⬇️ Baixar Banco Word (Docx)", doc_banco, "Banco_SIDE_Completo.docx", use_container_width=True)
