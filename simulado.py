import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS CUSTOMIZADO (MANTIDO CONFORME ORIGINAL) ──────────────────────────────
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
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 8px;
    }
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
    div[data-testid="stRadio"] > label { font-weight: 600; }
    section[data-testid="stSidebar"] { background: #f3f4f6; }
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
    .char-count { font-size: 0.78rem; color: #9ca3af; margin-top: -10px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES ───────────────────────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Língua Portuguesa", "Matemática", "Arte", "Língua Inglesa", "Ciências", "História", "Geografia", "Ensino Religioso", "Educação Física", "Leitura e Produção de texto"]
SENHA_COORD = "coord2026"

# ─── ESTADO INICIAL ───────────────────────────────────────────────────────────
_defaults = {"prof_nome": "", "prof_turma": "6° A", "prof_disc": "Língua Portuguesa", "q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": ""}
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
    perfil = st.radio("Perfil de acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"], label_visibility="collapsed")
    st.divider()
    st.caption(f"📍 Maracaju/MS")
    st.caption(f"🗓️ {datetime.now().strftime('%d/%m/%Y')}")

st.markdown('<div class="page-header"><h1>📚 Portal de Simulados</h1><p>Escola Estadual Padre Constantino de Monte — SIDE Maracaju/MS</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DO PROFESSOR (MANTIDA)
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
        enunciado = st.text_area("Enunciado*", value=st.session_state["q_enun"], height=140, placeholder="Digite o enunciado completo da questão…")
        st.markdown(f'<p class="char-count">{len(enunciado)} caractere(s)</p>', unsafe_allow_html=True)

        st.divider()
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

        if btn_salvar:
            erros = []
            if not nome_professor.strip(): erros.append("**Nome do(a) Professor(a)** vazio.")
            if not habilidade.strip(): erros.append("**Habilidade MS** vazia.")
            if not enunciado.strip(): erros.append("**Enunciado** vazio.")
            for l, v in [("A", alt_a), ("B", alt_b), ("C", alt_c), ("D", alt_d)]:
                if not v.strip(): erros.append(f"**Alternativa {l}** vazia.")

            st.session_state.update({"prof_nome": nome_professor, "prof_turma": turma, "prof_disc": disciplina, "q_hab": habilidade, "q_enun": enunciado, "q_a": alt_a, "q_b": alt_b, "q_c": alt_c, "q_d": alt_d})

            if erros:
                st.error("⚠️ Corrija os erros:")
                for err in erros: st.markdown(f"- {err}")
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
                    st.session_state.update({"q_hab": "", "q_enun": "", "q_a": "", "q_b": "", "q_c": "", "q_d": ""})
                    st.success("✅ Questão cadastrada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao gravar: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA DA COORDENAÇÃO (MELHORADA)
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Área da Coordenação")
    senha = st.text_input("Senha de acesso:", type="password")

    if senha and senha != SENHA_COORD:
        st.error("❌ Senha incorreta.")
    elif senha == SENHA_COORD:
        st.success("✅ Acesso autorizado.")
        
        # Proteção contra falha de conexão
        if conn is None:
            st.warning("Conexão indisponível.")
            st.stop()
            
        try:
            df = conn.read(ttl=0)
        except:
            st.error("Erro ao ler dados da planilha.")
            st.stop()

        if df.empty:
            st.info("Nenhuma questão cadastrada.")
            st.stop()

        # Métricas (Design original)
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        def metric_card(col, icon, value, label):
            col.markdown(f'<div class="metric-card"><div class="metric-value">{icon} {value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

        metric_card(m1, "📋", len(df), "Questões")
        metric_card(m2, "👨‍🏫", df["Professor(a)"].nunique(), "Professores")
        metric_card(m3, "📚", df["Disciplina"].nunique(), "Disciplinas")
        metric_card(m4, "🏫", df["Turma"].nunique(), "Turmas")
        
        # Filtros
        st.divider()
        st.markdown('<p class="section-label">🔍 Filtros</p>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: filtro_turma = st.multiselect("Turma:", sorted(df["Turma"].unique()))
        with f2: filtro_disc = st.multiselect("Disciplina:", sorted(df["Disciplina"].unique()))
        with f3: filtro_prof = st.multiselect("Professor(a):", sorted(df["Professor(a)"].unique()))

        df_view = df.copy()
        if filtro_turma: df_view = df_view[df_view["Turma"].isin(filtro_turma)]
        if filtro_disc: df_view = df_view[df_view["Disciplina"].isin(filtro_disc)]
        if filtro_prof: df_view = df_view[df_view["Professor(a)"].isin(filtro_prof)]

        st.dataframe(df_view, use_container_width=True, hide_index=True)

        # Exportação (Melhorada)
        st.divider()
        st.markdown('<p class="section-label">💾 Exportar</p>', unsafe_allow_html=True)
        exp1, exp2 = st.columns(2)

        with exp1:
            # Melhoria: encoding utf-8-sig para abrir direto no Excel sem erro de acento
            csv_bytes = df_view.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ Baixar como CSV", data=csv_bytes, file_name=f"simulado_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

        with exp2:
            if st.button("📄 Gerar e Baixar PDF", use_container_width=True):
                # Melhoria: Caminhos relativos (as fontes devem estar na pasta do script)
                FONT_REG  = "DejaVuSans.ttf"
                FONT_BOLD = "DejaVuSans-Bold.ttf"
                
                # Verificação simples de existência da fonte para evitar crash
                if not os.path.exists(FONT_REG):
                    st.error("Arquivo de fonte 'DejaVuSans.ttf' não encontrado na pasta raiz.")
                    st.stop()

                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_font("DV", "", FONT_REG, uni=True)
                pdf.add_font("DV", "B", FONT_BOLD, uni=True)
                pdf.add_page()

                # Cabeçalho PDF
                pdf.set_font("DV", "B", 15)
                pdf.cell(0, 10, "Portal de Simulados - SIDE", ln=True, align="C")
                pdf.set_font("DV", "", 9)
                pdf.cell(0, 7, "E.E. Padre Constantino de Monte - Maracaju/MS", ln=True, align="C")
                pdf.ln(5)

                lista_gabarito = []

                for idx, (_, row) in enumerate(df_view.iterrows(), start=1):
                    # Guardamos o gabarito para o final
                    lista_gabarito.append(f"Q{idx}: {row.get('Gabarito')}")
                    
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font("DV", "B", 10)
                    header = f"Q{idx} | {row.get('Disciplina')} | {row.get('Turma')} | Hab: {row.get('Habilidade')}"
                    pdf.multi_cell(0, 7, header, fill=True)
                    
                    pdf.set_font("DV", "", 10)
                    pdf.multi_cell(0, 6, str(row.get("Enunciado")))
                    pdf.ln(1)
                    
                    for letra in ["A", "B", "C", "D"]:
                        pdf.multi_cell(0, 6, f"   {letra}) {row.get(letra)}")
                    pdf.ln(4)

                # Melhoria: Folha de Respostas em nova página
                pdf.add_page()
                pdf.set_font("DV", "B", 14)
                pdf.cell(0, 10, "GABARITO OFICIAL", ln=True, align="C")
                pdf.set_font("DV", "", 11)
                pdf.ln(5)
                
                # Organiza o gabarito em 2 colunas para economizar papel
                for i in range(0, len(lista_gabarito), 2):
                    txt_col1 = lista_gabarito[i]
                    txt_col2 = lista_gabarito[i+1] if (i+1) < len(lista_gabarito) else ""
                    pdf.cell(90, 8, txt_col1, border=0)
                    pdf.cell(90, 8, txt_col2, border=0, ln=True)

                pdf_bytes = bytes(pdf.output())
                st.download_button("⬇️ Clique para baixar o PDF", data=pdf_bytes, file_name=f"simulado_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
