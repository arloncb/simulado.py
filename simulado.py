import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── FUNÇÃO DE AUTO-CURA (FONTES) ─────────────────────────────────────────────
def garantir_fontes():
    fontes = {
        "DejaVuSans.ttf": "https://github.com/reingart/pyfpdf/raw/master/font/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf": "https://github.com/reingart/pyfpdf/raw/master/font/dejavu/DejaVuSans-Bold.ttf"
    }
    for nome, url in fontes.items():
        if not os.path.exists(nome):
            try:
                urllib.request.urlretrieve(url, nome)
            except:
                pass 

# ─── CSS CUSTOMIZADO ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .page-header {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: white;
    }
    .page-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
    .page-header p  { margin: 4px 0 0; opacity: 0.8; font-size: 0.95rem; }
    .section-label {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em;
        text-transform: uppercase; color: #6b7280; margin-bottom: 8px;
    }
    .metric-card {
        background: #f9fafb; border: 1px solid #e5e7eb;
        border-radius: 10px; padding: 16px 20px; text-align: center;
    }
    .metric-card .metric-value { font-size: 2rem; font-weight: 700; color: #1a3a2a; }
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1a3a2a, #2d6a4f);
        color: white; border: none; font-weight: 600; width: 100%;
        border-radius: 8px; padding: 0.65rem; transition: 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES ───────────────────────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Ensino Religioso", "Educação Física", "Leitura e Produção de texto"]
SENHA_COORD = "coord2026"

# Inicialização do session_state
_defaults = {"prof_nome": "", "prof_turma": "6° A", "prof_disc": "Língua Portuguesa", "q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": "", "q_e": "", "q_imagem": ""}
for k, v in _defaults.items():
    if k not in st.session_state: 
        st.session_state[k] = v

# Inicializa log de atividades
if "log_atividades" not in st.session_state:
    st.session_state.log_atividades = []

# ─── CONEXÃO ──────────────────────────────────────────────────────────────────
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro de conexão: {e}")

# ─── FUNÇÃO PARA CARREGAR DADOS COM CACHE ─────────────────────────────────────
@st.cache_data(ttl=30)
def carregar_dados():
    """Carrega os dados do Google Sheets com cache de 30 segundos"""
    if conn:
        try:
            return conn.read(ttl=0)
        except:
            return None
    return None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 SIDE")
    perfil = st.radio("Acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"], label_visibility="collapsed")
    st.divider()
    st.caption(f"📍 Maracaju/MS | 🗓️ {datetime.now().strftime('%d/%m/%Y')}")

st.markdown('<div class="page-header"><h1>📚 Portal de Simulados</h1><p>Escola Estadual Padre Constantino de Monte — SIDE</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DO PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    with st.form("form_simulado", clear_on_submit=False):
        st.markdown('<p class="section-label">👤 Identificação</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: 
            nome_professor = st.text_input("Nome do(a) Professor(a)*", value=st.session_state["prof_nome"])
        with c2: 
            idx_t = LISTA_TURMAS.index(st.session_state["prof_turma"]) if st.session_state["prof_turma"] in LISTA_TURMAS else 0
            turma = st.selectbox("Turma*", LISTA_TURMAS, index=idx_t)
        with c3:
            idx_d = LISTA_DISCS.index(st.session_state["prof_disc"]) if st.session_state["prof_disc"] in LISTA_DISCS else 0
            disciplina = st.selectbox("Disciplina*", LISTA_DISCS, index=idx_d)

        st.divider()
        st.markdown('<p class="section-label">📝 Questão</p>', unsafe_allow_html=True)
        habilidade = st.text_input("Habilidade MS*", value=st.session_state["q_hab"])
        enunciado = st.text_area("Pergunta*", value=st.session_state["q_enun"], height=150)
        
        # Link da imagem (opcional)
        link_imagem = st.text_input("🔗 Link da Imagem (opcional)", value=st.session_state["q_imagem"], 
                                    placeholder="https://exemplo.com/imagem.jpg")
        
        ca, cb = st.columns(2)
        with ca:
            alt_a = st.text_input("Alternativa A*", value=st.session_state["q_a"])
            alt_b = st.text_input("Alternativa B*", value=st.session_state["q_b"])
            alt_c = st.text_input("Alternativa C*", value=st.session_state["q_c"])
        with cb:
            alt_d = st.text_input("Alternativa D*", value=st.session_state["q_d"])
            alt_e = st.text_input("Alternativa E*", value=st.session_state["q_e"])

        gabarito = st.radio("✅ Alternativa Correta*", ["A", "B", "C", "D", "E"], horizontal=True)
        
        # Preview da questão
        with st.expander("👁️ Pré-visualizar questão", expanded=False):
            if enunciado:
                if link_imagem:
                    st.image(link_imagem, caption="Imagem da questão", use_container_width=True)
                st.markdown(f"**{enunciado}**")
                st.markdown(f"A) {alt_a if alt_a else '...'}")
                st.markdown(f"B) {alt_b if alt_b else '...'}")
                st.markdown(f"C) {alt_c if alt_c else '...'}")
                st.markdown(f"D) {alt_d if alt_d else '...'}")
                st.markdown(f"E) {alt_e if alt_e else '...'}")
                st.markdown(f"✅ **Alternativa Correta: {gabarito}**")
            else:
                st.info("Preencha a pergunta para pré-visualizar")
        
        btn_salvar = st.form_submit_button("🚀 Cadastrar Questão")

        if btn_salvar:
            # Validações
            if not nome_professor or not habilidade or not enunciado:
                st.error("⚠️ Preencha os campos obrigatórios (Nome, Habilidade e Pergunta).")
            elif not all([alt_a, alt_b, alt_c, alt_d, alt_e]):
                st.error("⚠️ Todas as alternativas (A, B, C, D, E) são obrigatórias.")
            elif conn:
                try:
                    # Carrega dados atuais
                    df_atual = carregar_dados()
                    
                    # Se não existir dados, cria DataFrame vazio com o cabeçalho correto
                    if df_atual is None or df_atual.empty:
                        df_atual = pd.DataFrame(columns=[
                            "Data", "Professor (a)", "Disciplina", "Turma", "Habilidade", 
                            "Pergunta", "A", "B", "C", "D", "E", "Correta", "Link Imagem"
                        ])
                    
                    # Cria nova linha com o cabeçalho correto
                    nova_linha = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Professor (a)": nome_professor,
                        "Disciplina": disciplina,
                        "Turma": turma,
                        "Habilidade": habilidade,
                        "Pergunta": enunciado,
                        "A": alt_a,
                        "B": alt_b,
                        "C": alt_c,
                        "D": alt_d,
                        "E": alt_e,
                        "Correta": gabarito,
                        "Link Imagem": link_imagem if link_imagem else ""
                    }])
                    
                    # Concatena e salva
                    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
                    conn.update(data=df_final)
                    
                    # Atualiza session_state
                    st.session_state.update({
                        "prof_nome": nome_professor, 
                        "prof_turma": turma,
                        "prof_disc": disciplina,
                        "q_hab": "", 
                        "q_enun": "", 
                        "q_a": "", 
                        "q_b": "", 
                        "q_c": "", 
                        "q_d": "",
                        "q_e": "",
                        "q_imagem": ""
                    })
                    
                    # Registra no log
                    st.session_state.log_atividades.append(
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Questão cadastrada por {nome_professor} ({disciplina} - {turma})"
                    )
                    
                    # Limpa cache para forçar recarga
                    st.cache_data.clear()
                    
                    st.success("✅ Questão salva com sucesso!")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e: 
                    st.error(f"Erro ao salvar: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DA COORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Área da Coordenação")
    senha = st.text_input("Senha de acesso:", type="password")

    if senha == SENHA_COORD:
        try:
            # Carrega dados com cache
            df = carregar_dados()
            
            if df is None or df.empty:
                st.info("📭 Nenhuma questão cadastrada ainda.")
            else:
                # Verifica se as colunas existem antes de usar
                colunas_necessarias = ["Turma", "Disciplina", "Professor (a)"]
                colunas_presentes = [col for col in colunas_necessarias if col in df.columns]
                
                if len(colunas_presentes) == len(colunas_necessarias):
                    st.markdown('<p class="section-label">🔍 Filtros para Exportação</p>', unsafe_allow_html=True)
                    f1, f2, f3 = st.columns(3)
                    
                    with f1:
                        if "Turma" in df.columns:
                            op_t = sorted([str(x) for x in df["Turma"].dropna().unique()])
                            f_turma = st.multiselect("Turma:", op_t)
                        else:
                            f_turma = []
                    
                    with f2:
                        if "Disciplina" in df.columns:
                            op_d = sorted([str(x) for x in df["Disciplina"].dropna().unique()])
                            f_disc = st.multiselect("Disciplina:", op_d)
                        else:
                            f_disc = []
                    
                    with f3:
                        if "Professor (a)" in df.columns:
                            op_p = sorted([str(x) for x in df["Professor (a)"].dropna().unique()])
                            f_prof = st.multiselect("Professor(a):", op_p)
                        else:
                            f_prof = []

                    # Aplica filtros
                    df_v = df.copy()
                    if f_turma and "Turma" in df_v.columns: 
                        df_v = df_v[df_v["Turma"].isin(f_turma)]
                    if f_disc and "Disciplina" in df_v.columns: 
                        df_v = df_v[df_v["Disciplina"].isin(f_disc)]
                    if f_prof and "Professor (a)" in df_v.columns: 
                        df_v = df_v[df_v["Professor (a)"].isin(f_prof)]
                else:
                    df_v = df.copy()
                    st.warning("⚠️ Algumas colunas esperadas não foram encontradas. Exibindo todos os dados sem filtros.")

                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total de Questões", len(df_v))
                with col2:
                    if "Turma" in df_v.columns:
                        st.metric("🏫 Turmas", df_v["Turma"].nunique())
                    else:
                        st.metric("🏫 Turmas", 0)
                with col3:
                    if "Disciplina" in df_v.columns:
                        st.metric("📚 Disciplinas", df_v["Disciplina"].nunique())
                    else:
                        st.metric("📚 Disciplinas", 0)

                st.divider()
                st.dataframe(df_v, use_container_width=True, hide_index=True)

                # Exportação
                exp1, exp2 = st.columns(2)
                with exp1:
                    csv = df_v.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        "⬇️ Baixar CSV (Excel)", 
                        data=csv, 
                        file_name=f"simulado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
                        use_container_width=True
                    )
                
                with exp2:
                    if st.button("📄 Gerar e Baixar Banco de Questões PDF", use_container_width=True):
                        if df_v.empty:
                            st.warning("⚠️ Não há questões para gerar o PDF.")
                        else:
                            with st.spinner("Gerando PDF..."):
                                garantir_fontes()
                                pdf = FPDF()
                                pdf.set_auto_page_break(auto=True, margin=20)
                                
                                usar_unicode = False
                                if os.path.exists("DejaVuSans.ttf"):
                                    pdf.add_font("SideFont", "", "DejaVuSans.ttf", uni=True)
                                    pdf.add_font("SideFont", "B", "DejaVuSans-Bold.ttf", uni=True)
                                    fn, usar_unicode = "SideFont", True
                                else:
                                    fn = "Helvetica"

                                def clean(val):
                                    if pd.isna(val) or val is None: 
                                        return ""
                                    t = str(val).strip()
                                    return t if usar_unicode else t.encode('latin-1', 'replace').decode('latin-1')

                                # Página de rosto
                                pdf.add_page()
                                pdf.set_font(fn, "B", 16)
                                pdf.cell(0, 10, clean("SIDE - Sistema Integrado de Desempenho Escolar"), ln=True, align="C")
                                pdf.ln(5)
                                pdf.set_font(fn, "", 12)
                                pdf.cell(0, 8, clean("Banco de Questões para Simulados"), ln=True, align="C")
                                pdf.cell(0, 8, clean(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"), ln=True, align="C")
                                pdf.cell(0, 8, clean(f"Total de questões: {len(df_v)}"), ln=True, align="C")
                                
                                l_util = pdf.w - 2 * pdf.l_margin
                                gabs = []
                                
                                # Questões
                                for idx, (_, r) in enumerate(df_v.iterrows(), 1):
                                    pdf.add_page()
                                    
                                    # Gabarito
                                    correta = r.get('Correta', 'N/A')
                                    gabs.append(f"Q{idx}: {correta}")
                                    
                                    # Cabeçalho da questão
                                    pdf.set_font(fn, "B", 10)
                                    header_txt = f"QUESTÃO {idx:02d} | {r.get('Disciplina', 'N/A')} | ({r.get('Habilidade', 'N/A')}) | Turma: {r.get('Turma', 'N/A')}"
                                    pdf.multi_cell(l_util, 6, clean(header_txt))
                                    pdf.ln(2)
                                    
                                    # Enunciado
                                    pdf.set_font(fn, "", 11)
                                    pergunta = clean(r.get("Pergunta"))
                                    if pergunta:
                                        pdf.multi_cell(l_util, 6, pergunta)
                                    pdf.ln(4)
                                    
                                    # Alternativas (A, B, C, D, E)
                                    pdf.set_font(fn, "", 10)
                                    for l in ["A", "B", "C", "D", "E"]:
                                        texto_alt = clean(r.get(l))
                                        if texto_alt:
                                            pdf.set_x(pdf.l_margin + 8)
                                            # Destaca a alternativa correta
                                            if l == correta:
                                                pdf.set_font(fn, "B", 10)
                                                pdf.multi_cell(l_util - 8, 6, clean(f"({l}) {texto_alt} ✓"))
                                                pdf.set_font(fn, "", 10)
                                            else:
                                                pdf.multi_cell(l_util - 8, 6, clean(f"({l}) {texto_alt}"))
                                    
                                    pdf.ln(4)
                                    pdf.set_draw_color(200, 200, 200)
                                    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin, pdf.get_y())
                                    pdf.set_draw_color(0, 0, 0)
                                    pdf.ln(6)

                                # Gabarito
                                pdf.add_page()
                                pdf.set_font(fn, "B", 14)
                                pdf.cell(l_util, 10, clean("GABARITO DE REFERÊNCIA"), ln=True, align="C")
                                pdf.ln(8)
                                pdf.set_font(fn, "", 11)
                                for i in range(0, len(gabs), 3):
                                    pdf.cell(60, 8, clean(gabs[i]))
                                    if i+1 < len(gabs): 
                                        pdf.cell(60, 8, clean(gabs[i+1]))
                                    if i+2 < len(gabs): 
                                        pdf.cell(60, 8, clean(gabs[i+2]))
                                    pdf.ln()
                                
                                # Botão de download do PDF
                                pdf_bytes = bytes(pdf.output())
                                st.download_button(
                                    "⬇️ Baixar Banco de Questões (PDF)", 
                                    data=pdf_bytes, 
                                    file_name=f"banco_questoes_side_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                    use_container_width=True,
                                    key="download_pdf"
                                )
                                
                                st.success("✅ PDF gerado com sucesso!")

                # Log de atividades (apenas para coordenação)
                if st.session_state.log_atividades:
                    with st.expander("📋 Log de Atividades", expanded=False):
                        for log in st.session_state.log_atividades[-10:]:
                            st.text(log)

        except Exception as e:
            st.error(f"Erro ao processar os dados: {e}")
            st.info("Verifique se a planilha do Google Sheets está configurada corretamente.")
            
    elif senha:
        st.error("❌ Senha incorreta. Tente novamente.")
