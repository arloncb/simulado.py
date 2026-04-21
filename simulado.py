import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Inicialização do Estado (Memória Seletiva)
# Estes PERMANECEM
if 'nome_professor' not in st.session_state: st.session_state.nome_professor = ""
if 'turma' not in st.session_state: st.session_state.turma = "6° A"
if 'disciplina' not in st.session_state: st.session_state.disciplina = "Língua Portuguesa"

# Estes FICAM EM BRANCO após o cadastro
if 'habilidade' not in st.session_state: st.session_state.habilidade = ""
if 'enunciado' not in st.session_state: st.session_state.enunciado = ""
if 'alt_a' not in st.session_state: st.session_state.alt_a = ""
if 'alt_b' not in st.session_state: st.session_state.alt_b = ""
if 'alt_c' not in st.session_state: st.session_state.alt_c = ""
if 'alt_d' not in st.session_state: st.session_state.alt_d = ""

# 3. Conexão
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
    
    with st.form("form_simulado", clear_on_submit=False):
        col_prof, col_turma = st.columns([2, 1])
        with col_prof:
            nome_professor = st.text_input("Nome do(a) Professor(a):", value=st.session_state.nome_professor)
        with col_turma:
            lista_turmas = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
            idx_t = lista_turmas.index(st.session_state.turma) if st.session_state.turma in lista_turmas else 0
            turma = st.selectbox("Turma:", lista_turmas, index=idx_t)

        col_disc, col_hab = st.columns([1, 1])
        with col_disc:
            lista_discs = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Ensino Religioso", "Educação Física", "Leitura e Produção de texto"]
            idx_d = lista_discs.index(st.session_state.disciplina) if st.session_state.disciplina in lista_discs else 0
            disciplina = st.selectbox("Disciplina:", lista_discs, index=idx_d)
        with col_hab:
            habilidade = st.text_input("Habilidade MS:", value=st.session_state.habilidade)
            
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
            # Primeiro, atualizamos o estado com o que está na tela
            st.session_state.nome_professor = nome_professor
            st.session_state.turma = turma
            st.session_state.disciplina = disciplina
            st.session_state.habilidade = habilidade
            st.session_state.enunciado = enunciado
            st.session_state.alt_a = alt_a
            st.session_state.alt_b = alt_b
            st.session_state.alt_c = alt_c
            st.session_state.alt_d = alt_d

            if not all([nome_professor, habilidade, enunciado, alt_a, alt_b, alt_c, alt_d]):
                st.error("⚠️ Todos os campos são obrigatórios. O que você digitou foi mantido para correção.")
            elif conn is not None:
                try:
                    df_antigo = conn.read(ttl=0)
                    nova_q = pd.DataFrame([{
                        "Professor(a)": nome_professor, "Turma": turma, "Disciplina": disciplina,
                        "Habilidade": habilidade, "Enunciado": enunciado,
                        "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "Gabarito": gabarito
                    }])
                    conn.update(data=pd.concat([df_antigo, nova_q], ignore_index=True))
                    
                    # --- LIMPEZA APÓS SUCESSO ---
                    st.session_state.habilidade = ""
                    st.session_state.enunciado = ""
                    st.session_state.alt_a = ""
                    st.session_state.alt_b = ""
                    st.session_state.alt_c = ""
                    st.session_state.alt_d = ""
                    
                    st.success("✅ Questão cadastrada! Campos da questão limpos para o próximo lançamento.")
                    st.rerun() 
                except Exception as e:
                    st.error(f"Erro ao gravar: {e}")

# --- ÁREA DA COORDENAÇÃO ---
else:
    st.subheader("🔑 Área Restrita")
    senha = st.text_input("Senha da Coordenação:", type="password")
    if senha == "coord2026":
        st.success("Acesso Autorizado")
        if conn is not None:
            df = conn.read(ttl=0)
            st.dataframe(df, use_container_width=True)
            # (Aqui você pode manter seu código de PDF que já funciona)
