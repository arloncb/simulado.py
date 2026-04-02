import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Portal Simulado - Constantino", 
    layout="wide", 
    page_icon="📝",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÕES DO GITHUB ---
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: Chave 'github_token' não encontrada nos Secrets.")
    st.stop()

# --- CONEXÃO COM PLANILHA ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO DE UPLOAD ---
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
    except:
        return ""

# --- DESIGN PREMIUM (CSS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: 
            radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(219, 39, 119, 0.8) 0, transparent 50%), 
            radial-gradient(at 0% 100%, rgba(37, 99, 235, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }
    .stForm {
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 30px !important;
        border-radius: 25px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    }
    h1, h2, h3, .stSubheader { color: white !important; font-weight: 800 !important; text-align: center; }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; }
    div.stButton > button:first-child {
        width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important; font-weight: bold; padding: 15px; border-radius: 10px; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.markdown("<h2 style='color:white;'>Menu</h2>", unsafe_allow_html=True)
pagina = st.sidebar.radio("Escolha a página:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO DE QUESTÕES
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    with st.form("form_professor", clear_on_submit=True):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            prof = st.text_input("Nome do Professor (a):")
            disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"])
        with c2:
            turma = st.text_input("Série e Letra (Ex: 7° A):")
            hab = st.text_input("Habilidade (BNCC):")

        st.markdown("---")
        st.markdown("<h4 style='color:black;'>❓ Questão</h4>", unsafe_allow_html=True)
        pergunta = st.text_area("Enunciado da Questão:", height=120)
        foto = st.file_uploader("Imagem (Opcional):", type=["png", "jpg", "jpeg"])

        st.markdown("---")
        st.markdown("<h4 style='color:black;'>🔘 Alternativas</h4>", unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            alt_a = st.text_input("A:")
            alt_b = st.text_input("B:")
            alt_c = st.text_input("C:")
        with cb:
            alt_d = st.text_input("D:")
            alt_e = st.text_input("E:")
            gabarito = st.selectbox("Correta:", ["A", "B", "C", "D", "E"])

        enviar = st.form_submit_button("💾 SALVAR QUESTÃO")

        if enviar:
            if not prof or disc == "Selecione..." or not pergunta:
                st.error("🚨 Preencha os campos obrigatórios!")
            else:
                try:
                    link_img = ""
                    if foto:
                        with st.spinner("🚀 Subindo imagem..."):
                            nome_f = f"{disc}_{turma}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg".replace(" ", "_")
                            link_img = upload_to_github(foto, nome_f)
                    
                    df_antigo = conn.read(worksheet="Página1", ttl=0)
                    nova_linha = pd.DataFrame([{
                        "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                        "Professor (a)": prof, "Disciplina": disc, "Turma": turma,
                        "Habilidade": hab, "Pergunta": pergunta, "A": alt_a, "B": alt_b,
                        "C": alt_c, "D": alt_d, "E": alt_e, "Correta": gabarito, "Link Imagem": link_img
                    }])
                    df_final = pd.concat([df_antigo, nova_linha], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_final)
                    st.success("✅ SALVO COM SUCESSO!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro no salvamento: {e}")

# ==========================================
# PÁGINA 2: ÁREA DA COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    _, col_senha, _ = st.columns([1,2,1])
    with col_senha:
        senha = st.text_input("Senha de Acesso:", type="password")
    
    if senha == "constantino2026":
        st.success("Acesso Autorizado")
        df_raw = conn.read(worksheet="Página1", ttl=0)
        df = df_raw.fillna("") 
        
        if not df.empty:
            st.markdown("### 🔍 Filtros")
            cf1, cf2 = st.columns(2)
            with cf1:
                f_disc = st.multiselect("Disciplina:", df["Disciplina"].unique())
            with cf2:
                f_turma = st.multiselect("Turma:", df["Turma"].unique())
            
            df_filtrado = df.copy()
            if f_disc:
                df_filtrado = df_filtrado[df_filtrado["Disciplina"].isin(f_disc)]
            if f_turma:
                df_filtrado = df_filtrado[df_filtrado["Turma"].isin(f_turma)]

            st.dataframe(df_filtrado, use_container_width=True)
            
            csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Baixar Planilha Filtrada", data=csv_data, file_name="simulado.csv", mime="text/csv")
            
            st.markdown("---")
            st.subheader("👀 Revisão das Questões")
            for i, row in df_filtrado.iterrows():
                with st.expander(f"{row['Disciplina']} - {row['Turma']} (Prof. {row['Professor (a)']})"):
                    st.write(f"**Habilidade:** {row['Habilidade']}")
                    st.info(f"**Enunciado:** {row['Pergunta']}")
                    if row['Link Imagem'] and str(row['Link Imagem']).startswith("http"):
                        st.image(row['Link Imagem'], width=400)
                    st.write(f"a) {row['A']} | b) {row['B']} | c) {row['C']} | d) {row['D']} | e) {row['E']}")
                    st.success(f"Gabarito: {row['Correta']}")
        else:
            st.info("O banco de dados está vazio.")
    elif senha != "":
        st.error("Senha incorreta!")

st.markdown('<br><p style="text-align:center; color:white;">Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
