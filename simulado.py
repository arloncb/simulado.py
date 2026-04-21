import streamlit as st
import pandas as pd

# 1. Configurações Iniciais
st.set_page_config(page_title="Sistema de Simulados - Padre Constantino", layout="wide")

# Link da sua planilha de SIMULADOS (Pública no Google como 'Qualquer pessoa com o link')
URL_PLANILHA_SIMULADOS = "https://docs.google.com/spreadsheets/d/1gPhMASo7yOsn5HhvLw6_rGkYbSkcBB_xUsgN8QgzhWw/export?format=csv"

# 2. Função para carregar as questões (Sem precisar de Secrets)
def carregar_banco_questoes():
    try:
        # Lê a planilha de simulados diretamente
        df = pd.read_csv(URL_PLANILHA_SIMULADOS)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de questões: {e}")
        return None

# 3. Gerenciamento de Perfil (Barra Lateral)
with st.sidebar:
    st.title("🛡️ Acesso Restrito")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.write(f"**Escola Estadual Padre Constantino de Monte**")

# 4. Conteúdo Principal
st.title("📚 Portal de Simulados")
st.write("---")

if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Área do Professor (a) - Lançamento e Consulta")
    
    tab1, tab2 = st.tabs(["🔍 Ver Banco de Questões", "🚀 Lançar Nova Questão"])
    
    with tab1:
        df = carregar_banco_questoes()
        if df is not None:
            st.write("Aqui estão as questões já cadastradas no sistema:")
            st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.info("Para evitar erros de conexão, o lançamento agora é feito via formulário seguro.")
        # IMPORTANTE: Coloque aqui o link do Google Forms que alimenta a sua planilha de simulados
        st.link_button("ABRIR FORMULÁRIO DE LANÇAMENTO", "https://docs.google.com/forms/d/SEU_LINK_AQUI", use_container_width=True)

else:
    st.subheader("🔑 Área da Coordenação - Gestão de Simulados")
    
    df = carregar_banco_questoes()
    if df is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Total de questões disponíveis: **{len(df)}**")
        with col2:
            # Opção de baixar o banco para conferência offline
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Planilha (CSV)", csv, "banco_simulados.csv", "text/csv", use_container_width=True)
        
        st.divider()
        st.dataframe(df, use_container_width=True)
