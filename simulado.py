import streamlit as st
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página e Identidade
st.set_page_config(page_title="Portal de Simulados - Padre Constantino", layout="wide")

# Link da sua planilha de Simulados (Ajuste o link se necessário)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1gPhMASo7yOsn5HhvLw6_rGkYbSkcBB_xUsgN8QgzhWw/export?format=csv"

# --- FUNÇÃO PARA GERAR O PDF (Usando fpdf2) ---
def gerar_pdf_prova(dados_filtrados):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho da Escola
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Escola Estadual Padre Constantino de Monte", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, "Simulado Escolar - 2026", ln=True, align="C")
    pdf.line(10, 32, 200, 32)
    pdf.ln(10)
    
    for i, row in dados_filtrados.iterrows():
        # Disciplina e Habilidade
        pdf.set_font("helvetica", "B", 11)
        pdf.multi_cell(0, 8, f"QUESTÃO {i+1} - {row['Disciplina']}")
        pdf.set_font("helvetica", "I", 9)
        pdf.multi_cell(0, 6, f"Habilidade MS: {row['Habilidade']}")
        pdf.ln(2)
        
        # Enunciado
        pdf.set_font("helvetica", "", 11)
        pdf.multi_cell(0, 7, str(row['Enunciado']))
        pdf.ln(2)
        
        # Alternativas
        pdf.cell(0, 7, f"A) {row['A']}", ln=True)
        pdf.cell(0, 7, f"B) {row['B']}", ln=True)
        pdf.cell(0, 7, f"C) {row['C']}", ln=True)
        pdf.cell(0, 7, f"D) {row['D']}", ln=True)
        pdf.ln(6)
        
    return pdf.output()

# 2. Navegação Lateral
with st.sidebar:
    st.title("🛡️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Gestão de Simulados")

# --- ÁREA DO PROFESSOR (Lançamento Nativo) ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
    with st.form("form_simulado", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Lista atualizada com as disciplinas BNCC e correções solicitadas
            disciplina = st.selectbox("Disciplina:", [
                "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de texto"
            ])
            
        with col2:
            # Novo campo solicitado: Habilidade MS
            habilidade = st.text_input("Habilidade do Currículo de Referência MS:", placeholder="Ex: EF06LP01")
            
        enunciado = st.text_area("Enunciado da Questão:", height=150)
        
        # Alternativas
        c_a, c_b = st.columns(2)
        with c_a:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
        with c_b:
            alt_c = st.text_input("Alternativa C:")
            alt_d = st.text_input("Alternativa D:")
            
        gabarito = st.selectbox("Alternativa Correta:", ["A", "B", "C", "D"])
        
        btn_enviar = st.form_submit_button("🚀 CADASTRAR QUESTÃO NO BANCO")
        
        if btn_enviar:
            st.warning("⚠️ A interface de lançamento foi restaurada. Para salvar os dados nesta planilha, as 'Secrets' precisam estar configuradas corretamente.")

# --- ÁREA DA COORDENAÇÃO (Com Senha e Filtros) ---
else:
    st.subheader("🔑 Área Restrita da Coordenação")
    
    # B.O de Senha Resolvido
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso liberado!")
        
        try:
            # Carregamento dos dados via link público para evitar erro de conexão
            df = pd.read_csv(URL_PLANILHA)
            
            st.divider()
            st.write("### 🔍 Filtros para Exportação")
            
            # Filtros por disciplina
            lista_materias = df['Disciplina'].unique().tolist()
            filtro_materia = st.multiselect("Filtrar por Disciplina:", lista_materias)
            
            # Aplicando filtros
            if filtro_materia:
                df_final = df[df['Disciplina'].isin(filtro_materia)]
            else:
                df_final = df
            
            st.write(f"Total de questões selecionadas: **{len(df_final)}**")
            st.dataframe(df_final, use_container_width=True)
            
            # B.O de Download em PDF Resolvido
            if not df_final.empty:
                pdf_output = gerar_pdf_prova(df_final)
                st.download_button(
                    label="📄 BAIXAR PROVA FORMATADA (PDF)",
                    data=bytes(pdf_output),
                    file_name="simulado_padre_constantino.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"Erro ao acessar a planilha. Verifique se ela está pública. Detalhes: {e}")
            
    elif senha != "":
        st.error("Senha incorreta. Acesso negado.")
