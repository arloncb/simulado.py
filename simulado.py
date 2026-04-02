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

# --- FUNÇÃO GERADORA DE PDF (VERSÃO BYTES) ---
def gerar_pdf_bytes(df_limpo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Função interna para tratar o texto de forma segura
    def txt(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 10, txt("Simulado - Escola Padre Constantino"), ln=True, align="C")
    pdf.ln(10)

    for i, row in df_limpo.iterrows():
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(190, 8, txt(f"QUESTAO {i+1} | {row['Disciplina']} - {row['Turma']}"))
        
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(190, 6, txt(f"Habilidade: {row['Habilidade']}"))
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(190, 7, txt(row['Pergunta']))
        pdf.ln(4)
        
        for letra in ['A', 'B', 'C', 'D', 'E']:
            pdf.multi_cell(190, 6, txt(f"{letra.lower()}) {row[letra]}"))
        
        pdf.ln(8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    
    # O SEGREDO: converter para bytes que o Streamlit entende
    return bytes(pdf.output())

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%) fixed;
    }
    .stForm { background: rgba(255, 255, 255, 0.98) !important; padding: 40px !important; border-radius: 25px !important; }
    h1, h2, h3, .stSubheader { color: white !important; font-weight: 800 !important; text-align: center; }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; }
    div.stButton > button:first-child { width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); color: white !important; padding: 15px; border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE SESSÃO ---
if 'limpar' not in st.session_state: st.session_state.limpar = 0

# --- MENU ---
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Ir para:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    with st.form("form_v4"):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            prof = st.text_input("Seu Nome:", key="p_fixo")
            disc = st.selectbox("Sua Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"], key="d_fixo")
        with c2:
            turma = st.text_input("Série/Turma:", key="t_fixo")
            hab = st.text_input("Habilidade BNCC:", key=f"h_{st.session_state.limpar}")

        st.markdown("---")
        pergunta = st.text_area("Enunciado:", height=150, key=f"q_{st.session_state.limpar}")
        foto = st.file_uploader("Imagem:", type=["png", "jpg", "jpeg"], key=f"f_{st.session_state.limpar}")
        
        st.markdown("<h4 style='color:black;'>🔘 Alternativas</h4>", unsafe_allow_html=True)
        a = st.text_input("A:", key=f"a_{st.session_state.limpar}")
        b = st.text_input("B:", key=f"b_{st.session_state.limpar}")
        c = st.text_input("C:", key=f"c_{st.session_state.limpar}")
        d = st.text_input("D:", key=f"d_{st.session_state.limpar}")
        e = st.text_input("E:", key=f"e_{st.session_state.limpar}")
        gab = st.selectbox("Gabarito:", ["A", "B", "C", "D", "E"], key=f"g_{st.session_state.limpar}")

        if st.form_submit_button("💾 SALVAR E CONTINUAR"):
            if not prof or disc == "Selecione..." or not pergunta:
                st.error("🚨 Preencha os campos obrigatórios!")
            else:
                img_url = upload_to_github(foto, f"{disc}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg") if foto else ""
                df_old = conn.read(worksheet="Página1", ttl=0)
                nova = pd.DataFrame([{"Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), "Professor (a)": prof, "Disciplina": disc, "Turma": turma, "Habilidade": hab, "Pergunta": pergunta, "A": a, "B": b, "C": c, "D": d, "E": e, "Correta": gab, "Link Imagem": img_url}])
                conn.update(worksheet="Página1", data=pd.concat([df_old, nova], ignore_index=True))
                st.session_state.limpar += 1
                st.success("✅ Salvo! Dados mantidos.")
                st.rerun()

# ==========================================
# PÁGINA 2: COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    if st.text_input("Senha de Acesso:", type="password") == "constantino2026":
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
            st.markdown("### 📥 Exportar")
            col_pdf, col_csv = st.columns(2)
            with col_pdf:
                # O PDF agora é gerado em bytes reais
                pdf_output = gerar_pdf_bytes(dff)
                st.download_button(label="📄 Baixar PDF", data=pdf_output, file_name="simulado.pdf", mime="application/pdf")
            with col_csv:
                st.download_button(label="📊 Baixar Excel (CSV)", data=dff.to_csv(index=False).encode('utf-8'), file_name="simulado.csv", mime="text/csv")
        else: st.info("O banco de dados está vazio.")
    elif st.session_state.get('p_fixo') == "ERRO": st.error("Senha incorreta!")

st.markdown('<br><p style="text-align:center; color:white;">Feito com dedicação Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
