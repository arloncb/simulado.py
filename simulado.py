import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Inicialização do Estado (Memória do Sistema)
if 'nome_professor' not in st.session_state: st.session_state.nome_professor = ""
if 'turma' not in st.session_state: st.session_state.turma = "6° A"
if 'disciplina' not in st.session_state: st.session_state.disciplina = "Língua Portuguesa"
# Campos que serão limpos após o sucesso
if 'habilidade' not in st.session_state: st.session_state.habilidade = ""
if 'enunciado' not in st.session_state: st.session_state.enunciado = ""
if 'alt_a' not in st.session_state: st.session_state.alt_a = ""
if 'alt_b' not in st.session_state: st.session_state.alt_b = ""
if 'alt_c' not in st.session_state: st.session_state.alt_c = ""
if 'alt_d' not in st.session_state: st.session_state.alt_d = ""

# 3. Conexão com a Planilha
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")

# 4. Navegação Lateral
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
    # clear_on_submit=False para não apagar nada em caso de erro de validação
    with st.form("form_simulado", clear_on_submit=False):
        col_prof, col_turma = st.columns([2, 1])
        with col_prof:
            nome_professor = st.text_input("Nome do(a) Professor(a):", value=st.session_state.nome_professor)
        with col_turma:
            turma = st.selectbox("Turma:", [
                "4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", 
                "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"
            ], index=["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", 
                "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"].index(st.session_state.turma))

        col_disc, col_hab = st.columns([1, 1])
        with col_disc:
            disciplina = st.selectbox("Disciplina:", [
                "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de texto"
            ], index=["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", 
                "Ciências", "História", "Geografia", "Ensino Religioso", 
                "Educação Física", "Leitura e Produção de texto"].index(st.session_state.disciplina))
        
        with col_hab:
            habilidade = st.text_input("Habilidade MS (Ex: EF06LP01):", value=st.session_state.habilidade)
            
        enunciado = st.text_area("Enunciado da Questão:", value=st.session_state.enunciado, height=150)
        
        c1, c2 = st.columns(2)
        with c1:
            alt_a = st.text_input("Alternativa A:", value=st.session_state.alt_a)
            alt_b = st.text_input("Alternativa B:", value=st.session_state.alt_b)
        with c2:
            alt_c = st.text_input("Alternativa C:", value=st.session_state.alt_c)
            alt_d = st.text_input("Alternativa D:", value=st.session_state.alt_d)
            
        gabarito = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_salvar = st.form_submit_button("🚀 CADASTRAR QUESTÃO")
        
        if btn_salvar:
            # Salvar dados no estado para persistência imediata
            st.session_state.nome_professor = nome_professor
            st.session_state.turma = turma
            st.session_state.disciplina = disciplina
            st.session_state.habilidade = habilidade
            st.session_state.enunciado = enunciado
            st.session_state.alt_a = alt_a
            st.session_state.alt_b = alt_b
            st.session_state.alt_c = alt_c
            st.session_state.alt_d = alt_d

            campos_obrigatorios = [nome_professor, habilidade, enunciado, alt_a, alt_b, alt_c, alt_d]
            
            if not all(campos_obrigatorios):
                st.error("⚠️ Erro: Todos os campos são obrigatórios! O conteúdo digitado foi mantido para sua correção.")
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
                    
                    # SUCESSO: Limpamos apenas o conteúdo da questão, mantendo Prof/Turma/Disc
                    st.session_state.habilidade = ""
                    st.session_state.enunciado = ""
                    st.session_state.alt_a = ""
                    st.session_state.alt_b = ""
                    st.session_state.alt_c = ""
                    st.session_state.alt_d = ""
                    
                    st.success(f"✅ Questão cadastrada com sucesso! Os campos de Professor e Turma foram mantidos para o próximo lançamento.")
                    st.rerun() # Reinicia para aplicar a limpeza dos campos de questão
                    
                except Exception as e:
                    st.error(f"Erro ao gravar: {e}")

# --- ÁREA DA COORDENAÇÃO ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Senha da Coordenação:", type="password")
    
    if senha == "coord2026":
        st.success("Acesso Autorizado")
        if conn is not None:
            try:
                df = conn.read(ttl=0)
                st.write("### 🔍 Banco de Questões")
                
                c_f1, c_f2 = st.columns(2)
                with c_f1: f_turma = st.multiselect("Filtrar por Turma:", df['Turma'].unique())
                with c_f2: f_disc = st.multiselect("Filtrar por Disciplina:", df['Disciplina'].unique())
                
                df_filtrado = df.copy()
                if f_turma: df_filtrado = df_filtrado[df_filtrado['Turma'].isin(f_turma)]
                if f_disc: df_filtrado = df_filtrado[df_filtrado['Disciplina'].isin(f_disc)]
                
                st.dataframe(df_filtrado, use_container_width=True)
                
                if not df_filtrado.empty:
                    def criar_pdf(dados):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(0, 10, "E. E. Padre Constantino de Monte", ln=True, align='C')
                        pdf.ln(5)
                        for i, r in dados.iterrows():
                            pdf.set_font("Arial", "B", 11)
                            pdf.multi_cell(0, 8, f"QUESTÃO {i+1} - {r['Disciplina']} ({r['Turma']})")
                            pdf.set_font("Arial", "I", 9)
                            pdf.cell(0, 6, f"Prof: {r['Professor(a)']} | Hab: {r['Habilidade']}", ln=True)
                            pdf.set_font("Arial", "", 11)
                            pdf.multi_cell(0, 7, str(r['Enunciado']))
                            pdf.cell(0, 7, f"A) {r['A']}  B) {r['B']}  C) {r['C']}  D) {r['D']}", ln=True)
                            pdf.ln(4)
                        return pdf.output(dest='S').encode('latin-1')

                    st.download_button("📄 BAIXAR PROVA EM PDF", data=criar_pdf(df_filtrado), file_name="simulado.pdf")
            except:
                st.error("Erro ao carregar banco de dados.")
    elif senha != "":
        st.error("Senha Incorreta.")
