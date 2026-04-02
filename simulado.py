import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Simulado Constantino - Premium", layout="centered", page_icon="📝")

# --- DADOS DO SEU GITHUB ---
# Verifique se o seu usuário e repositório são exatamente estes:
GITHUB_USER = "arloncb" 
GITHUB_REPO = "simulado-constantino"
GITHUB_TOKEN = st.secrets["github_token"]

# Função para enviar a imagem diretamente para o repositório do GitHub
def upload_to_github(file, filename):
    try:
        # A imagem será salva em uma pasta chamada 'imagens' dentro do GitHub
        path = f"imagens/{filename}"
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
        
        # Converte a imagem para Base64 (formato que o GitHub exige)
        content = base64.b64encode(file.getvalue()).decode()
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "message": f"Upload de imagem: {filename}",
            "content": content,
            "branch": "main" # ou 'master', dependendo do seu GitHub
        }
        
        res = requests.put(url, json=data, headers=headers)
        
        if res.status_code in [200, 201]:
            # Retorna o link 'raw' que abre a imagem direto no navegador
            return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}"
        else:
            st.error(f"Erro no GitHub: {res.json().get('message')}")
            return ""
    except Exception as e:
        st.error(f"Erro técnico no upload: {e}")
        return ""

# --- ESTILO VISUAL PREMIUM (CORES VÍVIDAS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%);
        background-attachment: fixed;
    }
    .stForm {
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 40px !important;
        border-radius: 30px !important;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5) !important;
    }
    h1, h3, .stSubheader { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #000000 !important; font-size: 20px !important; font-weight: bold !important;
    }
    div.stButton > button:first-child {
        width: 100%; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important; padding: 20px; font-size: 22px; font-weight: bold;
        border-radius: 15px; border: none; transition: 0.3s;
    }
    .sucesso-gigante {
        background: #10b981; color: white; padding: 35px; border-radius: 20px;
        text-align: center; font-size: 35px; font-weight: 900;
    }
    .rodape { text-align: center; color: white; font-weight: bold; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULOS ---
try:
    img_logo = Image.open("logo.png")
    st.image(img_logo, width=200)
except: pass

st.title("📝 Portal do Professor")
st.subheader("Simulados - Escola Padre Constantino")

# 2. CONEXÃO COM PLANILHA
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FORMULÁRIO
with st.form("form_questoes", clear_on_submit=True):
    st.markdown("### 📋 Identificação")
    prof = st.text_input("Nome do Professor (a):")
    disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"])
    turma = st.text_input("Série e Letra (Ex: 7° A):")

    st.markdown("---")
    st.markdown("### ❓ Elaboração da Questão")
    hab = st.text_input("Habilidade ou Competência (BNCC):")
    pergunta = st.text_area("Enunciado da Questão:", height=150)
    foto = st.file_uploader("Upload de Imagem (Opcional):", type=["png", "jpg", "jpeg"])

    st.markdown("---")
    alt_a = st.text_input("Alternativa A:")
    alt_b = st.text_input("Alternativa B:")
    alt_c = st.text_input("Alternativa C:")
    alt_d = st.text_input("Alternativa D:")
    alt_e = st.text_input("Alternativa E:")
    gabarito = st.selectbox("Qual é a CORRETA?", ["A", "B", "C", "D", "E"])

    enviar = st.form_submit_button("💾 SALVAR QUESTÃO AGORA")

    if enviar:
        if not prof or disc == "Selecione..." or not turma or not pergunta:
            st.error("🚨 Preencha todos os campos obrigatórios!")
        else:
            try:
                link_foto = ""
                if foto:
                    with st.spinner("Salvando imagem no GitHub..."):
                        # Criamos um nome único para o arquivo
                        ext = foto.name.split('.')[-1]
                        nome_arquivo = f"{disc}_{turma}_{pd.Timestamp.now().strftime('%H%M%S')}.{ext}".replace(" ", "_")
                        link_foto = upload_to_github(foto, nome_arquivo)

                # Salvar na Planilha
                dados_atuais = conn.read(worksheet="Página1", ttl=0)
                nova_questao = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor (a)": prof,
                    "Disciplina": disc,
                    "Turma": turma,
                    "Habilidade": hab,
                    "Pergunta": pergunta,
                    "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                    "Correta": gabarito,
                    "Link Imagem": link_foto
                }])
                df_final = pd.concat([dados_atuais, nova_questao], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                st.markdown('<div class="sucesso-gigante">✅ SALVO COM SUCESSO!</div>', unsafe_allow_html=True)
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# 4. PRÉ-VISUALIZAÇÃO
if pergunta:
    st.markdown("<br><h3 style='color:white;'>👀 Pré-visualização:</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div style="background:white; padding:25px; border-left:15px solid #4f46e5; border-radius:15px; color:black;"><b>Habilidade:</b> {hab}<br><b>Questão:</b><br>{pergunta}</div>', unsafe_allow_html=True)
        if foto: st.image(foto, use_container_width=True)
        st.markdown(f'<div style="color:white; font-size:20px; font-weight:bold; margin-top:15px;">a) {alt_a}<br>b) {alt_b}<br>c) {alt_c}<br>d) {alt_d}<br>e) {alt_e}</div>', unsafe_allow_html=True)

st.markdown('<div class="rodape">Feito com carinho pela Equipe Padre Constantino ❤️</div>', unsafe_allow_html=True)
