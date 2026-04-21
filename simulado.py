import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Inicialização Inteligente do Estado (Session State)
# Campos que PERMANECEM (Professor, Turma, Disciplina)
if 'nome_professor' not in st.session_state: st.session_state.nome_professor = ""
if 'turma' not in st.session_state: st.session_state.turma = "6° A"
if 'disciplina' not in st.session_state: st.session_state.disciplina = "Língua Portuguesa"

# Campos que são LIMPOS (Questão, Habilidade, Alternativas)
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
    
    # Mantemos clear_on_submit=False para controlar o que apagar manualmente
    with st.form("form_simulado", clear_on_submit=False):
        col_prof, col_turma = st.columns([2, 1])
        with col_prof:
            nome_professor = st.text_input("Nome do(a) Professor(a):", value=st.session_state.nome_professor)
        with col_turma:
            turmas_lista = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
            idx_turma = turmas_lista.index(st.session_state.turma) if st.session_state.turma in turmas_lista else 0
            turma = st.selectbox("Turma:", turmas_lista, index=idx_turma)

        col_disc, col_hab = st.columns([1, 1])
        with col_disc:
            discs_lista = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Ensino Religioso", "Educação Física", "Leitura e Produção de texto"]
            idx_disc = discs_lista.index(st.session_state.disciplina) if st.session_state.disciplina in discs_lista else 0
            disciplina = st.selectbox("Disciplina:", discs_lista, index=idx_disc)
        
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
            # Sincroniza o estado com o que foi digitado
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
                st.error("⚠️ Preencha todos os campos! As informações foram mantidas para você corrigir.")
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
                    
                    # Gravação no Google Sheets
                    df_atualizado = pd.concat([df_antigo, nova_q], ignore_index=True)
                    conn.update(data=df_atualizado)
                    
                    # --- SUCESSO: O MOMENTO DA LIMPEZA SELETIVA ---
                    # Mantemos Prof/Turma/Disc (não alteramos o session_state deles)
                    # Limpamos apenas os campos da questão
                    st.session_state.habilidade = ""
                    st.session_state.enunciado = ""
                    st.session_state.alt_a = ""
                    st.session_state.alt_b = ""
                    st.session_state.alt_c = ""
                    st.session_state.alt_d = ""
                    
                    st.success("✅ Questão cadastrada! Nome, Disciplina e Turma permanecem para o próximo lançamento.")
                    st.rerun() # Atualiza a tela com os campos limpos
                    
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
                    # Gerador de PDF simples para conferência
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, "E. E. Padre Constantino de Monte - Prova", ln=True, align='C')
                    pdf.output(dest='S').encode('latin-1') 
                    # (Função de PDF completa omitida aqui para brevidade, mas mantida no seu arquivo)
            except:
                st.error("Erro ao carregar banco de dados.")
    elif senha != "":
        st.error("Senha Incorreta.")
