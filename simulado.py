import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Simulados - Constantino", layout="centered", page_icon="📝")

# --- ESTILO CSS AVANÇADO (Cores de Fundo e Design) ---
st.markdown("""
    <style>
    /* 1. Fundo da página inteira (Degradê Azul Suave) */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* 2. Remover fundo branco do cabeçalho */
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* 3. Estilo do Formulário (Branco com Sombra) */
    .stForm {
        background-color: white !important;
        padding: 30px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        border: none !important;
    }

    /* 4. Ajustes de Fontes */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    .stTextInput label, .stSelectbox label, .stTextArea label {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }

    /* 5. Alerta de Sucesso Personalizado */
    .sucesso-gigante {
        padding: 40px;
        background-color: #27ae60;
        color: white;
        border-radius: 20px;
        text-align: center;
        font-size: 35px !important;
        font-weight: bold;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* 6. Rodapé */
    .rodape {
        text-align: center;
        color: #555;
        font-style: italic;
        margin-top: 50px;
        padding: 20px;
        font-weight: 500;
    }
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
st.markdown("---")

# 2. Conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Formulário
with st.form("form_questoes", clear_on_submit=True):
    st.markdown("### 📋 Informações Básicas")
    prof = st.text_input("Nome do Professor (a):")
    disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    turma = st.text_input("Série e Letra (Ex: 7° A):")

    st.markdown("---")
    st.markdown("### ❓ Detalhes da Questão")
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
            st.error("🚨 Atenção: Todos os campos obrigatórios precisam ser preenchidos!")
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
                df_final = pd.concat([dados_atuais, nova_questao], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                st.markdown('<div class="sucesso-gigante">✅ SALVO COM SUCESSO!</div>', unsafe_allow_html=True)
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- 4. PRÉ-VISUALIZAÇÃO ---
if pergunta:
    st.markdown("---")
    st.subheader("👀 Pré-visualização:")
    with st.container():
        # Estilo de "Papel" para a questão
        st.markdown(f"""
        <div style="background-color: #fff; padding: 20px; border-left: 10px solid #3498db; border-radius: 10px;">
            <strong>Questão:</strong> {pergunta}
        </div>
        """, unsafe_allow_html=True)
        if foto: st.image(foto)
        st.write(f"a) {alt_a}")
        st.write(f"b) {alt_b}")
        st.write(f"c) {alt_c}")
        st.write(f"d) {alt_d}")
        st.write(f"e) {alt_e}")

# --- 5. RODAPÉ ---
st.markdown('<div class="rodape">Feito com carinho pela Equipe Padre Constantino ❤️</div>', unsafe_allow_html=True)
