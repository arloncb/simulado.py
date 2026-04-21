import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF

# 1. Configurações da Página
st.set_page_config(page_title="SIDE - Portal de Simulados", layout="wide")
st.title("📚 Portal de Simulados")
st.markdown("**Escola Estadual Padre Constantino de Monte**")
st.divider()

# 2. Inicialização do Estado (Chaves Fixas e Chaves de Questão)
# Se as chaves não existem, criamos. Se existem, o formulário as usará.
if 'prof_nome' not in st.session_state: st.session_state['prof_nome'] = ""
if 'prof_turma' not in st.session_state: st.session_state['prof_turma'] = "6° A"
if 'prof_disc' not in st.session_state: st.session_state['prof_disc'] = "Língua Portuguesa"

# Chaves da questão que precisam zerar
if 'q_hab' not in st.session_state: st.session_state['q_hab'] = ""
if 'q_enun' not in st.session_state: st.session_state['q_enun'] = ""
if 'q_a' not in st.session_state: st.session_state['q_a'] = ""
if 'q_b' not in st.session_state: st.session_state['q_b'] = ""
if 'q_c' not in st.session_state: st.session_state['q_c'] = ""
if 'q_d' not in st.session_state: st.session_state['q_d'] = ""

# 3. Conexão
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")

# 4. Sidebar
with st.sidebar:
    st.header("⚙️ Acesso")
    perfil = st.radio("Selecione seu Perfil:", ["Professor (a)", "Coordenação"])
    st.divider()
    st.info("SIDE - Maracaju/MS")

# --- ÁREA DO PROFESSOR ---
if perfil == "Professor (a)":
    st.subheader("👨‍🏫 Lançamento de Questões")
    
    # IMPORTANTE: Usamos os valores vindos do session_state
    with st.form("form_simulado"):
        col_prof, col_turma = st.columns([2, 1])
        with col_prof:
            nome_professor = st.text_input("Nome do(a) Professor(a):", value=st.session_state['prof_nome'])
        with col_turma:
            lista_turmas = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
            idx_t = lista_turmas.index(st.session_state['prof_turma']) if st.session_state['prof_turma'] in lista_turmas else 0
            turma = st.selectbox("Turma:", lista_turmas, index=idx_t)

        col_disc, col_hab = st.columns([1, 1])
        with col_disc:
            lista_discs = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Ensino Religioso", "Educação Física", "Leitura e Produção de texto"]
            idx_d = lista_discs.index(st.session_state['prof_disc']) if st.session_state['prof_disc'] in lista_discs else 0
            disciplina = st.selectbox("Disciplina:", lista_discs, index=idx_d)
        
        with col_hab:
            habilidade = st.text_input("Habilidade MS:", value=st.session_state['q_hab'])
            
        enunciado = st.text_area("Enunciado da Questão:", value=st.session_state['q_enun'], height=150)
        
        c1, c2 = st.columns(2)
        with c1:
            alt_a = st.text_input("Alternativa A:", value=st.session_state['q_a'])
            alt_b = st.text_input("Alternativa B:", value=st.session_state['q_b'])
        with c2:
            alt_c = st.text_input("Alternativa C:", value=st.session_state['q_c'])
            alt_d = st.text_input("Alternativa D:", value=st.session_state['q_d'])
            
        gabarito = st.selectbox("Gabarito:", ["A", "B", "C", "D"])
        
        btn_salvar = st.form_submit_button("🚀 CADASTRAR QUESTÃO")
        
        if btn_salvar:
            # 1. Validar se os campos obrigatórios estão preenchidos
            if not all([nome_professor, habilidade, enunciado, alt_a, alt_b, alt_c, alt_d]):
                # Se faltar algo, mantemos os dados no estado e avisamos
                st.session_state['prof_nome'] = nome_professor
                st.session_state['prof_turma'] = turma
                st.session_state['prof_disc'] = disciplina
                st.session_state['q_hab'] = habilidade
                st.session_state['q_enun'] = enunciado
                st.session_state['q_a'] = alt_a
                st.session_state['q_b'] = alt_b
                st.session_state['q_c'] = alt_c
                st.session_state['q_d'] = alt_d
                st.error("⚠️ Todos os campos são obrigatórios!")
            
            elif conn is not None:
                try:
                    # 2. Gravar na Planilha
                    df_antigo = conn.read(ttl=0)
                    nova_q = pd.DataFrame([{
                        "Professor(a)": nome_professor, "Turma": turma, "Disciplina": disciplina,
                        "Habilidade": habilidade, "Enunciado": enunciado,
                        "A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "Gabarito": gabarito
                    }])
                    conn.update(data=pd.concat([df_antigo, nova_q], ignore_index=True))
                    
                    # 3. SUCESSO: LIMPEZA SELETIVA
                    # Mantemos o que o professor é
                    st.session_state['prof_nome'] = nome_professor
                    st.session_state['prof_turma'] = turma
                    st.session_state['prof_disc'] = disciplina
                    
                    # ZERAMOS o que é da questão
                    st.session_state['q_hab'] = ""
                    st.session_state['q_enun'] = ""
                    st.session_state['q_a'] = ""
                    st.session_state['q_b'] = ""
                    st.session_state['q_c'] = ""
                    st.session_state['q_d'] = ""
                    
                    st.success("✅ Questão cadastrada! Próxima questão liberada.")
                    st.rerun() # O rerun forçará os inputs a lerem os novos valores ("") do session_state
                    
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
            # Botão de download PDF omitido aqui para brevidade, mas pode ser mantido.
