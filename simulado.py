import streamlit as st
import pandas as pd

# 1. Configurações e Identidade
st.set_page_config(page_title="Portal de Simulados - Padre Constantino", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Link da Planilha (Verifique se este link está correto para evitar o erro de 'Arquivo não existe')
#
URL_BASE = "https://docs.google.com/spreadsheets/d/1gPhMASo7yOsn5HhvLw6_rGkYbSkcBB_xUsgN8QgzhWw/export?format=csv"

# 3. Navegação por Perfil (Barra Lateral)
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("Sistema SIDE - Gestão de Simulados")

# --- ÁREA DO PROFESSOR (Restaurando o Lançamento Nativo) ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
    # Criando os campos que o professor usava antes
    with st.form("form_lancamento"):
        materia = st.selectbox("Disciplina:", ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências"])
        enunciado = st.text_area("Digite o enunciado da questão:")
        
        col1, col2 = st.columns(2)
        with col1:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
        with col2:
            alt_c = st.text_input("Alternativa C:")
            alt_d = st.text_input("Alternativa D:")
            
        correta = st.selectbox("Alternativa Correta:", ["A", "B", "C", "D"])
        
        btn_enviar = st.form_submit_button("🚀 CADASTRAR QUESTÃO")
        
        if btn_enviar:
            st.warning("⚠️ Para salvar diretamente na planilha, precisamos finalizar a conexão do Secrets. Por enquanto, os dados acima não estão sendo gravados.")

# --- ÁREA DA COORDENAÇÃO ---
else:
    st.subheader("🔑 Gestão da Coordenação")
    try:
        df = pd.read_csv(URL_BASE)
        st.write(f"Total de questões cadastradas: {len(df)}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        # Se o erro de 'Arquivo não existe' persistir, aparecerá aqui
        st.error(f"Não foi possível ler a planilha. Verifique o compartilhamento no Google Drive. Erro: {e}")
