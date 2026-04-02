import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Simulados - Constantino", layout="wide", page_icon="📝")

st.title("📝 Portal do Professor - Envio de Questões")
st.markdown("---")

# 2. Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Formulário de Entrada
with st.form("form_questoes", clear_on_submit=True):
    st.subheader("📋 Identificação e Enunciado")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        prof = st.text_input("Nome do Professor (a):") # Ajustado o rótulo aqui também
    with col2:
        disc = st.selectbox("Disciplina:", ["Matemática", "Português", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    with col3:
        turma = st.text_input("Turma (ex: 9º A):")

    pergunta = st.text_area("Enunciado da Questão (Dica: Use $ para fórmulas, ex: $x^2$):", height=150)
    
    foto = st.file_uploader("Upload de Imagem ou Gráfico (se houver):", type=["png", "jpg", "jpeg"])

    st.write("---")
    st.subheader("🔘 Alternativas")
    
    col_a, col_b = st.columns(2)
    with col_a:
        alt_a = st.text_input("Alternativa A:")
        alt_b = st.text_input("Alternativa B:")
        alt_c = st.text_input("Alternativa C:")
    with col_b:
        alt_d = st.text_input("Alternativa D:")
        alt_e = st.text_input("Alternativa E:")
        gabarito = st.selectbox("Qual é a alternativa CORRETA?", ["A", "B", "C", "D", "E"])

    enviar = st.form_submit_button("💾 SALVAR QUESTÃO NA PLANILHA")

    if enviar:
        if prof and pergunta:
            try:
                # Lemos os dados atuais
                dados_atuais = conn.read(worksheet="Página1", ttl=0)
                
                # Criamos a nova linha (AQUI ESTÁ A MUDANÇA)
                nova_questao = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor (a)": prof, # <-- DEVE SER IGUAL AO CABEÇALHO DA PLANILHA
                    "Disciplina": disc,
                    "Turma": turma,
                    "Pergunta": pergunta,
                    "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                    "Correta": gabarito
                }])
                
                df_final = pd.concat([dados_atuais, nova_questao], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                
                st.success(f"✅ Questão salva com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")
        else:
            st.warning("⚠️ Preencha o nome e o enunciado.")

# --- 4. PRÉ-VISUALIZAÇÃO ---
st.write("---")
if pergunta:
    with st.container(border=True):
        st.write(f"**Questão:** {pergunta}")
        if foto: st.image(foto)
        st.write(f"**a)** {alt_a}")
        st.write(f"**b)** {alt_b}")
        st.write(f"**c)** {alt_c}")
        st.write(f"**d)** {alt_d}")
        st.write(f"**e)** {alt_e}")
