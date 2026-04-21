import streamlit as st
import pandas as pd

# Link da sua planilha (ajustado para exportação CSV)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1gPhMASo7yOsn5HhvLw6_rGkYbSkcBB_xUsgN8QgzhWw/export?format=csv"

def carregar_dados():
    try:
        # Lê a planilha diretamente sem precisar de chaves ou JSON
        df = pd.read_csv(URL_PLANILHA)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

st.title("📚 Sistema de Simulados")

df = carregar_dados()

if df is not None:
    st.write("Dados carregados com sucesso!")
    st.dataframe(df) # Exibe os dados para testar
