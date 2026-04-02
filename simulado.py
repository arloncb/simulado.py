import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da página
st.set_page_config(page_title="Gerador de Simulados - Constantino", layout="wide")

st.title("📝 Envio de Questões para Simulado")
st.info("Professores: preencham os campos abaixo. Para fórmulas matemáticas, use o cifrão: $x^2$.")

# 2. Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Formulário do Professor
with st.form("form_questoes"):
    col1, col2 = st.columns(2)
    with col1:
        prof = st.text_input("Nome do Professor:")
        disc = st.selectbox("Disciplina:", ["Matemática", "Português", "História", "Geografia", "Ciências", "Outra"])
    with col2:
        turma = st.text_input("Turma (ex: 6º A):")
        
    st.write("---")
    
    # Campos da Questão
    pergunta = st.text_area("Enunciado da Questão:")
    
    # Campo para Imagem (O professor sobe a foto se precisar)
    foto = st.file_uploader("Tem imagem ou fórmula complexa? Suba a foto aqui:", type=["png", "jpg", "jpeg"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        alt_a = st.text_input("Alternativa A:")
        alt_c = st.text_input("Alternativa C:")
        alt_e = st.text_input("Alternativa E:")
    with col_b:
        alt_b = st.text_input("Alternativa B:")
        alt_d = st.text_input("Alternativa D:")
        gabarito = st.selectbox("Qual é a correta?", ["A", "B", "C", "D", "E"])

    enviar = st.form_submit_button("SALVAR QUESTÃO NA PLANILHA")

    if enviar:
        # Aqui o código vai enviar os dados para o Google Sheets
        nova_linha = pd.DataFrame([{
            "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
            "Professor": prof,
            "Disciplina": disc,
            "Turma": turma,
            "Pergunta": pergunta,
            "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
            "Correta": gabarito
        }])
        
        # Comando para adicionar na planilha
        try:
            # Pegamos os dados existentes
            existente = conn.read(worksheet="Página1")
            updated_df = pd.concat([existente, nova_linha], ignore_index=True)
            conn.update(worksheet="Página1", data=updated_df)
            st.success("✅ Questão salva com sucesso!")
        except:
            st.error("Erro na conexão. Precisamos configurar as 'Secrets'.")

# --- VISUALIZAÇÃO PRÉVIA (Como o aluno verá) ---
st.write("---")
st.subheader("👀 Pré-visualização da Questão:")
if pergunta:
    st.write(f"**{pergunta}**")
    if foto:
        st.image(foto)
    st.write(f"a) {alt_a}")
    st.write(f"b) {alt_b}")
    st.write(f"c) {alt_c}")
    st.write(f"d) {alt_d}")
    st.write(f"e) {alt_e}")
