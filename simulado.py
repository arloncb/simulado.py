import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64
import io
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal Simulado - Constantino", layout="wide", initial_sidebar_state="collapsed")

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
def gerar_pdf_simulado(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Simulado - Escola Padre Constantino", ln=True, align="C")
    pdf.ln(10)

    for i, row in df.iterrows():
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(0, 8, f"QUESTÃO {i+1} | {row['Disciplina']} - {row['Turma']}")
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 6, f"Habilidade: {row['Habilidade']}")
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, row['Pergunta'])
        pdf.ln(4)
        
        # Alternativas
        for letra in ['A', 'B', 'C', 'D', 'E']:
            pdf.multi_cell(0, 6, f"{letra.lower()}) {row[letra]}")
        pdf.ln(8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    return pdf.output()

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }
    .stForm { background: rgba(255, 255, 255, 0.98) !important; padding: 40px !important; border-radius: 25px !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
    h1, h2, h3, .stSubheader { color: white !important; font-weight: 800 !important; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; }
    div.stButton > button:first-child { width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); color: white !important; padding: 15px; border-radius: 12px; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE SESSÃO ---
if 'limpar_count' not in st.session_state: st.session_state.limpar_count = 0

# --- MENU ---
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Ir para:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    with st.form("form_v3"):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            prof = st.text_input("Nome do Professor (a):", key="p_nome")
            disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"], key="p_disc")
        with col2:
            turma = st.text_input("Série/Turma:", key="p_turma")
            hab = st.text_input("BNCC:", key=f"h_{st.session_state.limpar_count}")

        st.markdown("---")
        pergunta = st.text_area("Enunciado:", height=150, key=f"q_{st.session_state.limpar_count}")
        foto = st.file_uploader("Imagem:", type=["png", "jpg", "jpeg"], key=f"f_{st.session_state.limpar_count}")
        
        st.markdown("<h4 style='color:black;'>🔘 Alternativas</h4>", unsafe_allow_html=True)
        a = st.text_input("A:", key=f"a_{st.session_state.limpar_count}")
        b = st.text_input("B:", key=f"b_{st.session_state.limpar_count}")
        c = st.text_input("C:", key=f"c_{st.session_state.limpar_count}")
        d = st.text_input("D:", key=f"d_{st.session_state.limpar_count}")
        e = st.text_input("E:", key=f"e_{st.session_state.limpar_count}")
        gab = st.selectbox("Correta:", ["A", "B", "C", "D", "E"], key=f"g_{st.session_state.limpar_count}")

        if st.form_submit_button("💾 SALVAR QUESTÃO"):
            if not prof or disc == "Selecione..." or not pergunta:
                st.error("🚨 Preencha os campos obrigatórios!")
            else:
                l_img = upload_to_github(foto, f"{disc}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg") if foto else ""
                df_a = conn.read(worksheet="Página1", ttl=0)
                nova = pd.DataFrame([{"Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), "Professor (a)": prof, "Disciplina": disc, "Turma": turma, "Habilidade": hab, "Pergunta": pergunta, "A": a, "B": b, "C": c, "D": d, "E": e, "Correta": gab, "Link Imagem": l_img}])
                conn.update(worksheet="Página1", data=pd.concat([df_a, nova], ignore_index=True))
                st.session_state.limpar_count += 1
                st.success("✅ Salvo! Nome e Disciplina mantidos.")
                st.rerun()

# ==========================================
# PÁGINA 2: COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    if st.text_input("Senha:", type="password") == "constantino2026":
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
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 Baixar em PDF (Formatado)", data=gerar_pdf_simulado(dff), file_name="simulado.pdf", mime="application/pdf")
            with col_d2:
                st.download_button("📊 Baixar Excel (CSV)", data=dff.to_csv(index=False).encode('utf-8'), file_name="simulado.csv", mime="text/csv")
        else: st.info("Banco vazio.")
    elif st.session_state.get('pass_input') != "": st.error("Acesso negado.")

st.markdown('<br><p style="text-align:center; color:white;">Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
