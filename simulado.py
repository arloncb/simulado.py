import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import base64
from datetime import datetime
import pandas as pd
from docx import Document # Biblioteca para Word
from io import BytesIO

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Portal Simulado - Escola Constantino", layout="centered")

# --- 1. VISUAL PREMIUM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9 !important; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Segoe UI', sans-serif; }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #ffffff !important;
        padding: 25px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
        margin-bottom: 15px !important;
        border: 1px solid #e2e8f0 !important;
    }
    label p, .stMarkdown p, p { color: #1e293b !important; font-size: 19px !important; font-weight: 600 !important; }
    input, textarea, div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #cbd5e1 !important; border-radius: 8px !important; }
    .stButton>button { width: 100%; background-color: #059669 !important; color: white !important; font-weight: bold !important; font-size: 20px !important; height: 3.5em !important; border-radius: 10px !important; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO ---

def conectar_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info_gs = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(info_gs, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(info_gs["spreadsheet"]).get_worksheet(0)

def upload_github(arquivo, nome_arquivo):
    token = st.secrets["github_token"]
    repo = "SEU_USUARIO/SEU_REPOSITORIO" # ⚠️ AJUSTE AQUI
    url = f"https://api.github.com/repos/{repo}/contents/imagens/{nome_arquivo}"
    conteudo = base64.b64encode(arquivo.read()).decode()
    payload = {"message": f"Questão: {nome_arquivo}", "content": conteudo}
    headers = {"Authorization": f"token {token}"}
    res = requests.put(url, json=payload, headers=headers)
    return res.json()['content']['download_url'] if res.status_code in [200, 201] else ""

# --- 3. FUNÇÃO PARA GERAR O WORD ---

def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    doc.add_paragraph(f'Escola Padre Constantino de Monte - Data: {datetime.now().strftime("%d/%m/%Y")}')
    doc.add_paragraph("_" * 50)

    for i, row in df.iterrows():
        doc.add_paragraph(f'\nQuestão {i+1} ({row["Disciplina"]} - {row["Turma"]})', style='Heading 2')
        doc.add_paragraph(str(row['Enunciado']))
        
        # Lista as alternativas
        doc.add_paragraph(f"A) {row['A']}")
        doc.add_paragraph(f"B) {row['B']}")
        doc.add_paragraph(f"C) {row['C']}")
        doc.add_paragraph(f"D) {row['D']}")
        doc.add_paragraph(f"E) {row['E']}")
        doc.add_paragraph(f"Gabarito: {row['Gabarito']}")
        doc.add_paragraph("-" * 30)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. BARRA LATERAL (COORDENAÇÃO) ---
st.sidebar.title("🔐 Área Restrita")
senha = st.sidebar.text_input("Senha da Coordenação", type="password")
acesso_coord = (senha == "constantino2026")

if acesso_coord:
    st.sidebar.success("Acesso Liberado!")
    menu = st.sidebar.radio("Navegação", ["Lançar Questões", "Ver Banco de Questões"])
else:
    menu = "Lançar Questões"

# --- 5. INTERFACE: LANÇAR QUESTÕES ---
if menu == "Lançar Questões":
    st.title("📝 Portal de Simulados")
    with st.container():
        prof = st.text_input("👤 Nome do Professor")
        disciplina = st.selectbox("📚 Disciplina", ["Português", "Matemática", "História", "Geografia", "Ciências", "Inglês", "Artes", "Ed. Física"])
        turmas_selecionadas = st.multiselect("🏫 Para quais turmas?", ["6º A", "6º B", "7º A", "7º B", "8º A", "8º B", "9º A", "9º B"])

    with st.container():
        enunciado = st.text_area("✍️ Enunciado da Questão")
        foto = st.file_uploader("🖼️ Imagem (Máx 10MB)", type=["jpg", "jpeg", "png"])
        if foto and foto.size > 10 * 1024 * 1024:
            st.error("🚨 Imagem muito grande!")
            foto = None

    with st.container():
        st.write("🎯 **Alternativas**")
        c1, c2 = st.columns(2)
        with c1: a, b, c = st.text_input("A)"), st.text_input("B)"), st.text_input("C)")
        with c2: d, e = st.text_input("D)"), st.text_input("E)")
        gabarito = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"])

    if st.button("🚀 FINALIZAR E LANÇAR"):
        if not prof or not turmas_selecionadas or not enunciado:
            st.warning("⚠️ Preencha os campos obrigatórios!")
        else:
            with st.spinner("Gravando..."):
                try:
                    url_img = upload_github(foto, f"{datetime.now().timestamp()}.jpg") if foto else ""
                    sheet = conectar_google_sheets()
                    for t in turmas_selecionadas:
                        linha = [datetime.now().strftime("%d/%m/%Y %H:%M"), prof, disciplina, t, enunciado, url_img, a, b, c, d, e, gabarito]
                        sheet.append_row(linha)
                    st.success("✅ Questão enviada!")
                    st.balloons()
                except Exception as err: st.error(f"❌ Erro: {err}")

# --- 6. INTERFACE: ÁREA DA COORDENAÇÃO (FILTROS E EXPORTAÇÃO) ---
elif menu == "Ver Banco de Questões":
    st.title("📊 Gestão de Questões")
    
    try:
        sheet = conectar_google_sheets()
        df = pd.DataFrame(sheet.get_all_records())
        
        if not df.empty:
            # --- FILTROS ---
            with st.container():
                st.write("🔍 **Filtrar Simulado**")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    filtro_turma = st.multiselect("Filtrar por Turma", options=df['Turma'].unique())
                with col_f2:
                    filtro_disc = st.multiselect("Filtrar por Disciplina", options=df['Disciplina'].unique())
            
            # Aplicando filtros
            df_filtrado = df.copy()
            if filtro_turma: df_filtrado = df_filtrado[df_filtrado['Turma'].isin(filtro_turma)]
            if filtro_disc: df_filtrado = df_filtrado[df_filtrado['Disciplina'].isin(filtro_disc)]
            
            st.write(f"Total de questões encontradas: **{len(df_filtrado)}**")
            st.dataframe(df_filtrado, use_container_width=True)
            
            # --- BOTÕES DE DOWNLOAD ---
            c_down1, c_down2 = st.columns(2)
            with c_down1:
                # Gerar Word
                if st.button("📄 Gerar Arquivo Word"):
                    doc_word = gerar_word(df_filtrado, "Geral" if not filtro_turma else ", ".join(filtro_turma))
                    st.download_button(
                        label="⬇️ Baixar Simulado (.docx)",
                        data=doc_word,
                        file_name=f"simulado_{datetime.now().strftime('%d_%m')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            with c_down2:
                csv = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar Planilha (CSV)", csv, "banco_questoes.csv", "text/csv")
        else:
            st.info("Banco de dados vazio.")
    except Exception as e: st.error(f"Erro: {e}")
