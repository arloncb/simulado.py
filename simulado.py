import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal Simulado - Constantino", layout="wide", page_icon="📝")

# --- DADOS DO GITHUB ---
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado.py" 

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    st.error("❌ Erro: 'github_token' não encontrado nos Secrets do Streamlit.")
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
    except: return ""

# --- DESIGN CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%); background-attachment: fixed; }
    .stForm { background: white !important; padding: 30px !important; border-radius: 20px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; }
    h1, h2, h3 { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Escolha a página:", ["📝 Enviar Questão", "📋 Área da Coordenação"])

# ==========================================
# PÁGINA 1: ENVIO DE QUESTÕES
# ==========================================
if pagina == "📝 Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Envio de Questões - Escola Padre Constantino")

    with st.form("form_questoes", clear_on_submit=True):
        st.markdown("### 📋 Identificação")
        prof = st.text_input("Nome do Professor (a):")
        disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"])
        turma = st.text_input("Série e Letra (Ex: 7° A):")
        hab = st.text_input("Habilidade ou Competência (BNCC):")

        st.markdown("---")
        st.markdown("### ❓ Questão")
        pergunta = st.text_area("Enunciado da Questão:", height=150)
        foto = st.file_uploader("Upload de Imagem (Opcional):", type=["png", "jpg", "jpeg"])

        st.markdown("---")
        alt_a = st.text_input("A:")
        alt_b = st.text_input("B:")
        alt_c = st.text_input("C:")
        alt_d = st.text_input("D:")
        alt_e = st.text_input("E:")
        gabarito = st.selectbox("Qual é a CORRETA?", ["A", "B", "C", "D", "E"])

        enviar = st.form_submit_button("💾 SALVAR QUESTÃO NO BANCO")

        if enviar:
            if not prof or disc == "Selecione..." or not turma or not pergunta:
                st.error("🚨 Preencha todos os campos obrigatórios!")
            else:
                try:
                    link_img = ""
                    if foto:
                        with st.spinner("Salvando imagem..."):
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
                    st.success("✅ QUESTÃO SALVA COM SUCESSO!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

# ==========================================
# PÁGINA 2: ÁREA DA COORDENAÇÃO
# ==========================================
else:
    st.title("📋 Área Pedagógica")
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "constantino2026":
        st.success("Acesso autorizado!")
        
        # BUSCA DADOS E LIMPA OS 'NaN' (O PULO DO GATO ESTÁ AQUI)
        df_raw = conn.read(worksheet="Página1", ttl=0)
        df = df_raw.fillna("") # Transforma vazios em strings vazias
        
        if not df.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                f_disc = st.multiselect("Filtrar Disciplina:", df["Disciplina"].unique())
            with col2:
                f_turma = st.multiselect("Filtrar Turma:", df["Turma"].unique())
            
            df_filtrado = df.copy()
            if f_disc: df_filtrado = df_filtrado[df_filtrado["Disciplina"].isin(f_disc)]
            if f_turma: df_filtrado = df_filtrado[df_filtrado["Turma"].isin(f_turma)]

            st.dataframe(df_filtrado, use_container_width=True)
            
            # Download
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Planilha Filtrada", csv, "simulado.csv", "text/csv")
            
            st.markdown("---")
            st.subheader("🔍 Visualização das Questões")
            for i, row in df_filtrado.iterrows():
                with st.expander(f"{row['Disciplina']} - {row['Turma']} (Prof. {row['Professor (a)']})"):
                    st.write(f"**BNCC:** {row['Habilidade']}")
                    st.write(f"**Enunciado:** {row['Pergunta']}")
                    
                    # Checagem reforçada para evitar o erro do print
                    if row['Link Imagem'] and str(row['Link Imagem']).startswith("http"):
                        st.image(row['Link Imagem'], width=400)
                    
                    st.write(f"a) {row['A']} | b) {row['B']} | c) {row['C']} | d) {row['D']} | e) {row['E']}")
                    st.success(f"Gabarito: {row['Correta']}")
        else:
            st.info("Nenhuma questão cadastrada ainda.")
    elif senha != "":
        st.error("Senha incorreta!")

st.markdown('<br><p style="text-align:center; color:white;">Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
