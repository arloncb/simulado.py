import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Simulado Constantino - Premium", layout="centered", page_icon="📝")

# --- ID DA SUA PASTA DO DRIVE ---
ID_PASTA_DRIVE = "1vQrVswZ-_5TFDoHWJuEuxjGQLwPBBgqD"

# Função para fazer o upload da imagem para o Google Drive
def upload_to_drive(file, filename):
    try:
        # Usa as mesmas credenciais da planilha que já estão no Secrets
        info_chave = st.secrets["connections"]["gsheets"]
        credentials = service_account.Credentials.from_service_account_info(info_chave)
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {'name': filename, 'parents': [ID_PASTA_DRIVE]}
        media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='image/jpeg')
        
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # Retorna o link direto para a imagem
        return f"https://drive.google.com/uc?id={uploaded_file.get('id')}"
    except Exception as e:
        st.error(f"Erro ao enviar para o Drive: {e}")
        return ""

# --- DESIGN PREMIUM: CORES VIVAS E CONTRASTE ---
st.markdown("""
    <style>
    /* Fundo Mesh Gradient */
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: 
            radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(219, 39, 119, 0.8) 0, transparent 50%), 
            radial-gradient(at 0% 100%, rgba(37, 99, 235, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    h1, h3, .stSubheader {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        text-align: center;
    }
    /* Estilo do Card Branco */
    .stForm {
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 40px !important;
        border-radius: 30px !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5) !important;
    }
    /* Labels em Preto Sólido */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #000000 !important;
        font-size: 22px !important;
        font-weight: 800 !important;
    }
    /* Botão de Salvar */
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover { transform: translateY(-3px); }
    /* Alerta de Sucesso */
    .sucesso-gigante {
        background: #10b981;
        color: white;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 35px;
        font-weight: 900;
    }
    .rodape { text-align: center; color: white; font-weight: bold; margin-top: 50px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
try:
    img_logo = Image.open("logo.png")
    st.image(img_logo, width=220)
except:
    try:
        img_logo = Image.open("logo.jpg")
        st.image(img_logo, width=220)
    except:
        pass

st.title("📝 Portal do Professor")
st.subheader("Simulados - Escola Padre Constantino")

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FORMULÁRIO PRINCIPAL
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
    st.markdown("### 🔘 Alternativas")
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
                    with st.spinner("Enviando imagem para o Drive..."):
                        # Nome do arquivo será: NomeProf_Turma_Horario.jpg
                        nome_arquivo = f"{prof}_{turma}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg"
                        link_foto = upload_to_drive(foto, nome_arquivo)

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
                st.error(f"Erro técnico: {e}")

# --- 4. PRÉ-VISUALIZAÇÃO ---
if pergunta:
    st.markdown("<br><h3 style='color:white;'>👀 Pré-visualização:</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div style="background:white; padding:25px; border-left:15px solid #4f46e5; border-radius:15px; color:black;"><b>Habilidade:</b> {hab}<br><b>Questão:</b><br>{pergunta}</div>', unsafe_allow_html=True)
        if foto: st.image(foto, use_container_width=True)
        st.markdown(f'<div style="color:white; font-size:20px; font-weight:bold; margin-top:15px;">a) {alt_a}<br>b) {alt_b}<br>c) {alt_c}<br>d) {alt_d}<br>e) {alt_e}</div>', unsafe_allow_html=True)

st.markdown('<div class="rodape">Feito com carinho pela Equipe Padre Constantino ❤️</div>', unsafe_allow_html=True)
