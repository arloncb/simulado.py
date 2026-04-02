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

# --- CONFIGURAÇÕES GITHUB ---
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: Chave 'github_token' não encontrada.")
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

# --- ESTADO DE SESSÃO PARA LIMPEZA PARCIAL ---
# Inicializa campos que queremos limpar após o envio
if 'limpar' not in st.session_state:
    st.session_state.limpar = 0

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }
    .stForm { background: rgba(255, 255, 255, 0.98) !important; padding: 40px !important; border-radius: 25px !important; }
    h1, h2, h3 { color: white !important; font-weight: 800 !important; text-align: center; }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; font-size: 18px !important; }
    div.stButton > button:first-child { width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); color: white !important; padding: 15px; font-weight: bold; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.markdown("<h2 style='color:white;'>Menu</h2>", unsafe_allow_html=True)
pagina = st.sidebar.radio("Navegar:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO DE QUESTÕES
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Escola Padre Constantino")

    # Nota: Não usamos clear_on_submit=True para poder manter os dados do professor
    with st.form("form_questoes"):
        st.markdown("<h4 style='color:black;'>📋 Identificação</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            prof = st.text_input("Nome do Professor (a):", key="prof_input")
            disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"], key="disc_input")
        with col2:
            turma = st.text_input("Série e Letra (Ex: 7° A):", key="turma_input")
            # A Habilidade geralmente muda por questão, então damos uma chave que muda para limpar
            hab = st.text_input("Habilidade (BNCC):", key=f"hab_{st.session_state.limpar}")

        st.markdown("---")
        st.markdown("<h4 style='color:black;'>❓ Elaboração</h4>", unsafe_allow_html=True)
        # Campos da questão usam a chave dinâmica para serem limpos após o sucesso
        pergunta = st.text_area("Enunciado da Questão:", height=150, key=f"pergunta_{st.session_state.limpar}")
        foto = st.file_uploader("Imagem (Opcional):", type=["png", "jpg", "jpeg"], key=f"foto_{st.session_state.limpar}")

        st.markdown("---")
        st.markdown("<h4 style='color:black;'>🔘 Alternativas (Uma por linha)</h4>", unsafe_allow_html=True)
        # Alternativas agora estão uma sobre a outra
        alt_a = st.text_input("Alternativa A:", key=f"a_{st.session_state.limpar}")
        alt_b = st.text_input("Alternativa B:", key=f"b_{st.session_state.limpar}")
        alt_c = st.text_input("Alternativa C:", key=f"c_{st.session_state.limpar}")
        alt_d = st.text_input("Alternativa D:", key=f"d_{st.session_state.limpar}")
        alt_e = st.text_input("Alternativa E:", key=f"e_{st.session_state.limpar}")
        gabarito = st.selectbox("Qual é a CORRETA?", ["A", "B", "C", "D", "E"], key=f"gab_{st.session_state.limpar}")

        enviar = st.form_submit_button("💾 SALVAR E CONTINUAR")

        if enviar:
            if not prof or disc == "Selecione..." or not pergunta:
                st.error("🚨 Preencha os campos obrigatórios (Nome, Disciplina e Pergunta)!")
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
                    
                    st.success("✅ Questão Salva! Enunciado e Alternativas limpos para a próxima.")
                    
                    # Incrementa o contador de limpeza: isso faz com que os campos da questão 
                    # "resetem" mas os de identificação (nome, disc, turma) permaneçam
                    st.session_state.limpar += 1
                    st.rerun() # Reinicia a página para aplicar a limpeza parcial
                    
                except Exception as e:
                    st.error(f"Erro técnico: {e}")

# ==========================================
# PÁGINA 2: ÁREA DA COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    senha = st.text_input("Senha de Acesso:", type="password")
    
    if senha == "constantino2026":
        st.success("Acesso Liberado")
        df_raw = conn.read(worksheet="Página1", ttl=0)
        df = df_raw.fillna("") 
        
        if not df.empty:
            st.markdown("### 🔍 Filtros")
            cf1, cf2 = st.columns(2)
            with cf1:
                f_disc = st.multiselect("Por Disciplina:", df["Disciplina"].unique())
            with cf2:
                f_turma = st.multiselect("Por Turma:", df["Turma"].unique())
            
            df_filtrado = df.copy()
            if f_disc: df_filtrado = df_filtrado[df_filtrado["Disciplina"].isin(f_disc)]
            if f_turma: df_filtrado = df_filtrado[df_filtrado["Turma"].isin(f_turma)]

            st.dataframe(df_filtrado, use_container_width=True)
            
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Planilha", csv, "banco_questoes.csv", "text/csv")
            
            st.markdown("---")
            for i, row in df_filtrado.iterrows():
                with st.expander(f"{row['Disciplina']} - {row['Turma']} (Prof. {row['Professor (a)']})"):
                    st.write(f"**BNCC:** {row['Habilidade']}")
                    st.info(f"**Enunciado:** {row['Pergunta']}")
                    if row['Link Imagem'] and str(row['Link Imagem']).startswith("http"):
                        st.image(row['Link Imagem'], width=500)
                    st.write(f"a) {row['A']} | b) {row['B']} | c) {row['C']} | d) {row['D']} | e) {row['E']}")
                    st.success(f"Gabarito: {row['Correta']}")
    elif senha != "":
        st.error("Chave incorreta!")

st.markdown('<br><p style="text-align:center; color:white;">Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
