import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Conexão com a Planilha (Definindo 'conn' de forma global)
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro Crítico de Conexão: {e}. Verifique as chaves no Secrets.")

# 3. Navegação Lateral
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR ---
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
        
        btn_salvar = st.form_submit_button("🚀 CADASTRAR NO BANCO DE DADOS")
        
        if btn_salvar:
            if conn is None:
                st.error("Não é possível salvar: Conexão com a planilha não estabelecida.")
            elif not enunciado or not habilidade or not alt_a:
                st.warning("Preencha o enunciado, a habilidade e as alternativas.")
            else:
                try:
                    # Tenta ler os dados atuais
                    df_existente = conn.read(ttl=0)
                    
                    # Nova linha
                    nova_q = pd.DataFrame([{
                        "Disciplina": disciplina,
                        "Habilidade": habilidade,
                        "Enunciado": enunciado,
                        "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d,
                        "Gabarito": gabarito
                    }])
                    
                    # Atualiza a planilha
                    df_final = pd.concat([df_existente, nova_q], ignore_index=True)
                    conn.update(data=df_final)
                    st.success("✅ Questão cadastrada com sucesso!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao gravar dados: {e}")

# --- ÁREA DA COORDENAÇÃO ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Senha da Coordenação:", type="password")
    
    if senha == "coord2026":
        if conn is not None:
            try:
                df = conn.read(ttl=0)
                st.write("### 🔍 Banco de Questões")
                
                filtro = st.multiselect("Filtrar Disciplinas:", df['Disciplina'].unique())
                df_filtro = df[df['Disciplina'].isin(filtro)] if filtro else df
                
                st.dataframe(df_filtro, use_container_width=True)
                
                if not df_filtro.empty:
                    # Função PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, "Escola Estadual Padre Constantino de Monte", ln=True, align='C')
                    pdf.ln(10)
                    
                    for i, r in df_filtro.iterrows():
                        pdf.set_font("Arial", "B", 11)
                        pdf.multi_cell(0, 8, f"QUESTÃO {i+1} - {r['Disciplina']}")
                        pdf.set_font("Arial", "I", 9)
                        pdf.cell(0, 6, f"Habilidade: {r['Habilidade']}", ln=True)
                        pdf.set_font("Arial", "", 11)
                        pdf.multi_cell(0, 7, str(r['Enunciado']))
                        pdf.cell(0, 7, f"A) {r['A']}", ln=True)
                        pdf.cell(0, 7, f"B) {r['B']}", ln=True)
                        pdf.ln(4)
                    
                    st.download_button("📄 BAIXAR PDF", pdf.output(dest='S').encode('latin-1'), "simulado.pdf")
            except:
                st.error("Erro ao ler a planilha.")
        else:
            st.error("Conexão indisponível.")
    elif senha != "":
        st.error("Senha incorreta.")
