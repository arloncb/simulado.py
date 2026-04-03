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

# 1. CONFIGURAÇÃO (Deve ser a primeira linha)
st.set_page_config(page_title="Portal Constantino", layout="wide")

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("Chave 'github_token' não encontrada.")
    st.stop()

# --- FUNÇÕES ---
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

def gerar_pdf(df_limpo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(180, 10, "Simulado - Escola Pe. Constantino", ln=True, align="C")
    pdf.ln(10)
    for i, row in df_limpo.reset_index(drop=True).iterrows():
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(180, 7, f"QUESTÃO {i+1} | {row['Disciplina']} - {row['Turma']}".encode('latin-1', 'replace').decode('latin-1'))
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(180, 7, f"Habilidade: {row['Habilidade']}".encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(180, 7, str(row['Pergunta']).encode('latin-1', 'replace').decode('latin-1'))
        
        link = row.get('Link Imagem', '')
        if link and str(link).startswith("http"):
            try:
                res = requests.get(link)
                if res.status_code == 200:
                    pdf.image(io.BytesIO(res.content), x=15, w=90); pdf.ln(5)
            except: pass
            
        for l in ['A', 'B', 'C', 'D', 'E']:
            pdf.multi_cell(180, 7, f"{l.lower()}) {row[l]}".encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5); pdf.line(15, pdf.get_y(), 195, pdf.get_y()); pdf.ln(5)
    return bytes(pdf.output())

def gerar_docx(df_limpo):
    doc = Document()
    doc.add_heading('Simulado - Escola Pe. Constantino', 0)
    for i, row in df_limpo.reset_index(drop=True).iterrows():
        doc.add_heading(f"QUESTÃO {i+1} | {row['Disciplina']} - {row['Turma']}", level=2)
        doc.add_paragraph(f"Habilidade: {row['Habilidade']}").italic = True
        doc.add_paragraph(str(row['Pergunta']))
        link = row.get('Link Imagem', '')
        if link and str(link).startswith("http"):
            try:
                res = requests.get(link)
                if res.status_code == 200:
                    doc.add_picture(io.BytesIO(res.content), width=Inches(4))
            except: pass
        for l in ['A', 'B', 'C', 'D', 'E']:
            doc.add_paragraph(f"{l.lower()}) {row[l]}")
        doc.add_paragraph("-" * 30)
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

# --- DESIGN (Sem aspas triplas para não bugar) ---
st.markdown('<style>[data-testid="stAppViewContainer"]{background:linear-gradient(135deg,#1e1b4b 0%,#3b82f6 100%) fixed;}.stForm{background:white!important;padding:25px!important;border-radius:15px!important;}h1,h2,h3{color:white!important;text-align:center;}.stTextInput label,.stSelectbox label,.stTextArea label{color:black!important;font-weight:bold;}</style>', unsafe_allow_html=True)

if 'limpar' not in st.session_state: st.session_state.limpar = 0

menu = st.sidebar.radio("Navegação:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO
# ==========================================
if menu == "📝 Enviar Questão":
    st.title("📝 SIMULADO - Lançamento de Questões")
    with st.form("form_v19"):
        st.subheader("📋 Identificação")
        c1, c2 = st.columns(2)
        prof = c1.text_input("Seu Nome:", key="p_fixo")
        disc = c1.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"], key="d_fixo")
        # AJUSTE: 3° ano EM
        turmas = ["Selecione...", "4° ano", "5° ano", "6° ano", "7° ano", "8° ano", "9° ano", "1° ano EM", "2° ano EM", "3° ano EM"]
        turma = c2.selectbox("Série/Turma:", turmas, key="t_fixo")
        hab = c2.text_input("Habilidade (MS):", key=f"h_{st.session_state.limpar}")
        
        pergunta = st.text_area("Enunciado:", height=150, key=f"q_{st.session_state.limpar}")
        foto = st.file_uploader("Imagem (Opcional):", type=["png", "jpg", "jpeg"], key=f"f_{st.session_state.limpar}")
        
        st.write("---")
        a = st.text_input("A:", key=f"a1_{st.session_state.limpar}")
        b = st.text_input("B:", key=f"b1_{st.session_state.limpar}")
        c = st.text_input("C:", key=f"c1_{st.session_state.limpar}")
        d = st.text_input("D:", key=f"d1_{st.session_state.limpar}")
        e = st.text_input("E:", key=f"e1_{st.session_state.limpar}")
        gab = st.selectbox("Gabarito:", ["A", "B", "C", "D", "E"], key=f"g1_{st.session_state.limpar}")

        if st.form_submit_button("💾 SALVAR QUESTÃO"):
            if not prof or disc == "Selecione..." or turma == "Selecione..." or not pergunta:
                st.error("Preencha tudo!")
            else:
                with st.status("🚀 Salvando...") as status:
                    url = upload_to_github(foto, f"{disc}_{int(time.time())}.jpg") if foto else ""
                    df_old = conn.read(worksheet="Página1", ttl=0)
                    nova = pd.DataFrame([{"Data": pd.Timestamp.now().strftime("%d/%m/%Y"), "Professor (a)": prof, "Disciplina": disc, "Turma": turma, "Habilidade": hab, "Pergunta": pergunta, "A": a, "B": b, "C": c, "D": d, "E": e, "Correta": gab, "Link Imagem": url}])
                    conn.update(worksheet="Página1", data=pd.concat([df_old, nova], ignore_index=True))
                    status.update(label="✅ Sucesso!", state="complete", expanded=False)
                st.toast("Enviado!"); time.sleep(1); st.session_state.limpar += 1; st.rerun()

# ==========================================
# PÁGINA 2: COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área da Coordenação")
    if st.text_input("Senha:", type="password") == "constantino2026":
        df_base = conn.read(worksheet="Página1", ttl=0).fillna("")
        if not df_base.empty:
            f_d = st.multiselect("Filtrar Disciplinas:", df_base["Disciplina"].unique())
            f_t = st.multiselect("Filtrar Turmas:", df_base["Turma"].unique())
            dff = df_base.copy()
            if f_d: dff = dff[dff["Disciplina"].isin(f_d)]
            if f_t: dff = dff[dff["Turma"].isin(f_t)]
            if f_t: dff['Turma'] = pd.Categorical(dff['Turma'], categories=f_t, ordered=True)
            if f_d: dff['Disciplina'] = pd.Categorical(dff['Disciplina'], categories=f_d, ordered=True)
            dff = dff.sort_values(by=['Turma', 'Disciplina'])
            
            st.dataframe(dff, use_container_width=True)
            c1, c2 = st.columns(2)
            c1.download_button("📄 PDF", gerar_pdf(dff), "simulado.pdf")
            c2.download_button("📘 Word", gerar_docx(dff), "simulado.docx")
        else: st.info("Vazio.")

st.markdown('<p style="text-align:center;color:white;font-weight:bold;">Feito com carinho pela Equipe Pe. Constantino ❤️</p>', unsafe_allow_html=True)
