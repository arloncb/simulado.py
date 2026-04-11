import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Portal Simulado - Escola Constantino", layout="centered")

# --- 1. VISUAL PREMIUM (CSS) - FORÇANDO CONTRASTE ---
st.markdown("""
    <style>
    /* Fundo cinza claro para destacar os blocos brancos */
    .stApp {
        background-color: #f4f7f9 !important;
    }
    
    /* Títulos em Azul Escuro */
    h1, h2, h3 {
        color: #0f172a !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Cards Brancos com Sombra para os campos */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #ffffff !important;
        padding: 25px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
        margin-bottom: 15px !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* FORÇANDO COR DAS FONTES PARA PRETO/AZUL ESCURO */
    label p, .stMarkdown p, p {
        color: #1e293b !important;
        font-size: 19px !important;
        font-weight: 600 !important;
    }

    /* Estilizando os campos de texto para ficarem visíveis */
    input, textarea, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* Botão de Enviar - Verde Profissional */
    .stButton>button {
        width: 100%;
        background-color: #059669 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 3.5em !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #047857 !important;
        transform: scale(1.01);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO AJUSTADAS ---

def conectar_google_sheets():
    # AJUSTADO: Agora usa a chave 'connections.gsheets' que você já tem!
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # AJUSTADO: Abre direto pela URL que está no seu secret
    return client.open_by_url(st.secrets["spreadsheet"]).get_worksheet(0)

def upload_github(arquivo, nome_arquivo):
    # AJUSTADO: Usa o seu token do github
    token = st.secrets["github_token"]
    # ⚠️ IMPORTANTE: Mude para o seu usuário e nome do repositório abaixo:
    repo = "SEU_USUARIO/NOME_REPOSITORIO" 
    url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
    conteudo = base64.b64encode(arquivo.read()).decode()
    payload = {"message": f"Questão: {nome_arquivo}", "content": conteudo}
    headers = {"Authorization": f"token {token}"}
    res = requests.put(url, json=payload, headers=headers)
    return res.json()['content']['download_url'] if res.status_code in [200, 201] else ""

# --- 3. INTERFACE ---

st.title("📝 Portal de Simulados")
st.write("Escola Padre Constantino de Monte")

with st.container():
    prof = st.text_input("👤 Nome do Professor", placeholder="Digite seu nome...")
    disciplina = st.selectbox("📚 Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    
    # MULTISELEÇÃO DE TURMAS
    turmas = st.multiselect(
        "🏫 Para quais turmas é esta questão?", 
        ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"],
        help="Você pode selecionar várias turmas de uma vez."
    )

with st.container():
    enunciado = st.text_area("✍️ Enunciado da Questão", placeholder="Escreva a pergunta aqui...")
    
    # LIMITE DE 10MB
    foto = st.file_uploader("🖼️ Imagem (Opcional - Máx 10MB)", type=["jpg", "jpeg", "png"])
    if foto and foto.size > 10 * 1024 * 1024:
        st.error("🚨 Imagem muito pesada! Escolha uma de até 10MB.")
        foto = None

with st.container():
    st.write("🎯 **Alternativas**")
    c1, c2 = st.columns(2)
    with c1:
        a = st.text_input("A)")
        b = st.text_input("B)")
        c = st.text_input("C)")
    with c2:
        d = st.text_input("D)")
        e = st.text_input("E)")
        gabarito = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])

# --- 4. ENVIO ---

if st.button("🚀 LANÇAR QUESTÃO"):
    if not prof or not turmas or not enunciado:
        st.warning("⚠️ Preencha o nome, turmas e enunciado!")
    else:
        with st.spinner("Salvando..."):
            try:
                url_img = ""
                if foto:
                    nome_img = f"{datetime.now().timestamp()}.jpg"
                    url_img = upload_github(foto, nome_img)
                
                sheet = conectar_google_sheets()
                
                # LOOP PARA SALVAR UMA LINHA POR TURMA
                for t in turmas:
                    dados = [
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        prof, disciplina, t, enunciado, url_img,
                        a, b, c, d, e, gabarito
                    ]
                    sheet.append_row(dados)
                
                st.success(f"✅ Questão enviada para as turmas: {', '.join(turmas)}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro: {e}")
