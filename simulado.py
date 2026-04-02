import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image

# 1. Configuração da Página
st.set_page_config(page_title="Simulado Constantino - Premium", layout="centered", page_icon="📝")

# --- DESIGN TOTAL: CORES VIVAS, TEXTURAS E MODERNIDADE ---
st.markdown("""
    <style>
    /* 1. Fundo com Mesh Gradient Vibrante (Textura de Cores) */
    [data-testid="stAppViewContainer"] {
        background-color: #1e1b4b;
        background-image: 
            radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.8) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(219, 39, 119, 0.8) 0, transparent 50%), 
            radial-gradient(at 0% 100%, rgba(37, 99, 235, 0.8) 0, transparent 50%);
        background-attachment: fixed;
    }

    /* 2. Cabeçalho Transparente */
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }

    /* 3. Títulos em Branco (Contraste Máximo com o Fundo Vibrante) */
    h1, h3, .stSubheader {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        text-align: center;
    }

    /* 4. O CARD DO FORMULÁRIO (Efeito Vidro Moderno) */
    .stForm {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 50px !important;
        border-radius: 30px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* 5. CAMPOS DE DIGITAÇÃO MODERNOS */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea {
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        color: #0f172a !important; /* Texto Preto Sólido dentro do card branco */
    }
    
    /* Labels dos campos em Preto Sólido (Contraste com card branco) */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #000000 !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
    }

    /* 6. BOTÃO MODERNO E VIBRANTE */
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px rgba(79, 70, 229, 0.5);
        background: linear-gradient(90deg, #4338ca 0%, #6d28d9 100%);
    }

    /* 7. ALERTA DE SUCESSO GIGANTE */
    .sucesso-gigante {
        background: #10b981;
        color: white;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 40px !important;
        font-weight: 900;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: 5px solid #059669;
    }

    /* 8. RODAPÉ (Contraste com o fundo azul) */
    .rodape {
        text-align: center;
        color: #ffffff;
        font-size: 20px;
        font-weight: bold;
        margin-top: 50px;
        padding: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
col_logo, _ = st.columns([1, 2])
with col_logo:
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
st.markdown("<br>", unsafe_allow_html=True)

# 2. Conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Formulário Principal
with st.form("form_questoes", clear_on_submit=True):
    st.markdown("### 📋 Identificação do Professor")
    prof = st.text_input("Nome do Professor (a):")
    disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    turma = st.text_input("Série e Letra (Ex: 7° A):")

    st.markdown("<br>### ❓ Elaboração da Questão", unsafe_allow_html=True)
    pergunta = st.text_area("Enunciado da Questão:", height=150)
    foto = st.file_uploader("Upload de Imagem ou Gráfico (Opcional):", type=["png", "jpg", "jpeg"])

    st.markdown("<br>### 🔘 Alternativas e Gabarito", unsafe_allow_html=True)
    alt_a = st.text_input("Alternativa A:")
    alt_b = st.text_input("Alternativa B:")
    alt_c = st.text_input("Alternativa C:")
    alt_d = st.text_input("Alternativa D:")
    alt_e = st.text_input("Alternativa E:")
    gabarito = st.selectbox("Indique a alternativa CORRETA:", ["A", "B", "C", "D", "E"])

    st.markdown("<br>", unsafe_allow_html=True)
    enviar = st.form_submit_button("💾 FINALIZAR E SALVAR QUESTÃO")

    if enviar:
        if not prof or disc == "Selecione..." or not turma or not pergunta:
            st.error("🚨 ATENÇÃO: Preencha todos os campos obrigatórios antes de salvar!")
        else:
            try:
                dados_atuais = conn.read(worksheet="Página1", ttl=0)
                nova_questao = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor (a)": prof,
                    "Disciplina": disc,
                    "Turma": turma,
                    "Pergunta": pergunta,
                    "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                    "Correta": gabarito
                }])
                df_
