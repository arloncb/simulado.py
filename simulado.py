import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image

# 1. Configuração da Página
st.set_page_config(page_title="Gerador de Simulados - Constantino", layout="wide", page_icon="📝")

st.title("📝 Portal do Professor - Envio de Questões")
st.markdown("---")

# 2. Conexão com o Google Sheets (usa as Secrets que configuramos)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Formulário de Entrada
with st.form("form_questoes", clear_on_submit=True):
    st.subheader("📋 Identificação e Enunciado")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        prof = st.text_input("Nome do Professor:")
    with col2:
        disc = st.selectbox("Disciplina:", ["Matemática", "Português", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
    with col3:
        turma = st.text_input("Turma (ex: 9º A):")

    pergunta = st.text_area("Enunciado da Questão (Dica: Use $ para fórmulas, ex: $x^2$):", height=150)
    
    # Campo de Imagem (opcional)
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

    # --- Lógica de Salvamento ---
    if enviar:
        if prof and pergunta:
            try:
                # 1. Lemos os dados atuais (ttl=0 força a leitura do que está lá agora)
                # IMPORTANTE: Verifique se o nome da aba na sua planilha é "Página1"
                dados_atuais = conn.read(worksheet="Página1", ttl=0)
                
                # 2. Criamos a nova linha
                nova_questao = pd.DataFrame([{
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Professor": prof,
                    "Disciplina": disc,
                    "Turma": turma,
                    "Pergunta": pergunta,
                    "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e,
                    "Correta": gabarito
                }])
                
                # 3. Concatenamos (penduramos a nova embaixo da antiga)
                df_final = pd.concat([dados_atuais, nova_questao], ignore_index=True)
                
                # 4. Atualizamos a planilha
                conn.update(worksheet="Página1", data=df_final)
                
                st.success(f"✅ Questão de {disc} salva com sucesso! O formulário foi limpo para a próxima.")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro ao conectar com a planilha: {e}")
        else:
            st.warning("⚠️ Atenção: Preencha pelo menos o nome do professor e o enunciado da questão.")

# --- 4. PRÉ-VISUALIZAÇÃO (Para o professor conferir o visual) ---
st.write("---")
st.subheader("👀 Como o aluno verá no simulado:")
if pergunta:
    with st.container(border=True):
        st.write(f"**Questão:** {pergunta}")
        if foto:
            st.image(foto, caption="Imagem da Questão")
        st.write(f"**a)** {alt_a}")
        st.write(f"**b)** {alt_b}")
        st.write(f"**c)** {alt_c}")
        st.write(f"**d)** {alt_d}")
        st.write(f"**e)** {alt_e}")
