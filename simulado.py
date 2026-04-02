import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests
import base64

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal Simulado - Constantino", layout="wide")

# --- DADOS GITHUB ---
GITHUB_TOKEN = st.secrets["github_token"]
GITHUB_USER = "arloncb"
GITHUB_REPO = "simulado.py"

# --- BARRA LATERAL (MENU) ---
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Ir para:", ["Enviar Questão", "Área da Coordenação"])

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES DE APOIO (Upload GitHub) ---
def upload_to_github(file, filename):
    try:
        path = f"imagens/{filename}"
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
        content = base64.b64encode(file.getvalue()).decode()
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        data = {"message": f"Upload: {filename}", "content": content, "branch": "main"}
        res = requests.put(url, json=data, headers=headers)
        if res.status_code in [200, 201]:
            return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}"
        return ""
    except: return ""

# ==========================================
# PÁGINA 1: ENVIO DE QUESTÕES (PROFESSORES)
# ==========================================
if pagina == "Enviar Questão":
    st.title("📝 Portal do Professor")
    st.subheader("Envio de Questões - Escola Padre Constantino")
    
    with st.form("form_envio", clear_on_submit=True):
        # ... (Aqui entra todo aquele bloco de campos que já criamos: prof, disc, turma, pergunta, etc)
        # (Para encurtar, use o código de formulário da última versão que te mandei)
        st.info("Utilize este espaço para cadastrar suas questões no banco oficial.")
        # [COLE AQUI O FORMULÁRIO COMPLETO DAS VERSÕES ANTERIORES]

# ==========================================
# PÁGINA 2: ÁREA DA COORDENAÇÃO (ADMIN)
# ==========================================
elif pagina == "Área da Coordenação":
    st.title("📋 Painel Pedagógico")
    
    # Proteção por Senha Simples
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "constantino2026": # Você escolhe a senha aqui
        st.success("Acesso autorizado!")
        
        # Lendo os dados
        df = conn.read(worksheet="Página1", ttl=0)
        
        if not df.empty:
            st.markdown("### 📊 Banco de Dados Atual")
            
            # Filtros na tela
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                f_disc = st.multiselect("Filtrar por Disciplina:", df["Disciplina"].unique())
            with col_f2:
                f_turma = st.multiselect("Filtrar por Turma:", df["Turma"].unique())
            
            # Aplicando filtros
            df_filtrado = df.copy()
            if f_disc: df_filtrado = df_filtrado[df_filtrado["Disciplina"].isin(f_disc)]
            if f_turma: df_filtrado = df_filtrado[df_filtrado["Turma"].isin(f_turma)]
            
            # Tabela Interativa
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Botão para baixar Excel
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Questões Selecionadas (CSV/Excel)", csv, "questoes_simulado.csv", "text/csv")
            
            st.markdown("---")
            st.markdown("### 🔍 Visualização das Questões")
            
            # Loop para mostrar questão por questão com a imagem
            for index, row in df_filtrado.iterrows():
                with st.expander(f"Questão: {row['Disciplina']} - {row['Turma']} (Por: {row['Professor (a)']})"):
                    st.write(f"**Habilidade:** {row['Habilidade']}")
                    st.write(f"**Enunciado:** {row['Pergunta']}")
                    if row['Link Imagem']:
                        st.image(row['Link Imagem'], caption="Imagem da Questão", width=400)
                    st.write(f"a) {row['A']} | b) {row['B']} | c) {row['C']} | d) {row['D']} | e) {row['E']}")
                    st.success(f"Gabarito: {row['Correta']}")
        else:
            st.info("O banco de dados ainda está vazio.")
    elif senha != "":
        st.error("Senha incorreta!")
