import streamlit as st
import pandas as pd
from fpdf import FPDF # Certifique-se de adicionar 'fpdf' no seu requirements.txt

# 1. Configurações e Identidade
st.set_page_config(page_title="Portal de Simulados - Padre Constantino", layout="wide")

# Link da Planilha Pública (Apenas Leitura para evitar erro de Secrets)
URL_BASE = "https://docs.google.com/spreadsheets/d/1gPhMASo7yOsn5HhvLw6_rGkYbSkcBB_xUsgN8QgzhWw/export?format=csv"

# --- FUNÇÃO PARA GERAR PDF DA PROVA ---
def gerar_pdf(df_filtrado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "E. E. Padre Constantino de Monte", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, "Simulado Escolar - 2026", ln=True, align='C')
    pdf.ln(10)
    
    for i, row in df_filtrado.iterrows():
        pdf.set_font("Arial", 'B', 11)
        pdf.multi_cell(190, 7, f"Questão {i+1} - [{row['Disciplina']}]")
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(190, 5, f"Habilidade: {row['Habilidade']}")
        pdf.ln(2)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(190, 7, str(row['Enunciado']))
        pdf.cell(190, 7, f"A) {row['A']}", ln=True)
        pdf.cell(190, 7, f"B) {row['B']}", ln=True)
        pdf.cell(190, 7, f"C) {row['C']}", ln=True)
        pdf.cell(190, 7, f"D) {row['D']}", ln=True)
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1')

# 2. Navegação por Perfil (Barra Lateral)
with st.sidebar:
    st.title("🏫 SIDE - Simulados")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()

# --- ÁREA DO PROFESSOR ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões - BNCC/MS")
    
    with st.form("form_lancamento", clear_on_submit=True):
        col_disc, col_hab = st.columns([1, 1])
        
        with col_disc:
            disciplina = st.selectbox("Disciplina:", [
                "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de Texto"
            ])
        
        with col_hab:
            habilidade = st.text_input("Habilidade (Ex: EF06LP01):", help="Conforme o Currículo de Referência de MS")
            
        enunciado = st.text_area("Enunciado da Questão:")
        
        c1, c2 = st.columns(2)
        with c1:
            a = st.text_input("Alternativa A:")
            b = st.text_input("Alternativa B:")
        with c2:
            c = st.text_input("Alternativa C:")
            d = st.text_input("Alternativa D:")
            
        correta = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_salvar = st.form_submit_button("💾 SALVAR QUESTÃO NO BANCO")
        
        if btn_salvar:
            st.warning("⚠️ Lembrete: A gravação direta na planilha exige o Secrets. Use o Google Forms para salvar por enquanto.")

# --- ÁREA DA COORDENAÇÃO ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso Autorizado!")
        
        # Carregar Dados
        try:
            df = pd.read_csv(URL_BASE)
            
            # Filtros para a Prova
            st.write("### 📑 Gerador de Provas (PDF)")
            f_disc = st.multiselect("Filtrar por Disciplina:", df['Disciplina'].unique())
            
            df_filtrado = df[df['Disciplina'].isin(f_disc)] if f_disc else df
            
            st.dataframe(df_filtrado, use_container_width=True)
            
            if not df_filtrado.empty:
                # Botão de Download PDF
                pdf_data = gerar_pdf(df_filtrado)
                st.download_button(
                    label="📄 BAIXAR PROVA EM PDF",
                    data=pdf_data,
                    file_name="prova_simulado.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except:
            st.error("Erro ao carregar banco de dados. Verifique o link da planilha.")
    elif senha != "":
        st.error("Senha Incorreta!")
