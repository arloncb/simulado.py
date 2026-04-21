import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Conexão com a Planilha (Usando o que está no seu requirements)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro de conexão. Verifique o seu Secrets no Streamlit Cloud.")

# 3. Navegação Lateral
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR (Lançamento Direto na Planilha) ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
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
            
        enunciado = st.text_area("Enunciado da Questão:", height=150)
        
        c1, c2 = st.columns(2)
        with c1:
            alt_a = st.text_input("Alternativa A:")
            alt_b = st.text_input("Alternativa B:")
        with c2:
            alt_c = st.text_input("Alternativa C:")
            alt_d = st.text_input("Alternativa D:")
            
        correta = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_salvar = st.form_submit_button("🚀 CADASTRAR NO BANCO DE DADOS")
        
        if btn_salvar:
            if enunciado and alt_a and habilidade:
                try:
                    # Lê o que já existe
                    df_antigo = conn.read(ttl=0)
                    
                    # Cria a nova linha
                    nova_linha = pd.DataFrame([{
                        "Disciplina": disciplina,
                        "Habilidade": habilidade,
                        "Enunciado": enunciado,
                        "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d,
                        "Gabarito": correta
                    }])
                    
                    # Junta tudo e envia de volta
                    df_atualizado = pd.concat([df_antigo, nova_linha], ignore_index=True)
                    conn.update(data=df_atualizado)
                    
                    st.success("✅ Sucesso! Questão gravada na planilha.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("Por favor, preencha o Enunciado e a Habilidade.")

# --- ÁREA DA COORDENAÇÃO (Filtros + Gerador de PDF) ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Digite a senha da Coordenação:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso Autorizado")
        
        try:
            df = conn.read(ttl=0)
            
            st.write("### 🔍 Filtros para Prova")
            lista_materias = df['Disciplina'].unique().tolist()
            selecao = st.multiselect("Filtrar Disciplinas:", lista_materias)
            
            df_final = df[df['Disciplina'].isin(selecao)] if selecao else df
            
            st.dataframe(df_final, use_container_width=True)
            
            if not df_final.empty:
                def gerar_pdf(dados):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0, 10, "Escola Estadual Padre Constantino de Monte", ln=True, align='C')
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

                st.download_button(
                    "📄 BAIXAR PROVA EM PDF",
                    data=gerar_pdf(df_final),
                    file_name="simulado_constantino.pdf",
                    mime="application/pdf"
                )
        except:
            st.error("Erro ao carregar banco de dados.")
    elif senha != "":
        st.error("Senha Incorreta.")
