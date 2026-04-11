st.markdown("""
    <style>
    /* Estilo geral da página */
    .stApp {
        background-color: #f8f9fa; /* Um cinza bem clarinho para destacar o colorido */
    }
    
    /* Estilizando os containers (caixas) com sombra */
    .stForm, div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Sombra suave */
        margin-bottom: 20px;
    }

    /* Aumentando as letras dos títulos e rótulos */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    label p {
        font-size: 20px !important; /* Letras maiores para o professor ler bem */
        font-weight: bold;
        color: #4a4a4a;
    }

    /* Botão colorido e com sombra */
    .stButton>button {
        background-color: #4CAF50; /* Verde claro */
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 25px;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px); /* Efeito de subir ao passar o mouse */
    }
    </style>
    """, unsafe_allow_html=True)
