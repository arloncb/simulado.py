# ─── CSS GLOBAL ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset e base ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
}

/* ── Fundo geral ── */
.stApp {
    background: #f0f7f4;
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 0%, rgba(45,106,79,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(26,58,42,0.06) 0%, transparent 55%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e8f5ed 0%, #d4ede0 100%) !important;
    border-right: 1px solid rgba(45,106,79,0.20) !important;
}
section[data-testid="stSidebar"] * {
    color: #1a3a2a !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #1a3a2a !important;
}

/* ── Header animado ── */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-22px); }
    to   { opacity: 1; transform: translateY(0); }
}
.header-box {
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 60%, #52b788 100%);
    border: 1px solid rgba(255,255,255,0.20);
    border-radius: 16px;
    padding: 30px 36px;
    color: white;
    margin-bottom: 28px;
    animation: fadeSlideDown 0.6s ease both;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
}
.header-box::before {
    content: '';
    position: absolute;
    top: -40%; right: -10%;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.10) 0%, transparent 70%);
    pointer-events: none;
}
.header-box h1 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0 0 6px 0;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.header-box p {
    margin: 0;
    opacity: 0.85;
    font-size: 0.95rem;
    font-weight: 300;
    letter-spacing: 0.3px;
}

/* ── Cards de seção ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.card-section {
    background: rgba(255,255,255,0.80);
    border: 1px solid rgba(45,106,79,0.20);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 20px;
    animation: fadeUp 0.5s ease both;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

/* ── Títulos de seção ── */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2d6a4f;
    letter-spacing: 0.4px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(45,106,79,0.30), transparent);
    margin-left: 6px;
}

/* ── Inputs ── */
.stTextInput input,
.stTextArea textarea,
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid rgba(45,106,79,0.25) !important;
    border-radius: 10px !important;
    color: #1a3a2a !important;
    font-family: 'Sora', sans-serif !important;
    transition: border-color 0.25s, box-shadow 0.25s;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(45,106,79,0.50) !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.10) !important;
}
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stRadio label,
.stMultiSelect label {
    color: #2d6a4f !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px;
}

/* ── Radio Buttons ── */
.stRadio div[role="radiogroup"] {
    gap: 10px;
}
.stRadio div[role="radiogroup"] label {
    background: #ffffff;
    border: 1px solid rgba(45,106,79,0.25);
    border-radius: 8px;
    padding: 6px 14px;
    transition: all 0.2s ease;
    color: #2d6a4f !important;
}
.stRadio div[role="radiogroup"] label:hover {
    border-color: rgba(45,106,79,0.50);
    background: rgba(45,106,79,0.08);
}

/* ── Botão principal ── */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(45,106,79,0.25); }
    50%        { box-shadow: 0 0 0 8px rgba(45,106,79,0); }
}
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(45,106,79,0.30) !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.3px;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.25s ease !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::before,
.stFormSubmitButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.4s ease;
}
.stButton > button:hover::before,
.stFormSubmitButton > button:hover::before {
    left: 100%;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #40916c 0%, #52b788 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(45,106,79,0.30) !important;
    animation: pulse-glow 1.5s infinite;
}
.stButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 6px rgba(45,106,79,0.20) !important;
}

/* ── Download button destaque ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%) !important;
    border: 1px solid rgba(45,106,79,0.35) !important;
    width: 100%;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #40916c 0%, #52b788 100%) !important;
}

/* ── Métricas ── */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid rgba(45,106,79,0.20) !important;
    border-radius: 12px !important;
    padding: 16px 22px !important;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
div[data-testid="stMetric"] label {
    color: #2d6a4f !important;
    font-size: 0.82rem !important;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1a3a2a !important;
    font-size: 2.1rem !important;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(45,106,79,0.20) !important;
    background: #ffffff;
}

/* ── Divider ── */
hr {
    border-color: rgba(45,106,79,0.20) !important;
    margin: 20px 0 !important;
}

/* ── Alertas / Toasts ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
    font-family: 'Sora', sans-serif !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #40916c, #74c69d) !important;
    border-radius: 999px !important;
}
.stProgress > div > div {
    background: rgba(45,106,79,0.12) !important;
    border-radius: 999px !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] {
    color: #2d6a4f !important;
}

/* ── Multiselect tags ── */
span[data-baseweb="tag"] {
    background: rgba(45,106,79,0.15) !important;
    border-radius: 6px !important;
    color: #1a3a2a !important;
}

/* ── Cabeçalho da sidebar ── */
.sidebar-logo {
    text-align: center;
    padding: 12px 0 8px 0;
}
.sidebar-logo .logo-icon {
    font-size: 2.4rem;
    line-height: 1;
    display: block;
    margin-bottom: 6px;
    filter: drop-shadow(0 0 10px rgba(45,106,79,0.3));
}
.sidebar-logo .logo-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #2d6a4f;
    letter-spacing: 2px;
}
.sidebar-logo .logo-sub {
    font-size: 0.72rem;
    color: #40916c;
    opacity: 0.75;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Badge de data ── */
.date-badge {
    background: rgba(45,106,79,0.12);
    border: 1px solid rgba(45,106,79,0.20);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.78rem;
    color: #2d6a4f;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
    margin-top: 8px;
}

/* ── Tag de campo obrigatório ── */
.req-badge {
    display: inline-block;
    background: rgba(231,111,81,0.12);
    color: #e76f51;
    border: 1px solid rgba(231,111,81,0.25);
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 1px 6px;
    margin-left: 6px;
    letter-spacing: 0.5px;
    vertical-align: middle;
}

/* ── Animação de entrada dos campos ── */
@keyframes fadeInField {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.field-animated {
    animation: fadeInField 0.4s ease both;
}

/* ── Ajuste visual para o Quill ── */
.quill-label {
    color: #2d6a4f;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.3px;
    margin-bottom: 6px;
    display: block;
}
</style>
""", unsafe_allow_html=True)
