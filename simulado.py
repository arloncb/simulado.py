import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS CUSTOMIZADO ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Tipografia e cores base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header da página */
    .page-header {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: white;
    }
    .page-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
    .page-header p  { margin: 4px 0 0; opacity: 0.8; font-size: 0.95rem; }

    /* Seção do formulário */
    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 8px;
    }

    /* Cards de métricas customizados */
    .metric-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a3a2a;
        line-height: 1;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 4px;
    }

    /* Alinhamento do botão de submit */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1a3a2a, #2d6a4f);
        color: white;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.65rem 1.5rem;
        border-radius: 8px;
        width: 100%;
        transition: opacity 0.2s;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { opacity: 0.88; }

    /* Gabarito radio horizontal */
    div[data-testid="stRadio"] > label { font-weight: 600; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: #f3f4f6; }
    section[data-testid="stSidebar"] hr { border-color: #d1d5db; }

    /* Linha divisória suave */
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }

    /* Tag de contagem de caracteres */
    .char-count { font-size: 0.78rem; color: #9ca3af; margin-top: -10px; margin-bottom: 8px; }
    .char-ok    { color: #16a34a; }
    .char-warn  { color: #d97706; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES ───────────────────────────────────────────────────────────────
LISTA_TURMAS = [
    "4° A", "5° A",
    "6° A", "6° B", "6° C",
    "7° A",
    "8° A",
    "9° A", "9° B", "9° C", "9° D",
    "1° A", "1° B",
    "2° A",
    "3° A",
]
LISTA_DISCS = [
    "Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa",
    "Ciências", "História", "Geografia", "Ensino Religioso",
    "Educação Física", "Leitura e Produção de texto",
]
SENHA_COORD = "coord2026"

# ─── ESTADO INICIAL ───────────────────────────────────────────────────────────
_defaults = {
    "prof_nome": "", "prof_turma": "6° A", "prof_disc": "Língua Portuguesa",
    "q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": "",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── CONEXÃO GOOGLE SHEETS ────────────────────────────────────────────────────
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
    perfil = st.radio(
        "Perfil de acesso:",
        ["👨‍🏫 Professor(a)", "🔑 Coordenação"],
        label_visibility="collapsed",
    )
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

        # — Identificação ——————————————————————————————————————————————————————
        st.markdown('<p class="section-label">👤 Identificação</p>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            nome_professor = st.text_input(
                "Nome do(a) Professor(a)*",
                value=st.session_state["prof_nome"],
                placeholder="Ex.: Maria Silva",
            )
        with c2:
            idx_t = LISTA_TURMAS.index(st.session_state["prof_turma"]) \
                    if st.session_state["prof_turma"] in LISTA_TURMAS else 0
            turma = st.selectbox("Turma*", LISTA_TURMAS, index=idx_t)
        with c3:
            idx_d = LISTA_DISCS.index(st.session_state["prof_disc"]) \
                    if st.session_state["prof_disc"] in LISTA_DISCS else 0
            disciplina = st.selectbox("Disciplina*", LISTA_DISCS, index=idx_d)

        st.divider()

        # — Questão ————————————————————————————————————————————————————————————
        st.markdown('<p class="section-label">📝 Questão</p>', unsafe_allow_html=True)

        habilidade = st.text_input(
            "Habilidade MS*",
            value=st.session_state["q_hab"],
            placeholder="Ex.: EF06LP01",
        )

        enunciado = st.text_area(
            "Enunciado*",
            value=st.session_state["q_enun"],
            height=140,
            placeholder="Digite o enunciado completo da questão…",
        )

        # Contador de caracteres — apenas informativo
        n_chars = len(st.session_state["q_enun"])
        st.markdown(
            f'<p class="char-count">{n_chars} caractere(s)</p>',
            unsafe_allow_html=True,
        )

        st.divider()

        # — Alternativas ———————————————————————————————————————————————————————
        st.markdown('<p class="section-label">🔤 Alternativas</p>', unsafe_allow_html=True)

        ca, cb = st.columns(2)
        with ca:
            alt_a = st.text_input("Alternativa A*", value=st.session_state["q_a"])
            alt_b = st.text_input("Alternativa B*", value=st.session_state["q_b"])
        with cb:
            alt_c = st.text_input("Alternativa C*", value=st.session_state["q_c"])
            alt_d = st.text_input("Alternativa D*", value=st.session_state["q_d"])

        gabarito = st.radio("✅ Gabarito*", ["A", "B", "C", "D"], horizontal=True)

        btn_salvar = st.form_submit_button("🚀 Cadastrar Questão", use_container_width=True)

        # ── Lógica de submit ──────────────────────────────────────────────────
        if btn_salvar:
            # Validações individuais (mensagens específicas por campo)
            erros = []
            if not nome_professor.strip():
                erros.append("**Nome do(a) Professor(a)** não pode estar vazio.")
            if not habilidade.strip():
                erros.append("**Habilidade MS** não pode estar vazia.")
            if not enunciado.strip():
                erros.append("**Enunciado** não pode estar vazio.")
            for letra, valor in [("A", alt_a), ("B", alt_b), ("C", alt_c), ("D", alt_d)]:
                if not valor.strip():
                    erros.append(f"**Alternativa {letra}** não pode estar vazia.")

            # Sempre preserva o estado atual para não perder o que foi digitado
            st.session_state.update({
                "prof_nome": nome_professor,
                "prof_turma": turma,
                "prof_disc": disciplina,
                "q_hab": habilidade,
                "q_enun": enunciado,
                "q_a": alt_a, "q_b": alt_b, "q_c": alt_c, "q_d": alt_d,
            })

            if erros:
                st.error("⚠️ Corrija os erros abaixo antes de salvar:")
                for err in erros:
                    st.markdown(f"- {err}")

            elif conn is not None:
                try:
                    df_antigo = conn.read(ttl=0)
                    nova_q = pd.DataFrame([{
                        "Professor(a)": nome_professor.strip(),
                        "Turma": turma,
                        "Disciplina": disciplina,
                        "Habilidade": habilidade.strip(),
                        "Enunciado": enunciado.strip(),
                        "A": alt_a.strip(),
                        "B": alt_b.strip(),
                        "C": alt_c.strip(),
                        "D": alt_d.strip(),
                        "Gabarito": gabarito,
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    }])
                    conn.update(data=pd.concat([df_antigo, nova_q], ignore_index=True))

                    # Mantém identificação, zera somente os campos da questão
                    st.session_state.update({
                        "q_hab": "", "q_enun": "",
                        "q_a": "", "q_b": "", "q_c": "", "q_d": "",
                    })
                    st.success("✅ Questão cadastrada! Os campos foram limpos para a próxima.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro ao gravar na planilha: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DA COORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Área da Coordenação")

    senha = st.text_input(
        "Senha de acesso:",
        type="password",
        placeholder="Digite a senha…",
    )

    if senha and senha != SENHA_COORD:
        st.error("❌ Senha incorreta.")

    elif senha == SENHA_COORD:
        st.success("✅ Acesso autorizado.")

        if conn is None:
            st.stop()

        df = conn.read(ttl=0)

        if df.empty:
            st.info("Nenhuma questão cadastrada ainda.")
            st.stop()

        # ── Métricas ─────────────────────────────────────────────────────────
        st.divider()
        m1, m2, m3, m4 = st.columns(4)

        def metric_card(col, icon, value, label):
            col.markdown(
                f"""<div class="metric-card">
                        <div class="metric-value">{icon} {value}</div>
                        <div class="metric-label">{label}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

        metric_card(m1, "📋", len(df), "Questões")
        metric_card(m2, "👨‍🏫", df["Professor(a)"].nunique() if "Professor(a)" in df.columns else "—", "Professores")
        metric_card(m3, "📚", df["Disciplina"].nunique() if "Disciplina" in df.columns else "—", "Disciplinas")
        metric_card(m4, "🏫", df["Turma"].nunique() if "Turma" in df.columns else "—", "Turmas")
        st.divider()

        # ── Filtros ───────────────────────────────────────────────────────────
        st.markdown('<p class="section-label">🔍 Filtros</p>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)

        with f1:
            opts_turma = sorted(df["Turma"].dropna().unique()) if "Turma" in df.columns else []
            filtro_turma = st.multiselect("Turma:", opts_turma)

        with f2:
            opts_disc = sorted(df["Disciplina"].dropna().unique()) if "Disciplina" in df.columns else []
            filtro_disc = st.multiselect("Disciplina:", opts_disc)

        with f3:
            opts_prof = sorted(df["Professor(a)"].dropna().unique()) if "Professor(a)" in df.columns else []
            filtro_prof = st.multiselect("Professor(a):", opts_prof)

        # Aplica filtros
        df_view = df.copy()
        if filtro_turma:
            df_view = df_view[df_view["Turma"].isin(filtro_turma)]
        if filtro_disc:
            df_view = df_view[df_view["Disciplina"].isin(filtro_disc)]
        if filtro_prof:
            df_view = df_view[df_view["Professor(a)"].isin(filtro_prof)]

        st.markdown(f"**{len(df_view)} questão(ões) encontrada(s)**")
        st.dataframe(df_view, use_container_width=True, hide_index=True)

        # ── Exportação ────────────────────────────────────────────────────────
        st.divider()
        st.markdown('<p class="section-label">💾 Exportar</p>', unsafe_allow_html=True)

        exp1, exp2 = st.columns(2)

        # CSV
        with exp1:
            csv_bytes = df_view.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Baixar como CSV",
                data=csv_bytes,
                file_name=f"simulado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # PDF
        with exp2:
            if st.button("📄 Gerar e Baixar PDF", use_container_width=True):

                # Caminhos das fontes DejaVu (disponíveis no Streamlit Cloud / Ubuntu)
                FONT_DIR = "/usr/share/fonts/truetype/dejavu"
                FONT_REG  = f"{FONT_DIR}/DejaVuSans.ttf"
                FONT_BOLD = f"{FONT_DIR}/DejaVuSans-Bold.ttf"
                FONT_ITAL = f"{FONT_DIR}/DejaVuSans-Oblique.ttf"

                # Helper: garante string segura e sem None
                def txt(value):
                    return str(value) if value is not None else ""

                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Registra as fontes TTF (suporte completo a UTF-8 / português)
                pdf.add_font("DV",  "",  FONT_REG,  uni=True)
                pdf.add_font("DV",  "B", FONT_BOLD, uni=True)
                pdf.add_font("DV",  "I", FONT_ITAL, uni=True)

                pdf.add_page()

                # Cabecalho do PDF
                pdf.set_font("DV", "B", 15)
                pdf.cell(0, 10, "Portal de Simulados - SIDE", ln=True, align="C")
                pdf.set_font("DV", "", 10)
                pdf.cell(0, 7, "E.E. Padre Constantino de Monte - Maracaju/MS", ln=True, align="C")
                pdf.set_font("DV", "I", 8)
                pdf.cell(0, 6, f"Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}", ln=True, align="C")
                pdf.ln(6)

                for idx, (_, row) in enumerate(df_view.iterrows(), start=1):
                    # Cabecalho da questao
                    pdf.set_fill_color(235, 235, 235)
                    pdf.set_font("DV", "B", 10)
                    header_txt = (
                        f"Q{idx}  |  {txt(row.get('Disciplina'))}  |  "
                        f"{txt(row.get('Turma'))}  |  Hab: {txt(row.get('Habilidade'))}"
                    )
                    pdf.multi_cell(0, 7, header_txt, fill=True)

                    # Enunciado
                    pdf.set_font("DV", "", 9)
                    pdf.multi_cell(0, 6, txt(row.get("Enunciado")))
                    pdf.ln(1)

                    # Alternativas
                    for letra in ["A", "B", "C", "D"]:
                        pdf.multi_cell(0, 6, f"   {letra})  {txt(row.get(letra))}")

                    # Gabarito
                    pdf.set_font("DV", "B", 9)
                    pdf.cell(0, 7, f"   Gabarito: {txt(row.get('Gabarito'))}", ln=True)
                    pdf.ln(4)

                pdf_bytes = bytes(pdf.output())
                st.download_button(
                    label="⬇️ Clique aqui para baixar o PDF",
                    data=pdf_bytes,
                    file_name=f"simulado_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
