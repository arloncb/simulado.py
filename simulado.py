import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# 1. Configurações e Identidade
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# Link da sua Planilha Pública (Ajustado para exportação CSV direta)
# Este método NÃO usa Secrets, evitando o erro de conexão.
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1bHaPE2WA7vEYR8Gr9DMHgRku7dtapo2R3pJ7ODuM2T8/export?format=csv"

# 2. Navegação Lateral
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("Sistema SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
    with st.form("form_simulado", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Disciplinas atualizadas conforme BNCC e solicitações
            disciplina = st.selectbox("Disciplina:", [
                "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de texto"
            ])
            
        with col2:
            # Campo Habilidade solicitado
            habilidade = st.text_input("Habilidade MS (Ex: EF06LP01):")
            
        enunciado = st.text_area("Enunciado da Questão:", height=150)
        
        c_a, c_b = st.columns(2)
        with c_a:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
        with c_b:
            alt_c = st.text_input("Alternativa C:")
            alt_d = st.text_input("Alternativa D:")
            
        gabarito = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_enviar = st.form_submit_button("🚀 CADASTRAR QUESTÃO")
        
        if btn_enviar:
            # Aviso honesto sobre a gravação
            st.warning("⚠️ O App agora carrega os dados, mas para GRAVAR diretamente sem erro de 'Secrets', "
                       "recomendamos usar o Google Forms vinculado à planilha. "
                       "Deseja que eu te ajude a criar o link do Forms?")

# --- ÁREA DA COORDENAÇÃO (Com Senha e Gerador de PDF) ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso liberado!")
        
        try:
            # Leitura direta via Pandas (Sem usar st.connection ou Secrets)
            df = pd.read_csv(URL_PLANILHA)
            
            st.divider()
            st.write("### 🔍 Banco de Questões e Filtros")
            
            materias = df['Disciplina'].unique().tolist() if 'Disciplina' in df.columns else []
            filtro = st.multiselect("Filtrar Matérias para a Prova:", materias)
            
            df_final = df[df['Disciplina'].isin(filtro)] if filtro else df
            
            st.write(f"Questões selecionadas: **{len(df_final)}**")
            st.dataframe(df_final, use_container_width=True)
            
            if not df_final.empty:
                # Função interna para gerar o PDF formatado
                def criar_pdf_prova(dados):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("helvetica", "B", 16)
                    pdf.cell(0, 10, "Escola Estadual Padre Constantino de Monte", ln=True, align="C")
                    pdf.set_font("helvetica", "", 12)
                    pdf.cell(0, 10, "Simulado Escolar - 2026", ln=True, align="C")
                    pdf.line(10, 32, 200, 32)
                    pdf.ln(10)
                    
                    for i, row in dados.iterrows():
                        pdf.set_font("helvetica", "B", 11)
                        pdf.multi_cell(0, 8, f"QUESTÃO {i+1} - {row.get('Disciplina', 'N/A')}")
                        pdf.set_font("helvetica", "I", 9)
                        pdf.multi_cell(0, 6, f"Habilidade MS: {row.get('Habilidade', 'N/A')}")
                        pdf.ln(2)
                        pdf.set_font("helvetica", "", 11)
                        pdf.multi_cell(0, 7, str(row.get('Enunciado', '')))
                        pdf.cell(0, 7, f"A) {row.get('A', '')}", ln=True)
                        pdf.cell(0, 7, f"B) {row.get('B', '')}", ln=True)
                        pdf.cell(0, 7, f"C) {row.get('C', '')}", ln=True)
                        pdf.cell(0, 7, f"D) {row.get('D', '')}", ln=True)
                        pdf.ln(6)
                    return pdf.output()

                # Botão de Download do PDF
                pdf_output = criar_pdf_prova(df_final)
                st.download_button(
                    label="📄 BAIXAR PROVA EM PDF",
                    data=bytes(pdf_output),
                    file_name="simulado_padre_constantino.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Erro ao carregar os dados. Verifique se a planilha está como 'Qualquer pessoa com o link'. Erro: {e}")
            
    elif senha != "":
        st.error("Senha incorreta.")
