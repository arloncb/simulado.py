import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página e Identidade
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Conexão com a Planilha (Usando o que está no seu requirements)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Sidebar - Perfil e Navegação
with st.sidebar:
    st.header("⚙️ Acesso ao Sistema")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR (Lançamento Real) ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões BNCC/MS")
    
    with st.form("form_simulado", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            disciplina = st.selectbox("Disciplina:", [
                "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de texto"
            ])
        with col2:
            habilidade = st.text_input("Habilidade MS:", placeholder="Ex: EF06LP01")
            
        enunciado = st.text_area("Enunciado da Questão:")
        
        c1, c2 = st.columns(2)
        with c1:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
        with c2:
            alt_c = st.text_input("Alternativa C:")
            alt_d = st.text_input("Alternativa D:")
            
        correta = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_salvar = st.form_submit_button("🚀 CADASTRAR NA PLANILHA")
        
        if btn_salvar:
            if enunciado and alt_a and habilidade:
                # Criando o novo dado
                nova_questao = pd.DataFrame([{
                    "Disciplina": disciplina,
                    "Habilidade": habilidade,
                    "Enunciado": enunciado,
                    "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d,
                    "Gabarito": correta
                }])
                
                # Buscando dados existentes e adicionando o novo
                try:
                    existentes = conn.read(ttl=0) # ttl=0 força a leitura atualizada
                    dados_atualizados = pd.concat([existentes, nova_questao], ignore_index=True)
                    conn.update(data=dados_atualizados)
                    st.success("✅ Questão cadastrada com sucesso no Banco de Dados!")
                except Exception as e:
                    st.error("Erro ao gravar. Verifique se o Secrets está configurado.")
            else:
                st.warning("Preencha todos os campos antes de cadastrar.")

# --- ÁREA DA COORDENAÇÃO (Filtros + PDF) ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Senha da Coordenação:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso Autorizado")
        
        try:
            df = conn.read(ttl=0)
            
            st.write("### 🔍 Filtros para Gerar Prova")
            materias = st.multiselect("Filtrar por Disciplina:", df['Disciplina'].unique())
            
            df_prova = df[df['Disciplina'].isin(materias)] if materias else df
            
            st.dataframe(df_prova, use_container_width=True)
            
            if not df_prova.empty:
                # Função para gerar PDF
                def criar_pdf(dados):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0, 10, "E. E. Padre Constantino de Monte", ln=True, align='C')
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(0, 10, "Simulado Escolar - 2026", ln=True, align='C')
                    pdf.ln(10)
                    
                    for i, r in dados.iterrows():
                        pdf.set_font("Arial", "B", 11)
                        pdf.multi_cell(0, 8, f"QUESTÃO {i+1} - {r['Disciplina']}")
                        pdf.set_font("Arial", "I", 9)
                        pdf.cell(0, 6, f"Habilidade: {r['Habilidade']}", ln=True)
                        pdf.set_font("Arial", "", 11)
                        pdf.multi_cell(0, 7, str(r['Enunciado']))
                        pdf.cell(0, 7, f"A) {r['A']}", ln=True)
                        pdf.cell(0, 7, f"B) {r['B']}", ln=True)
                        pdf.cell(0, 7, f"C) {r['C']}", ln=True)
                        pdf.cell(0, 7, f"D) {r['D']}", ln=True)
                        pdf.ln(5)
                    return pdf.output(dest='S').encode('latin-1')

                btn_pdf = st.download_button(
                    "📄 BAIXAR PROVA EM PDF",
                    data=criar_pdf(df_prova),
                    file_name="prova_simulado.pdf",
                    mime="application/pdf"
                )
        except:
            st.error("Planilha não encontrada. Verifique o link no Secrets.")
    elif senha != "":
        st.error("Senha Incorreta")
