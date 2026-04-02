import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Simulados - Constantino", layout="centered", page_icon="📝")

# --- ESTILO CSS PERSONALIZADO (Aumentar fontes e alertas) ---
st.markdown("""
    <style>
    /* Aumentar fonte geral de labels e textos */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    .stTextInput label, .stSelectbox label, .stTextArea label {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    /* Alerta de sucesso gigante */
    .sucesso-gigante {
        padding: 40px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 20px;
        border: 4px solid #c3e6cb;
        text-align: center;
        font-size: 35px !important;
        font-weight: bold;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📝 Portal do Professor - Envio de Questões")
st.markdown("---")

# 2. Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Formulário de Entrada
# clear_on_submit=True limpa os campos após o envio
with st.form("form_questoes", clear_on_submit=True):
    st.subheader("📋 Identificação")
    
    prof = st.text_input("Nome do Professor (a):")
    
    # Adicionada opção neutra para forçar a escolha da disciplina
    disc = st.selectbox("Disciplina:", ["Selecione...", "Matemática", "Português", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    
    # Instrução clara para o padrão da turma
    turma = st.text_input("Série e Letra (Exemplo: 7° A, 9° B, 1° EM):")

    st.write("---")
    st.subheader("❓ Questão")
    pergunta = st.text_area("Enunciado da Questão:", height=150)
    
    foto = st.file_uploader("Upload de Imagem ou Gráfico (Opcional):", type=["png", "jpg", "jpeg"])

    st.write("---")
    st.subheader("🔘 Alternativas (Selecione a Correta)")
    
    # Alternativas uma abaixo da outra como solicitado
    alt_a = st.text_input("Alternativa A:")
    alt_b = st.text_input("Alternativa B:")
    alt_c = st.text_input("Alternativa C:")
    alt_d = st.text_input("Alternativa D:")
    alt_e = st.text_input("Alternativa E:")
    
    gabarito = st.selectbox("Indique qual é a alternativa CORRETA:", ["A", "B", "C", "D", "E"])

    enviar = st.form_submit_button("💾 SALVAR QUESTÃO NA PLANILHA")

    # --- Lógica de Validação e Salvamento ---
    if enviar:
        # BLOQUEIO: Não permite enviar se faltar Nome, Disciplina (padrão) ou Turma
        if not prof or disc == "Selecione..." or not turma or not pergunta:
            st.error("🚨 ERRO: Preencha obrigatoriamente Nome, Disciplina, Turma e o Enunciado!")
        else:
            try:
                # Lemos os dados atuais
                dados_atuais = conn.read(worksheet="Página1", ttl=0)
                
                # Criamos a nova linha
                nova_questao = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor (a)": prof,
                    "Disciplina": disc,
                    "Turma": turma,
                    "Pergunta": pergunta,
                    "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                    "Correta": gabarito
                }])
                
                # Concatenamos
                df_final = pd.concat([dados_atuais, nova_questao], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                
                # Mensagem de sucesso GIGANTE e personalizada
                st.markdown('<div class="sucesso-gigante">✅ QUESTÃO SALVA COM SUCESSO!</div>', unsafe_allow_html=True)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erro técnico ao salvar: {e}")

# --- 4. PRÉ-VISUALIZAÇÃO ---
if pergunta:
    st.write("---")
    st.subheader("👀 Pré-visualização:")
    with st.container(border=True):
        st.write(f"**Questão:** {pergunta}")
        if foto: st.image(foto)
        st.write(f"a) {alt_a}")
        st.write(f"b) {alt_b}")
        st.write(f"c) {alt_c}")
        st.write(f"d) {alt_d}")
        st.write(f"e) {alt_e}")
