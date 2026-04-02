import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Simulado Constantino - Premium", layout="centered")

# --- BUSCA O TOKEN ---
try:
    GITHUB_TOKEN = st.secrets["github_token"]
    GITHUB_USER = "arloncb" # <<-- VERIFIQUE SE ESTÁ IGUAL AO SEU GITHUB
    GITHUB_REPO = "simulado-constantino" # <<-- VERIFIQUE SE O NOME DO REPOSITÓRIO É ESTE
except:
    st.error("❌ Erro: 'github_token' não encontrado nos Secrets.")
    st.stop()

def upload_to_github(file, filename):
    try:
        # A pasta 'imagens' será criada automaticamente pelo GitHub no primeiro upload
        path = f"imagens/{filename}"
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
        
        content = base64.b64encode(file.getvalue()).decode()
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Removi o campo 'branch' para evitar erro se for 'master' ou 'main'
        data = {
            "message": f"Upload: {filename}",
            "content": content
        }
        
        res = requests.put(url, json=data, headers=headers)
        
        if res.status_code in [200, 201]:
            # Retorna o link direto
            return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}"
        else:
            # Mostra o erro detalhado para a gente saber o que é
            st.error(f"Erro detalhado do GitHub: {res.json().get('message')}")
            return ""
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return ""

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1b4b 0%, #3b82f6 100%); background-attachment: fixed; }
    .stForm { background: white !important; padding: 40px !important; border-radius: 25px !important; }
    .stTextInput label, .stSelectbox label, .stTextArea label { color: black !important; font-weight: bold !important; }
    .sucesso-gigante { background: #10b981; color: white; padding: 30px; border-radius: 20px; text-align: center; font-size: 30px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

st.title("📝 Portal do Professor")
st.subheader("Simulados - Escola Padre Constantino")

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FORMULÁRIO
with st.form("form_simulado", clear_on_submit=True):
    prof = st.text_input("Nome do Professor (a):")
    disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Biologia", "Química", "Física", "Sociologia", "Filosofia", "Inglês", "Artes", "Ed. Física"])
    turma = st.text_input("Série e Letra (Ex: 7° A):")
    hab = st.text_input("Habilidade (BNCC):")
    pergunta = st.text_area("Enunciado da Questão:", height=150)
    foto = st.file_uploader("Upload de Imagem (Opcional):", type=["png", "jpg", "jpeg"])
    
    st.write("---")
    alt_a = st.text_input("A:")
    alt_b = st.text_input("B:")
    alt_c = st.text_input("C:")
    alt_d = st.text_input("D:")
    alt_e = st.text_input("E:")
    gabarito = st.selectbox("Correta:", ["A", "B", "C", "D", "E"])

    enviar = st.form_submit_button("💾 SALVAR QUESTÃO")

    if enviar:
        if not prof or disc == "Selecione..." or not turma or not pergunta:
            st.error("🚨 Preencha os campos obrigatórios!")
        else:
            try:
                link_img = ""
                if foto:
                    with st.spinner("Enviando imagem..."):
                        nome_f = f"{disc}_{turma}_{pd.Timestamp.now().strftime('%H%M%S')}.jpg".replace(" ", "_")
                        link_img = upload_to_github(foto, nome_f)
                
                # Salvar na Planilha
                df_antigo = conn.read(worksheet="Página1", ttl=0)
                nova_linha = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor (a)": prof, "Disciplina": disc, "Turma": turma,
                    "Habilidade": hab, "Pergunta": pergunta, "A": alt_a, "B": alt_b,
                    "C": alt_c, "D": alt_d, "E": alt_e, "Correta": gabarito, "Link Imagem": link_img
                }])
                df_final = pd.concat([df_antigo, nova_linha], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                
                st.markdown('<div class="sucesso-gigante">✅ SALVO COM SUCESSO!</div>', unsafe_allow_html=True)
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

st.markdown('<br><p style="text-align:center; color:white;">Equipe Padre Constantino ❤️</p>', unsafe_allow_html=True)
