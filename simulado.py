import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from docx import Document # Nova importação
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

# ─── FUNÇÃO PARA GERAR DOCX ──────────────────────────────────────────────────
def gerar_docx(dados):
    doc = Document()
    doc.add_heading('SIDE — Portal de Simulados', 0)
    doc.add_paragraph(f"Professor(a): {dados['prof_nome']}")
    doc.add_paragraph(f"Disciplina: {dados['prof_disc']} | Turma: {dados['prof_turma']}")
    doc.add_paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    doc.add_paragraph("-" * 30)
    
    doc.add_heading(f"Habilidade: {dados['q_hab']}", level=2)
    doc.add_paragraph(dados['q_enun'])
    
    for letra in ['A', 'B', 'C', 'D', 'E']:
        doc.add_paragraph(f"({letra}) {dados['q_' + letra.lower()]}")
    
    doc.add_paragraph(f"\nGabarito: {dados['gabarito']}")
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ─── FUNÇÃO DE AUTO-CURA (FONTES) ─────────────────────────────────────────────
def garantir_fontes():
    fontes = {
        "DejaVuSans.ttf": "https://github.com/reingart/pyfpdf/raw/master/font/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf": "https://github.com/reingart/pyfpdf/raw/master/font/dejavu/DejaVuSans-Bold.ttf"
    }
    for nome, url in fontes.items():
        if not os.path.exists(nome):
            try:
                urllib.request.urlretrieve(url, nome)
            except:
                pass 

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
_defaults = {"prof_nome": "", "prof_turma": "6° A", "prof_disc": "Língua Portuguesa", "q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": "", "q_e": "", "q_imagem": ""}
for k, v in _defaults.items():
    if k not in st.session_state: 
        st.session_state[k] = v

if "log_atividades" not in st.session_state:
    st.session_state.log_atividades = []

# ─── CONEXÃO ──────────────────────────────────────────────────────────────────
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro de conexão: {e}")

@st.cache_data(ttl=30)
def carregar_dados():
    if conn:
        try: return conn.read(ttl=0)
        except: return None
    return None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 SIDE")
    perfil = st.radio("Acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"], label_visibility="collapsed")
    st.divider()
    st.caption(f"📍 Maracaju/MS | 🗓️ {datetime.now().strftime('%d/%m/%Y')}")

st.markdown('<div class="page-header"><h1>📚 Portal de Simulados</h1><p>Escola Estadual Padre Constantino de Monte — SIDE</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DO PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    
    with st.form("form_simulado", clear_on_submit=False):
        st.markdown('<p class="section-label">👤 Identificação</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: nome_professor = st.text_input("Nome do(a) Professor(a)*", value=st.session_state["prof_nome"])
        with c2: 
            idx_t = LISTA_TURMAS.index(st.session_state["prof_turma"]) if st.session_state["prof_turma"] in LISTA_TURMAS else 0
            turma = st.selectbox("Turma*", LISTA_TURMAS, index=idx_t)
        with c3:
            idx_d = LISTA_DISCS.index(st.session_state["prof_disc"]) if st.session_state["prof_disc"] in LISTA_DISCS else 0
            disciplina = st.selectbox("Disciplina*", LISTA_DISCS, index=idx_d)

        st.divider()
        st.markdown('<p class="section-label">📝 Questão</p>', unsafe_allow_html=True)
        habilidade = st.text_input("Habilidade MS*", value=st.session_state["q_hab"])
        enunciado = st.text_area("Pergunta*", value=st.session_state["q_enun"], height=150)
        
        ca, cb = st.columns(2)
        with ca:
            alt_a = st.text_input("Alternativa A*", value=st.session_state["q_a"])
            alt_b = st.text_input("Alternativa B*", value=st.session_state["q_b"])
            alt_c = st.text_input("Alternativa C*", value=st.session_state["q_c"])
        with cb:
            alt_d = st.text_input("Alternativa D*", value=st.session_state["q_d"])
            alt_e = st.text_input("Alternativa E*", value=st.session_state["q_e"])

        gabarito = st.radio("✅ Alternativa Correta*", ["A", "B", "C", "D", "E"], horizontal=True)
        btn_salvar = st.form_submit_button("🚀 Cadastrar Questão")

        if btn_salvar:
            if not nome_professor or not habilidade or not enunciado or not all([alt_a, alt_b, alt_c, alt_d, alt_e]):
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
            elif conn:
                with st.spinner("🚀 Processando sua questão..."):
                    time.sleep(1.5) # Animação de espera
                    try:
                        df_atual = carregar_dados()
                        if df_atual is None or df_atual.empty:
                            df_atual = pd.DataFrame(columns=["Data", "Professor (a)", "Disciplina", "Turma", "Habilidade", "Pergunta", "A", "B", "C", "D", "E", "Correta", "Link Imagem"])
                        
                        nova_linha = pd.DataFrame([{
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Professor (a)": nome_professor,
                            "Disciplina": disciplina,
                            "Turma": turma,
                            "Habilidade": habilidade,
                            "Pergunta": enunciado,
                            "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                            "Correta": gabarito, "Link Imagem": ""
                        }])
                        
                        conn.update(data=pd.concat([df_atual, nova_linha], ignore_index=True))
                        st.session_state.log_atividades.append(f"{datetime.now().strftime('%H:%M')} - {nome_professor} cadastrou questão.")
                        st.toast(f"Questão de {disciplina} enviada!", icon='✅')
                        st.balloons()
                        st.success("✨ Questão salva com sucesso no banco de dados!")
                        # st.rerun() # Opcional: remover se quiser manter os dados na tela para baixar o docx
                    except Exception as e: st.error(f"Erro: {e}")

    # Novo: Se houver dados preenchidos, permite baixar em DOCX
    if enunciado:
        st.markdown("---")
        st.markdown('<p class="section-label">📄 Exportação Rápida</p>', unsafe_allow_html=True)
        dados_doc = {
            'prof_nome': nome_professor, 'prof_disc': disciplina, 'prof_turma': turma,
            'q_hab': habilidade, 'q_enun': enunciado, 'q_a': alt_a, 'q_b': alt_b,
            'q_c': alt_c, 'q_d': alt_d, 'q_e': alt_e, 'gabarito': gabarito
        }
        docx_file = gerar_docx(dados_doc)
        st.download_button(
            label="⬇️ Baixar esta Questão em Word (.docx)",
            data=docx_file,
            file_name=f"Questao_{disciplina}_{turma}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

# (O restante do código para a Coordenação permanece igual, mas agora sem a opção de planilha no perfil do Professor)
