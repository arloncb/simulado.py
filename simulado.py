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

# --- FUNÇÃO GERADORA DE PDF (AGORA COM IMAGEM) ---
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
        escrever_texto(f"QUESTÃO {i+1} | {row['Disciplina']} - {row['Turma']}", "B", 12)
        escrever_texto(f"Código da Habilidade (Referencial Curricular de MS): {row['Habilidade']}", "I", 10)
        pdf.ln(2)
        escrever_texto(row['Pergunta'], "", 11)
        pdf.ln(2)

        # LÓGICA DE IMAGEM NO PDF
        link_img = row.get('Link Imagem', '')
        if link_img and str(link_img).startswith("http"):
            try:
                response = requests.get(link_img)
                if response.status_code == 200:
                    img_data = io.BytesIO(response.content)
                    pdf.image(img_data, x=15, w=100) # Insere a imagem com 10cm de largura
                    pdf.ln(5)
            except:
                escrever_texto("[Imagem não carregada no PDF]", "I", 8)

        for letra in ['A', 'B', 'C', 'D', 'E']:
            escrever_texto(f"{letra.lower()}) {row[letra]}", "", 11)
        
        pdf.ln(10)
        pdf.set_x(15)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)
    return bytes(pdf.output())

# --- FUNÇÃO GERADORA DE WORD (AGORA COM IMAGEM) ---
def gerar_docx_bytes(df_limpo):
    doc = Document()
    doc.add_heading('Simulado - Escola Pe. Constantino', 0)
    for i, row in df_limpo.reset_index(drop=True).iterrows():
        doc.add_heading(f"QUESTÃO {i+1} | {row['Disciplina']} - {row['Turma']}", level=2)
        p_hab = doc.add_paragraph()
        run_hab = p_hab.add_run(f"Código da Habilidade (Referencial Curricular de MS): {row['Habilidade']}")
        run_hab.italic = True
        doc.add_paragraph(row['Pergunta'])

        # LÓGICA DE IMAGEM NO WORD
        link_img = row.get('Link Imagem', '')
        if link_img and str(link_img).startswith("http"):
            try:
                response = requests.get(link_img)
                if response.status_code == 200:
                    img_data = io.BytesIO(response.content)
                    doc.add_picture(img_data, width=Inches(4)) # Insere a imagem no Word
            except:
                doc.add_paragraph("[Imagem não disponível]")

        for letra in ['A', 'B', 'C', 'D', 'E']:
            doc.add_paragraph(f"{letra.lower()}) {row[letra]}")
        doc.add_paragraph("-" * 40)
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%) fixed; }
    .stForm { background: rgba(255, 255, 255, 0.98) !important; padding: 40px !important; border-radius: 25px !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
    h1, h2, h3, .stSubheader { color: white !important; font-weight: 800 !important; text-align: center; }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; font-size: 16px !important; }
    div.stButton > button:first-child { width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); color: white !important; padding: 15px; border-radius: 12px; font-weight: bold; border: none; }
    .instrucao-foto { color: #1e1b4b; font-weight: bold; margin-bottom: -15px; font-size: 16px; }
    .rodape-final { text-align: center; color: white; font-weight: bold; padding: 30px; font-size: 18px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

if 'limpar' not in st.session_state: st.session_state.limpar = 0

st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

if pagina == "📝 Enviar Questão":
    st.title("📝 SIMULADO - Lançamento de Questões")
    st.subheader("Escola Pe. Constantino")
    with st.form("form_v8"):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            prof = st.text_input("Seu Nome:", key="p_fixo")
            disc = st.selectbox("Sua Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"], key="d_fixo")
        with c2:
            turma = st.text_input("Série/Turma:", key="t_fixo")
            hab = st.text_input("Código da Habilidade (Referencial Curricular de MS):", key=f"h_{st.session_state.limpar}")
        st.markdown("---")
        pergunta = st.text_area("Enunciado da Questão:", height=150, key=f"q_{st.session_state.limpar}")
        st.markdown('<p class="instrucao-foto">Adicione uma imagem em sua questão aqui:</p>', unsafe_allow_html=True)
        foto = st.file_uploader("", type=["png", "jpg", "jpeg"], key=f"f_{st.session_state.limpar}")
        st.markdown("---")
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
                with st.status("🚀 Processando lançamento...", expanded=True) as status:
                    img_url = upload_to_github(foto, f"{disc}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg") if foto else ""
                    df_old = conn.read(worksheet="Página1", ttl=0)
                    nova = pd.DataFrame([{"Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), "Professor (a)": prof, "Disciplina": disc, "Turma": turma, "Habilidade": hab, "Pergunta": pergunta, "A": a, "B": b, "C": c, "D": d, "E": e, "Correta": gab, "Link Imagem": img_url}])
                    conn.update(worksheet="Página1", data=pd.concat([df_old, nova], ignore_index=True))
                    status.update(label="✅ Questão enviada com sucesso!", state="complete", expanded=False)
                st.toast("Sucesso! Próxima questão...", icon='📝')
                time.sleep(1.5)
                st.session_state.limpar += 1
                st.rerun()
else:
    st.title("📋 Área da Coordenação")
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
            dff = dff.sort_values(by=['Turma', 'Disciplina'])
            st.dataframe(dff, use_container_width=True)
            st.markdown("### 📥 Exportar Questões Filtradas")
            col_pdf, col_word, col_excel = st.columns(3)
            with col_pdf:
                st.download_button(label="📄 Baixar PDF", data=gerar_pdf_bytes(dff), file_name="simulado_constantino.pdf", mime="application/pdf")
            with col_word:
                st.download_button(label="📘 Baixar Word (DOCX)", data=gerar_docx_bytes(dff), file_name="simulado_constantino.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            with col_excel:
                st.download_button(label="📊 Baixar Excel (CSV)", data=dff.to_csv(index=False).encode('utf-8'), file_name="simulado.csv", mime="text/csv")
        else: st.info("Banco vazio.")
    elif senha != "": st.error("Senha incorreta!")

st.markdown('<div class="rodape-final">Feito com carinho pela Equipe Pe. Constantino ❤️</div>', unsafe_allow_html=True)
