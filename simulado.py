def gerar_word(df, titulo_doc):
    doc = Document()
    doc.add_heading(f'Simulado - {titulo_doc}', 0)
    doc.add_paragraph(f'Escola Padre Constantino de Monte - Data: {datetime.now().strftime("%d/%m/%Y")}')
    doc.add_paragraph("_" * 50)

    # Normaliza os nomes das colunas para evitar erro de maiúsculas/minúsculas
    df.columns = [str(col).strip().capitalize() for col in df.columns]

    for i, row in df.iterrows():
        try:
            # Tenta pegar os dados. Se a coluna não existir, ele usa um texto padrão.
            pergunta = row.get('Enunciado', 'Questão sem enunciado')
            disc = row.get('Disciplina', '-')
            turma = row.get('Turma', '-')
            
            doc.add_paragraph(f'\nQuestão {i+1} ({disc} - {turma})', style='Heading 2')
            doc.add_paragraph(str(pergunta))
            
            # Alternativas
            doc.add_paragraph(f"A) {row.get('A', '')}")
            doc.add_paragraph(f"B) {row.get('B', '')}")
            doc.add_paragraph(f"C) {row.get('C', '')}")
            doc.add_paragraph(f"D) {row.get('D', '')}")
            doc.add_paragraph(f"E) {row.get('E', '')}")
            doc.add_paragraph(f"Gabarito: {row.get('Gabarito', 'N/A')}")
            doc.add_paragraph("-" * 30)
        except Exception as e:
            continue # Pula se houver erro em uma linha específica

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
