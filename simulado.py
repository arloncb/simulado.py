import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64

# 1. CONFIGURAÇÃO DA PÁGINA (Barra lateral inicia recolhida)
st.set_page_config(
    page_title="Portal Simulado - Constantino", 
    layout="wide", 
    page_icon="📝",
    initial_sidebar_state="collapsed"
)

# --- DADOS DO GITHUB ---
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: 'github_token' não encontrado nos Secrets.")
    st.stop()

# --- CONEXÃO COM PLANILHA ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO DE UPLOAD PARA GITHUB ---
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

# --- DESIGN PREMIUM: CORES VIVAS E CONTRASTE ALTO ---
st.markdown("""
    <style>
    /* Fundo com Mesh Gradient Vibrante */
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: 
            radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(219, 39, 119, 0.8) 0, transparent 50%), 
            radial-gradient(at 0% 100%, rgba(37, 99, 235, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }

    /* Card Branco de Alto Contraste */
    .stForm {
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 40px !important;
        border-radius: 30px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6) !important;
    }

    /* Labels em Preto Puro */
    .stTextInput label, .stSelectbox label, .stTextArea label, .stFileUploader label {
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 800 !important;
    }

    /* Títulos em Branco com Sombra */
    h1, h2, h3, .stSubheader {
        color: #ffffff !important;
        font-weight: 900 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        text-align: center;
    }

    /* Botão Degradê Moderno */
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        padding: 15px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        transition: 0.3s ease;
    }
    
    /* Estilo de Sucesso */
    .sucesso-premium {
        background: #10b981;
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-size: 28px;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.markdown("<h2 style='color:white;'>Menu</h2>", unsafe_allow_html=True)
pagina = st.sidebar.radio("Navegar para:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO DE QUESTÕES
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    with st.form("form_questoes", clear_on_submit=True):
        st.markdown("<h3 style='color:black !important; text-shadow:none;'>📋 Identificação</h3>", unsafe_allow_html=True)
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            prof = st.text_input("Nome do Professor (a):")
            disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"])
        with col_id2:
            turma = st.text_input("Série e Letra (Ex: 7° A):")
            hab = st.text_input("Habilidade BNCC:")

        st.markdown("---")
        st.markdown("<h3 style='color:black !important; text-shadow:none;'>❓ Elaboração</h3>", unsafe_allow_html=True)
        pergunta = st.text_area("Enunciado da Questão:", height=150)
        foto = st.file_uploader("Anexar Imagem (Opcional):", type=["png", "jpg", "jpeg"])

        st.markdown("---")
        st.markdown("<h3 style='color:black !important; text-shadow:none;'>🔘 Alternativas</h3>", unsafe_allow_html=True)
        c_alt1, c_alt2 = st.columns(2)
        with c_alt1:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
            alt_c = st.text_input("Alternativa C:")
        with c_alt2:
            alt_d = st.text_input("Alternativa D:")
            alt_e = st.text_input("Alternativa E:")
            gabarito = st.selectbox("Qual é a CORRETA?", ["A", "B", "C", "D", "E"])

        enviar = st.form_submit_button("💾 SALVAR QUESTÃO AGORA")

        if enviar:
            if not prof or disc == "Selecione..." or not turma or not pergunta:
                st.error("🚨 Atenção: Preencha todos os campos obrigatórios!")
            else:
                try:
                    link_img = ""
                    if foto:
                        with st.spinner("🚀 Enviando imagem..."):
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
                    st.markdown('<div class="sucesso-premium">✅ SALVO COM SUCESSO!</div>', unsafe_allow_html=True)
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro técnico: {e}")

# ==========================================
# PÁGINA 2: ÁREA DA COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    
    col_lock, col_pass, col_lock2 = st.columns([1,2,1])
    with col_pass:
        senha = st.text_input("Chave de Acesso:", type="password")
    
    if senha == "constantino2026":
        st.success("Acesso Liberado")
        df_raw = conn.read(worksheet="Página1", ttl=0)
        df = df_raw.fillna("") 
        
        if not df.empty:
            st.markdown("### 🔍 Filtros de Busca")
            c1, c2 = st.columns(2)
            with c1:
                f_disc = st.multiselect("Por Disciplina:", df["Disciplina"].unique())
            with c2:
                f_turma = st.multiselect("Por Turma:", df["Turma"].unique())
            
            df_filtrado = df.copy()
            if f_disc:
                df_filtrado = df_filtrado[df_filtrado["Disciplina"].isin(f_disc)]
            if f_turma:
                df_filtrado = df_filtrado[df_filtrado["Turma"].isin(f_turma)]

            st.dataframe(df_filtrado, use_container_width=True)
            
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Planilha",
