from fpdf import FPDF
import io

def gerar_pdf(df_filtrado):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título do Documento
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Simulado - Escola Padre Constantino", ln=True, align="C")
    pdf.ln(10)

    for i, row in df_filtrado.iterrows():
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Questão {i+1} - {row['Disciplina']} ({row['Turma']})")
        
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(0, 8, f"Habilidade: {row['Habilidade']}")
        pdf.ln(2)

        # Enunciado
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, row['Pergunta'])
        pdf.ln(5)

        # Imagem (Tenta baixar e inserir no PDF)
        if row['Link Imagem'] and str(row['Link Imagem']).startswith("http"):
            try:
                # O PDF precisa da imagem em um formato que ele entenda
                img_data = requests.get(row['Link Imagem']).content
                img_io = io.BytesIO(img_data)
                pdf.image(img_io, x=10, w=100) # Ajusta o tamanho da imagem
                pdf.ln(5)
            except:
                pdf.set_font("Arial", "I", 8)
                pdf.cell(0, 5, "[Erro ao carregar imagem desta questão]", ln=True)

        # Alternativas
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, f"a) {row['A']}")
        pdf.multi_cell(0, 7, f"b) {row['B']}")
        pdf.multi_cell(0, 7, f"c) {row['C']}")
        pdf.multi_cell(0, 7, f"d) {row['D']}")
        pdf.multi_cell(0, 7, f"e) {row['E']}")
        pdf.ln(10)
        
        # Linha separadora
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    return pdf.output()

# --- NO SEU CÓDIGO, ONDE TEM O BOTÃO DE DOWNLOAD CSV, ADICIONE: ---
# pdf_bytes = gerar_pdf(df_filtrado)
# st.download_button(label="📥 Baixar Simulado em PDF", data=pdf_bytes, file_name="simulado_completo.pdf", mime="application/pdf")
