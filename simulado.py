import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64
import io
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Portal Simulado - Constantino", 
    layout="wide", 
    page_icon="📝",
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
        if res.status_code in [200, 201]:
            return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}"
        return ""
    except: return ""

# --- FUNÇÃO GERADORA DE PDF (CORRIGIDA) ---
def gerar_pdf_simulado(df_limpo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Largura útil da página (A4 tem 210mm, descontando 10mm de cada margem = 190mm)
    largura_util = 190 

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(largura_util, 10, "Simulado - Escola Padre Constantino", ln=True, align="C")
    pdf.ln(10)

    for i, row in df_limpo.iterrows():
        # Título da Questão
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(largura_util, 8, f"QUESTÃO {i+1} | {row['Disciplina']} - {row['Turma']}")
        
        # Habilidade
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(largura_util, 6, f"Habilidade: {row['Habilidade']}")
        pdf.ln(2)

        # Enunciado
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(largura_util, 7, str(row['Pergunta']))
        pdf.ln(4)
        
        # Alternativas (Uma embaixo da outra)
        pdf.set_font("Helvetica", "", 11)
        for letra in ['A', 'B', 'C', 'D', 'E']:
            texto_alt = f"{letra.lower()}) {row[letra]}"
            pdf.multi_cell(largura_util, 6, str(texto_alt))
        
        pdf.ln(8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Linha divisória
        pdf.ln(5)
        
    return pdf.output()

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: radial-gradient(at 0% 0%, rgba(79, 70, 22, 0.8) 0, transparent 50%), radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }
    .stForm { background: rgba(255, 255, 255, 0.98) !important; padding: 40px !important; border-radius: 25px !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
    h1, h2, h3, .stSubheader { color: white !important; font-weight: 800 !important; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; }
    div.stButton > button:first-child { width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); color: white !important; padding: 15px; border-radius: 12px; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE SESSÃO PARA MEMÓRIA ---
if 'limpar_id' not in st.session_state: st.session_state.limpar_id = 0

# --- MENU ---
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    with st.form("form_professor"):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            prof = st.text_input("Seu Nome:", key="prof_fixo")
            disc = st.selectbox("Sua Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"], key="disc_fixo")
        with col2:
            turma = st.text_input("Série/Turma (Ex: 9 B):", key="turma_fixo")
            hab = st.text_input("Habilidade BNCC:", key=f"hab_{st.session_state.limpar_id}")

        st.markdown("---")
        pergunta = st.text_area("Enunciado da Questão:", height=150, key=f"q_{st.session_state.limpar_id}")
        foto = st.file_uploader("Anexar Imagem:", type=["png", "jpg", "jpeg"], key=f"f_{st.session_state.limpar_id}")
        
        st.markdown("<h4 style='color:black;'>🔘 Alternativas</h4>", unsafe_allow_html=True)
        a = st.text_input("Alternativa A:", key=f"a_{st.session_state.limpar_id}")
        b = st.text_input("Alternativa B:", key=f"b_{st.session_state.limpar_id}")
        c = st.text_input("Alternativa C:", key=f"c_{st.session_state.limpar_id}")
        d = st.text_input("Alternativa D:", key=f"d_{st.session_state.limpar_id}")
        e = st.text_input("Alternativa E:", key=f"e_{st.session_state.limpar_id}")
        gab = st.selectbox("Gabarito:", ["A", "B", "C", "D", "E"], key=f"g_{st.session_state.limpar_id}")

        if st.form_submit_button("💾 SALVAR QUESTÃO"):
            if not prof or disc == "Selecione..." or not pergunta:
                st.error("🚨 Preencha os campos obrigatórios!")
            else:
                l_img = upload_to_github(foto, f"{disc}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg") if foto else ""
                df_antigo = conn.read(worksheet="Página1", ttl=0)
                nova = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor (a)": prof, "Disciplina": disc, "Turma": turma,
                    "Habilidade": hab, "Pergunta": pergunta, "A": a, "B": b, "C": c, "D": d, "E": e, "Correta": gab, "Link Imagem": l_img
                }])
                conn.update(worksheet="Página1", data=pd.concat([df_antigo, nova], ignore_index=True))
                st.session_state.limpar_id += 1
                st.success("✅ Salvo com sucesso! Nome e Disciplina mantidos.")
                st.rerun()

# ==========================================
# PÁGINA 2: COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    senha = st.text_input("Senha de Acesso:", type="password")
    
    if senha == "constantino2026":
        st.success("Acesso Autorizado")
        df = conn.read(worksheet="Página1", ttl=0).fillna("")
        
        if not df.empty:
            c1, c2 = st.columns(2)
            f_d = c1.multiselect("Filtrar Disciplina:", df["Disciplina"].unique())
            f_t = c2.multiselect("Filtrar Turma:", df["Turma"].unique())
            
            dff = df.copy()
            if f_d: dff = dff[dff["Disciplina"].isin(f_d)]
            if f_t: dff = dff[dff["Turma"].isin(f_t)]
            
            st.dataframe(dff, use_container_width=True)
            
            # BOTÕES DE DOWNLOAD
            st.markdown("### 📥 Exportar Simulados")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                pdf_data = gerar_pdf_simulado(dff)
                st.download_button(label="📄 Baixar Prova em PDF", data=pdf_data, file_name="simulado_constantino.pdf", mime="application/pdf")
            with col_d2:
                st.download_button(label="📊 Baixar Tabela Excel (CSV)", data=dff.to_csv(index=False).encode('utf-8'), file_name="simulado.csv", mime="text/csv")
            
            st.markdown("---")
            for i, row in dff.iterrows():
                with st.expander(f"Questão {i+1}: {row['Disciplina']} - {row['Turma']}"):
                    st.write(f"**BNCC:** {row['Habilidade']}")
                    st.info(f"**Pergunta:** {row['Pergunta']}")
                    if row['Link Imagem'] and str(row['Link Imagem']).startswith("http"):
                        st.image(row['Link Imagem'], width=400)
                    st.write(f"a) {row['A']} | b) {row['B']} | c) {row['C']} | d) {row['D']} | e) {row['E']}")
                    st.success(f"Gabarito: {row['Correta']}")
        else: st.info("O banco de dados está vazio.")
    elif senha != "":
        st.error("Chave incorreta!")

st.markdown('<br><p style="text-align:center; color:white;">Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
