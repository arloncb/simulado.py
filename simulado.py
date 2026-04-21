import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Conexão com a Planilha
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")

# 3. Navegação Lateral
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR (Lançamento) ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
    with st.form("form_simulado", clear_on_submit=True):
        col_prof, col_turma = st.columns([2, 1])
        with col_prof:
            nome_professor = st.text_input("Nome do(a) Professor(a):")
        with col_turma:
            turma = st.selectbox("Turma:", [
                "4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", 
                "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"
            ])

        col_disc, col_hab = st.columns([1, 1])
        with col_disc:
            disciplina = st.selectbox("Disciplina:", [
                "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de texto"
            ])
        with col_hab:
            habilidade = st.text_input("Habilidade MS (Ex: EF06LP01):")
            
        enunciado = st.text_area("Enunciado da Questão:", height=150)
        
        c1, c2 = st.columns(2)
        with c1:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
        with c2:
            alt_c = st.text_input("Alternativa C:")
            alt_d = st.text_input("Alternativa D:")
            
        gabarito = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_salvar = st.form_submit_button("🚀 CADASTRAR QUESTÃO")
        
        if btn_salvar:
            # Validação de campos obrigatórios
            campos = [nome_professor, habilidade, enunciado, alt_a, alt_b, alt_c, alt_d]
            if not all(campos):
                st.error("⚠️ Todos os campos são obrigatórios! Por favor, preencha tudo antes de enviar.")
            elif conn is not None:
                try:
                    df_antigo = conn.read(ttl=0)
                    nova_q = pd.DataFrame([{
                        "Professor(a)": nome_professor,
                        "Turma": turma,
                        "Disciplina": disciplina,
                        "Habilidade": habilidade,
                        "Enunciado": enunciado,
                        "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d,
                        "Gabarito": gabarito
                    }])
                    
                    df_atualizado = pd.concat([df_antigo, nova_q], ignore_index=True)
                    conn.update(data=df_atualizado)
                    st.success(f"✅ Questão de {disciplina} ({turma}) cadastrada com sucesso!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao gravar: {e}")

# --- ÁREA DA COORDENAÇÃO (Filtros e PDF) ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Senha da Coordenação:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso Autorizado")
        if conn is not None:
            try:
                df = conn.read(ttl=0)
                
                st.write("### 🔍 Filtros para Gerar Prova")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    f_turma = st.multiselect("Filtrar por Turma:", df['Turma'].unique())
                with col_f2:
                    f_disc = st.multiselect("Filtrar por Disciplina:", df['Disciplina'].unique())
                
                # Aplicação dos filtros
                df_filtrado = df.copy()
                if f_turma:
                    df_filtrado = df_filtrado[df_filtrado['Turma'].isin(f_turma)]
                if f_disc:
                    df_filtrado = df_filtrado[df_filtrado['Disciplina'].isin(f_disc)]
                
                st.dataframe(df_filtrado, use_container_width=True)
                
                if not df_filtrado.empty:
                    def criar_pdf_formatado(dados):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 16)
                        pdf.cell(0, 10, "E. E. Padre Constantino de Monte", ln=True, align='C')
                        pdf.set_font("Arial", "", 12)
                        pdf.cell(0, 10, "Simulado Escolar - 2026", ln=True, align='C')
                        pdf.ln(10)
                        
                        for i, r in dados.iterrows():
                            pdf.set_font("Arial", "B", 11)
                            pdf.multi_cell(0, 8, f"QUESTÃO {i+1} - {r['Disciplina']} ({r['Turma']})")
                            pdf.set_font("Arial", "I", 9)
                            pdf.cell(0, 6, f"Professor(a): {r['Professor(a)']} | Habilidade: {r['Habilidade']}", ln=True)
                            pdf.set_font("Arial", "", 11)
                            pdf.multi_cell(0, 7, str(r['Enunciado']))
                            pdf.cell(0, 7, f"A) {r['A']}", ln=True)
                            pdf.cell(0, 7, f"B) {r['B']}", ln=True)
                            pdf.cell(0, 7, f"C) {r['C']}", ln=True)
                            pdf.cell(0, 7, f"D) {r['D']}", ln=True)
                            pdf.ln(5)
                        return pdf.output(dest='S').encode('latin-1')

                    st.download_button(
                        "📄 BAIXAR PROVA EM PDF",
                        data=criar_pdf_formatado(df_filtrado),
                        file_name="simulado_escolar.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error("Erro ao carregar banco de dados.")
    elif senha != "":
        st.error("Senha Incorreta.")
