import streamlit as st
import pandas as pd

# 1. Configurações Iniciais
st.set_page_config(page_title="Sistema de Simulados - Padre Constantino", layout="wide")

# Link da sua planilha pública (formato CSV)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1gPhMASo7yOsn5HhvLw6_rGkYbSkcBB_xUsgN8QgzhWw/export?format=csv"
# Link do seu Google Forms para os professores lançarem as questões
URL_FORMULARIO_LANCAMENTO = "https://docs.google.com/forms/d/e/SEU_ID_DO_FORM/viewform"

def carregar_dados():
    try:
        return pd.read_csv(URL_PLANILHA)
    except:
        return None

# 2. Gestão de Perfil (Session State)
if 'perfil' not in st.session_state:
    st.session_state.perfil = "Selecionar"

# Barra Lateral para Troca de Perfil
with st.sidebar:
    st.title("⚙️ Configurações")
    st.session_state.perfil = st.selectbox(
        "Selecione seu Perfil:",
        ["Professor (a)", "Coordenação"],
        index=0 if st.session_state.perfil == "Professor (a)" else 1
    )
    st.divider()
    st.info(f"Conectado como: {st.session_state.perfil}")

# 3. Cabeçalho Principal
st.title("📚 Portal de Simulados")
st.markdown(f"**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 4. Lógica de Visualização por Perfil
if st.session_state.perfil == "Professor (a)":
    st.subheader("👨‍🏫 Área do Professor (a)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Deseja enviar novas questões para o banco de dados?")
        # O botão de lançamento agora é um link seguro que não exige Secrets
        st.link_button("🚀 LANÇAR NOVA QUESTÃO", URL_FORMULARIO_LANCAMENTO, use_container_width=True)

    with col2:
        st.write("Consulte as questões já cadastradas:")
        if st.button("🔍 VER BANCO DE QUESTÕES", use_container_width=True):
            df = carregar_dados()
            if df is not None:
                st.dataframe(df)

elif st.session_state.perfil == "Coordenação":
    st.subheader("🔑 Área da Coordenação")
    
    # Aqui a coordenação pode ver tudo e gerar relatórios
    df = carregar_dados()
    if df is not None:
        st.write(f"Total de questões no banco: {len(df)}")
        st.dataframe(df)
        
        # Botão para baixar tudo em Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 BAIXAR BANCO COMPLETO", csv, "banco_questoes.csv", "text/csv", use_container_width=True)
