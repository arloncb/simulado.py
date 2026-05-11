import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from docx import Document
from docx.shared import Inches
from io import BytesIO
from datetime import datetime
import os
import requests
import time

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SIDE — Portal de Simulados",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── TRATAMENTO DE TEXTO (EVITAR CARACTERES ESPECIAIS) ──────────────────────
def limpar_texto(texto):
    if pd.isna(texto) or texto is None:
        return ""
    t = str(texto).strip()
    substituicoes = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...',
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2026': '...'
    }
    for original, novo in substituicoes.items():
        t = t.replace(original, novo)
    return t

# ─── FUNÇÃO PARA GERAR DOCX (NOVO PADRÃO SIDE) ──────────────────────────────
def gerar_docx_questoes(df_export):
    doc = Document()
    
    for idx, (_, r) in enumerate(df_export.iterrows(), 1):
        # 1. Disciplina
        doc.add_paragraph(f"Disciplina: {r.get('Disciplina')}")
        
        # 2. Habilidade
        doc.add_paragraph(f"Habilidade: {r.get('Habilidade')}")
        
        # 3. Número da questão (Dinâmico)
        p_num = doc.add_paragraph()
        p_num.add_run(f"QUESTÃO {idx:02d}").bold = True
        
        # 4. Enunciado da questão
        doc.add_paragraph(limpar_texto(r.get("Pergunta")))
        
        # 5. Imagem (se houver)
        link_img = r.get("Link Imagem")
        if pd.notna(link_img) and str(link_img).strip().lower() not in ["", "nan"]:
            try:
                resp = requests.get(link_img, timeout=10)
                if resp.status_code == 200:
                    img_io = BytesIO(resp.content)
                    doc.add_picture(img_io, width=Inches(4.0))
            except:
                pass 
        
        # 6. Alternativas uma sobre a outra
        for letra in ["A", "B", "C", "D", "E"]:
            conteudo = r.get(letra)
            if pd.notna(conteudo):
                doc.add_paragraph(f"({letra}) {limpar_texto(conteudo)}")
        
        # Linha separadora entre questões
        doc.add_paragraph("-" * 30)
        doc.add_paragraph("\n")
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ─── CONSTANTES E CONEXÃO ─────────────────────────────────────────────────────
LISTA_TURMAS = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
LISTA_DISCS = ["Arte", "Ciências", "Educação Física", "Geografia", "História", "Língua Inglesa", "Língua Portuguesa", "Leitura e Produção de texto", "Matemática"]
SENHA_COORD = "coord2026"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def carregar_dados():
    try:
        return conn.read(ttl=0)
    except:
        return None

# ─── INTERFACE VISUAL ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .header-box {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%);
        border-radius: 12px; padding: 25px; color: white; margin-bottom: 20px;
    }
</style>
<div class="header-box">
    <h1>📚 Portal de Simulados</h1>
    <p>Escola Estadual Padre Constantino de Monte — Maracaju/MS</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📚 SIDE")
    perfil = st.radio("Selecione o Acesso:", ["👨‍🏫 Professor(a)", "🔑 Coordenação"])
    st.divider()
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL PROFESSOR
# ═══════════════════════════════════════════════════════════════════════════════
if perfil == "👨‍🏫 Professor(a)":
    st.subheader("Lançamento de Questões")
    with st.form("form_prof", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: nome_p = st.text_input("Nome do(a) Professor(a)*")
        with c2: turma_p = st.selectbox("Turma*", LISTA_TURMAS)
        with c3: disc_p = st.selectbox("Disciplina*", sorted(LISTA_DISCS))
        
        st.divider()
        hab_p = st.text_input("Habilidade MS*")
        enun_p = st.text_area("Pergunta*", height=150)
        link_p = st.text_input("🔗 Link da Imagem (opcional)")
        
        ca, cb = st.columns(2)
        with ca:
            a, b, c = st.text_input("Alt A*"), st.text_input("Alt B*"), st.text_input("Alt C*")
        with cb:
            d, e = st.text_input("Alt D*"), st.text_input("Alt E*")
        
        gab_p = st.radio("✅ Alternativa Correta*", ["A", "B", "C", "D", "E"], horizontal=True)
        btn_enviar = st.form_submit_button("🚀 Enviar Questão")

        if btn_enviar:
            if not all([nome_p, hab_p, enun_p, a, b, c, d, e]):
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
            else:
                with st.spinner("🚀 Salvando no banco de dados..."):
                    time.sleep(1.2)
                    df_atual = carregar_dados()
                    nova_q = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Professor (a)": nome_p, "Disciplina": disc_p, "Turma": turma_p,
                        "Habilidade": hab_p, "Pergunta": enun_p, "A": a, "B": b, "C": c, "D": d, "E": e,
                        "Correta": gab_p, "Link Imagem": link_p
                    }])
                    conn.update(data=pd.concat([df_atual, nova_q], ignore_index=True))
                    st.balloons()
                    st.toast("Sucesso!", icon='✅')
                    st.success("✨ Questão registrada com sucesso!")

    if enun_p:
        st.divider()
        temp_df = pd.DataFrame([{
            "Disciplina": disc_p, "Habilidade": hab_p, "Pergunta": enun_p, 
            "A": a, "B": b, "C": c, "D": d, "E": e, "Link Imagem": link_p
        }])
        doc_prof = gerar_docx_questoes(temp_df)
        st.download_button("⬇️ Baixar esta Questão em Word", doc_prof, "Minha_Questao.docx", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL COORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("Portal da Coordenação")
    senha = st.text_input("Chave de Acesso:", type="password")
    
    if senha == SENHA_COORD:
        df = carregar_dados()
        if df is not None and not df.empty:
            st.markdown("### 🔍 Filtros Seletores")
            f1, f2, f3 = st.columns(3)
            with f1: t_f = st.multiselect("Filtrar Turmas:", sorted(df["Turma"].unique()))
            with f2: d_f = st.multiselect("Filtrar Disciplinas:", sorted(df["Disciplina"].unique()))
            with f3: p_f = st.multiselect("Filtrar Professor(a):", sorted(df["Professor (a)"].unique()))
            
            df_v = df.copy()
            if t_f: df_v = df_v[df_v["Turma"].isin(t_f)]
            if d_f: df_v = df_v[df_v["Disciplina"].isin(d_f)]
            if p_f: df_v = df_v[df_v["Professor (a)"].isin(p_f)]
            
            st.metric("Questões Selecionadas", len(df_v))
            st.dataframe(df_v, use_container_width=True, hide_index=True)
            
            st.divider()
            
            if not df_v.empty:
                with st.spinner("Preparando arquivo Word..."):
                    doc_banco = gerar_docx_questoes(df_v)
                    st.download_button(
                        label="⬇️ Baixar Banco Selecionado em Word (Docx)", 
                        data=doc_banco, 
                        file_name=f"Banco_SIDE_{datetime.now().strftime('%d_%m')}.docx", 
                        use_container_width=True
                    )
            else:
                st.warning("Nenhuma questão encontrada com os filtros selecionados.")
