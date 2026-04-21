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
    """Baixa as fontes necessárias para o PDF se não existirem localmente."""
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

# ─── CSS CUSTOMIZADO (DESIGN ORIGINAL PRESERVADO) ──────────────────────────────
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
    .metric-card .metric-value { font-size: 2rem; font-weight: 700; color: #1a3a2a; line-height: 1.2; }
    .metric-card .metric-label { font-size: 0.8rem; color: #6b7280; }
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1a3a2a, #2d6a4f);
        color: white; border: none; font-weight: 600; width: 100%;
        border-radius: 8px; padding: 0.65rem; transition: 0.2s;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { opacity: 0.85; }
    .char-count { font-size: 0.78rem; color: #9ca3af; margin-top: -10px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES E ESTADO INICIAL ──────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Ensino Religioso", "Educação Física", "Leitura e Produção de texto"]
SENHA_COORD = "coord2026"

_defaults = {"prof_nome": "", "prof_turma": "6° A", "prof_disc": "Língua Portuguesa", "q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": ""}
for k, v in _defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ─── CONEXÃO COM GOOGLE SHEETS ────────────────────────────────────────────────
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ Erro de conexão com a planilha: {e}")

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 SIDE")
    st.markdown("**Portal de Simulados**")
    st.divider()
    perfil = st.radio("Perfil:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"], label_visibility="collapsed")
    st.divider()
    st.caption(f"📍 Maracaju/MS")
    st.caption(f"🗓️ {datetime.now().strftime('%d/%m/%Y')}")

# ─── CABEÇALHO PRINCIPAL ──────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>📚 Portal de Simulados</h1>
    <p>Escola Estadual Padre Constantino de Monte — SIDE Maracaju/MS</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DO PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    with st.form("form_simulado", clear_on_submit=False):
        st.markdown('<p class="section-label">👤 Identificação</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            nome_professor = st.text_input("Nome do(a) Professor(a)*", value=st.session_state["prof_nome"], placeholder="Ex.: Maria Silva")
        with c2:
            idx_t = LISTA_TURMAS.index(st.session_state["prof_turma"]) if st.session_state["prof_turma"] in LISTA_TURMAS else 0
            turma = st.selectbox("Turma*", LISTA_TURMAS, index=idx_t)
        with c3:
            idx_d = LISTA_DISCS.index(st.session_state["prof_disc"]) if st.session_state["prof_disc"] in LISTA_DISCS else 0
            disciplina = st.selectbox("Disciplina*", LISTA_DISCS, index=idx_d)

        st.divider()
        st.markdown('<p class="section-label">📝 Questão</p>', unsafe_allow_html=True)
        habilidade = st.text_input("Habilidade MS*", value=st.session_state["q_hab"], placeholder="Ex.: EF06LP01")
        enunciado = st.text_area("Enunciado*", value=st.session_state["q_enun"], height=140, placeholder="Digite o enunciado...")
        st.markdown(f'<p class="char-count">{len(enunciado)} caractere(s)</p>', unsafe_allow_html=True)

        st.markdown('<p class="section-label">🔤 Alternativas</p>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            alt_a = st.text_input("Alternativa A*", value=st.session_state["q_a"])
            alt_b = st.text_input("Alternativa B*", value=st.session_state["q_b"])
        with cb:
            alt_c = st.text_input("Alternativa C*", value=st.session_state["q_c"])
            alt_d = st.text_input("Alternativa D*", value=st.session_state["q_d"])

        gabarito = st.radio("✅ Gabarito*", ["A", "B", "C", "D"], horizontal=True)
        btn_salvar = st.form_submit_button("🚀 Cadastrar Questão")

        if btn_salvar:
            if not nome_professor or not habilidade or not enunciado:
                st.error("⚠️ Preencha os campos obrigatórios.")
            elif conn is not None:
                try:
                    df_antigo = conn.read(ttl=0)
                    nova_q = pd.DataFrame([{
                        "Professor(a)": nome_professor.strip(), "Turma": turma, "Disciplina": disciplina,
                        "Habilidade": habilidade.strip(), "Enunciado": enunciado.strip(),
                        "A": alt_a.strip(), "B": alt_b.strip(), "C": alt_c.strip(), "D": alt_d.strip(),
                        "Gabarito": gabarito, "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    }])
                    conn.update(data=pd.concat([df_antigo, nova_q], ignore_index=True))
                    # Limpeza de estado (Mantém apenas o nome do professor)
                    st.session_state.update({"prof_nome": nome_professor, "q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": ""})
                    st.success("✅ Questão cadastrada!")
                    st.rerun()
                except Exception as e: st.error(f"Erro ao gravar: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DA COORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Área da Coordenação")
    senha = st.text_input("Senha de acesso:", type="password", placeholder="Digite a senha...")

    if senha == SENHA_COORD:
        if conn is not None:
            try:
                df = conn.read(ttl=0)
                if df.empty:
                    st.info("Nenhuma questão cadastrada ainda.")
                else:
                    # Métricas (Com proteção para NaN)
                    st.divider()
                    m1, m2, m3, m4 = st.columns(4)
                    def metric_card(col, icon, value, label):
                        col.markdown(f'<div class="metric-card"><div class="metric-value">{icon} {value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
                    
                    metric_card(m1, "📋", len(df), "Questões")
                    metric_card(m2, "👨‍🏫", df["Professor(a)"].nunique(), "Professores")
                    metric_card(m3, "📚", df["Disciplina"].nunique(), "Disciplinas")
                    metric_card(m4, "🏫", df["Turma"].nunique(), "Turmas")

                    # Filtros (CORREÇÃO TYPEERROR/NAN)
                    st.divider()
                    st.markdown('<p class="section-label">🔍 Filtros</p>', unsafe_allow_html=True)
                    f1, f2, f3 = st.columns(3)
                    with f1:
                        op_t = sorted([str(x) for x in df["Turma"].dropna().unique()])
                        f_turma = st.multiselect("Turma:", op_t)
                    with f2:
                        op_d = sorted([str(x) for x in df["Disciplina"].dropna().unique()])
                        f_disc = st.multiselect("Disciplina:", op_d)
                    with f3:
                        op_p = sorted([str(x) for x in df["Professor(a)"].dropna().unique()])
                        f_prof = st.multiselect("Professor(a):", op_p)

                    df_view = df.copy()
                    if f_turma: df_view = df_view[df_view["Turma"].isin(f_turma)]
                    if f_disc: df_view = df_view[df_view["Disciplina"].isin(f_disc)]
                    if f_prof: df_view = df_view[df_view["Professor(a)"].isin(f_prof)]

                    st.dataframe(df_view, use_container_width=True, hide_index=True)

                    # Exportação (CORREÇÃO FPDF / ESPAÇO HORIZONTAL)
                    st.divider()
                    st.markdown('<p class="section-label">💾 Exportar</p>', unsafe_allow_html=True)
                    exp1, exp2 = st.columns(2)
                    with exp1:
                        csv_data = df_view.to_csv(index=False).encode("utf-8-sig")
                        st.download_button("⬇️ CSV (Excel)", data=csv_data, file_name="simulado.csv", use_container_width=True)
                    
                    with exp2:
                        if st.button("📄 Gerar e Baixar PDF", use_container_width=True):
                            garantir_fontes()
                            pdf = FPDF()
                            pdf.set_auto_page_break(auto=True, margin=15)
                            
                            if os.path.exists("DejaVuSans.ttf"):
                                pdf.add_font("SideFont", "", "DejaVuSans.ttf", uni=True)
                                pdf.add_font("SideFont", "B", "DejaVuSans-Bold.ttf", uni=True)
                                fn = "SideFont"
                            else: fn = "Helvetica"

                            pdf.add_page()
                            l_util = pdf.w - 2 * pdf.l_margin # Cálculo fixo de largura segura

                            pdf.set_font(fn, "B", 15)
                            pdf.cell(l_util, 10, "SIDE - Portal de Simulados".encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
                            pdf.set_font(fn, "", 9)
                            pdf.cell(l_util, 7, "E.E. Padre Constantino de Monte - Maracaju/MS".encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
                            pdf.ln(5)

                            gabs = []
                            for idx, (_, r) in enumerate(df_view.iterrows(), 1):
                                gabs.append(f"Q{idx}: {r.get('Gabarito')}")
                                pdf.set_fill_color(240, 240, 240)
                                pdf.set_font(fn, "B", 10)
                                header = f"Q{idx} | {r.get('Disciplina')} | {r.get('Turma')} | Hab: {r.get('Habilidade')}"
                                pdf.multi_cell(l_util, 7, header.encode('latin-1', 'replace').decode('latin-1'), fill=True)
                                
                                pdf.set_font(fn, "", 10)
                                pdf.multi_cell(l_util, 6, str(r.get("Enunciado")).encode('latin-1', 'replace').decode('latin-1'))
                                for l in ["A", "B", "C", "D"]:
                                    pdf.multi_cell(l_util, 6, f"   {l}) {str(r.get(l))}".encode('latin-1', 'replace').decode('latin-1'))
                                pdf.ln(4)

                            pdf.add_page()
                            pdf.set_font(fn, "B", 14)
                            pdf.cell(l_util, 10, "GABARITO OFICIAL", ln=True, align="C")
                            pdf.set_font(fn, "", 11)
                            pdf.ln(5)
                            for i in range(0, len(gabs), 2):
                                pdf.cell(80, 8, gabs[i])
                                if i+1 < len(gabs): pdf.cell(80, 8, gabs[i+1])
                                pdf.ln()

                            st.download_button("⬇️ Baixar PDF", data=bytes(pdf.output()), file_name="simulado.pdf", use_container_width=True)
            except Exception as e: st.error(f"Erro ao processar dados: {e}")
    elif senha: st.error("❌ Senha incorreta.")
