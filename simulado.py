import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from docx import Document
from io import BytesIO
from datetime import datetime
import os
import urllib.request
import time

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── FUNÇÃO DE TRATAMENTO DE TEXTO (CORREÇÃO DO ?) ───────────────────────────
def limpar_texto_pdf(texto):
    """Substitui caracteres especiais que quebram o PDF por caracteres padrão."""
    if pd.isna(texto) or texto is None:
        return ""
    t = str(texto).strip()
    # Substitui aspas inteligentes e traços longos que geram o "?"
    substituicoes = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...',
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"'
    }
    for original, novo in substituicoes.items():
        t = t.replace(original, novo)
    return t

# ─── FUNÇÃO PARA GERAR DOCX (PROFESSOR) ──────────────────────────────────────
def gerar_docx(dados):
    doc = Document()
    doc.add_heading('SIDE — Portal de Simulados', 0)
    doc.add_paragraph(f"Professor(a): {dados['prof_nome']}")
    doc.add_paragraph(f"Disciplina: {dados['prof_disc']} | Turma: {dados['prof_turma']}")
    doc.add_paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    doc.add_paragraph("-" * 30)
    
    doc.add_heading(f"Habilidade: {dados['q_hab']}", level=2)
    doc.add_paragraph(limpar_texto_pdf(dados['q_enun']))
    
    for letra in ['A', 'B', 'C', 'D', 'E']:
        doc.add_paragraph(f"({letra}) {limpar_texto_pdf(dados['q_' + letra.lower()])}")
    
    doc.add_paragraph(f"\nGabarito: {dados['gabarito']}")
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ─── CSS CUSTOMIZADO ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .page-header {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: white;
    }
    .page-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
    .page-header p  { margin: 4px 0 0; opacity: 0.8; font-size: 0.95rem; }
    .section-label {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em;
        text-transform: uppercase; color: #6b7280; margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES (Ensino Religioso Removido) ──────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Educação Física", "Leitura e Produção de texto"]
SENHA_COORD = "coord2026"

# Inicialização do session_state
if "log_atividades" not in st.session_state: st.session_state.log_atividades = []

# ─── CONEXÃO ──────────────────────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=30)
def carregar_dados():
    try: return conn.read(ttl=0)
    except: return None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 SIDE")
    perfil = st.radio("Acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"], label_visibility="collapsed")
    st.divider()
    st.caption(f"Maracaju/MS | {datetime.now().strftime('%d/%m/%Y')}")

st.markdown('<div class="page-header"><h1>📚 Portal de Simulados</h1><p>Escola Estadual Padre Constantino de Monte — SIDE</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DO PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    
    with st.form("form_simulado", clear_on_submit=False):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: nome_professor = st.text_input("Nome do(a) Professor(a)*")
        with c2: turma = st.selectbox("Turma*", LISTA_TURMAS)
        with c3: disciplina = st.selectbox("Disciplina*", LISTA_DISCS)

        st.divider()
        habilidade = st.text_input("Habilidade MS*")
        enunciado = st.text_area("Pergunta*", height=150)
        link_imagem = st.text_input("🔗 Link da Imagem (opcional)")
        
        ca, cb = st.columns(2)
        with ca:
            alt_a = st.text_input("Alternativa A*")
            alt_b = st.text_input("Alternativa B*")
            alt_c = st.text_input("Alternativa C*")
        with cb:
            alt_d = st.text_input("Alternativa D*")
            alt_e = st.text_input("Alternativa E*")

        gabarito = st.radio("✅ Alternativa Correta*", ["A", "B", "C", "D", "E"], horizontal=True)
        btn_salvar = st.form_submit_button("🚀 Cadastrar Questão")

        if btn_salvar:
            if not nome_professor or not habilidade or not enunciado or not all([alt_a, alt_b, alt_c, alt_d, alt_e]):
                st.error("⚠️ Preencha todos os campos obrigatórios.")
            else:
                with st.spinner("🚀 Processando e salvando questão..."):
                    time.sleep(1.5) # Efeito visual
                    try:
                        df_atual = carregar_dados()
                        nova_linha = pd.DataFrame([{
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Professor (a)": nome_professor,
                            "Disciplina": disciplina, "Turma": turma,
                            "Habilidade": habilidade, "Pergunta": enunciado,
                            "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                            "Correta": gabarito, "Link Imagem": link_imagem
                        }])
                        conn.update(data=pd.concat([df_atual, nova_linha], ignore_index=True))
                        st.balloons()
                        st.toast("Questão enviada!", icon='✅')
                        st.success("✨ Salvo com sucesso!")
                    except Exception as e: st.error(f"Erro: {e}")

    if enunciado:
        st.markdown("---")
        docx_file = gerar_docx({
            'prof_nome': nome_professor, 'prof_disc': disciplina, 'prof_turma': turma,
            'q_hab': habilidade, 'q_enun': enunciado, 'q_a': alt_a, 'q_b': alt_b,
            'q_c': alt_c, 'q_d': alt_d, 'q_e': alt_e, 'gabarito': gabarito
        })
        st.download_button("⬇️ Baixar Questão em Word (Docx)", data=docx_file, file_name=f"Questao_{turma}.docx", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DA COORDENAÇÃO (COM CORREÇÃO DE CARACTERES NO PDF)
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Área da Coordenação")
    senha = st.text_input("Senha:", type="password")

    if senha == SENHA_COORD:
        df = carregar_dados()
        if df is not None and not df.empty:
            st.metric("Total de Questões", len(df))
            st.dataframe(df, use_container_width=True)

            if st.button("📄 Gerar Banco de Questões (PDF)"):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=20)
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "BANCO DE QUESTÕES - SIDE", ln=True, align="C")
                pdf.ln(10)

                for idx, (_, r) in enumerate(df.iterrows(), 1):
                    pdf.set_font("Arial", "B", 11)
                    # Aplica a limpeza de texto aqui para evitar o "?"
                    titulo = f"QUESTÃO {idx:02d} ({limpar_texto_pdf(r.get('Disciplina'))})"
                    pdf.multi_cell(0, 6, titulo)
                    
                    pdf.set_font("Arial", "", 11)
                    pergunta = limpar_texto_pdf(r.get("Pergunta"))
                    pdf.multi_cell(0, 6, pergunta)
                    pdf.ln(2)

                    for l in ["A", "B", "C", "D", "E"]:
                        alt = limpar_texto_pdf(r.get(l))
                        pdf.cell(10)
                        pdf.multi_cell(0, 6, f"({l}) {alt}")
                    pdf.ln(5)

                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("⬇️ Baixar PDF Corrigido", data=pdf_bytes, file_name="banco_questoes.pdf", use_container_width=True)
