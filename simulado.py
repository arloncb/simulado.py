def gerar_word(df, titulo_doc):
    doc = Document()
    
    txt_tit = f'Simulado - {titulo_doc}'
    dt_hoje = datetime.now().strftime("%d/%m/%Y")
    txt_cab = f'Escola Pe. Constantino de Monte - Gerado: {dt_hoje}'
    
    doc.add_heading(txt_tit, 0)
    doc.add_paragraph(txt_cab)

    for i, row in df.iterrows():
        disc = str(row.get('disciplina', row.get('Disciplina', '-'))).upper()
        txt_q = f'Questão {i+1} - {disc}'
        doc.add_heading(txt_q, level=2)
        
        hab = str(row.get('habilidade', row.get('Habilidade', 'Não informada')))
        doc.add_paragraph(f'Habilidade: {hab}')
        
        doc.add_paragraph("")
        
        enunc = row.get('enunciado', row.get('Enunciado', row.get('pergunta', 'Sem texto')))
        doc.add_paragraph(str(enunc))
        
        # Busca a URL da imagem testando todos os nomes de coluna possíveis
        url_foto = ""
        for col_name in ['foto', 'Foto', 'imagem', 'Imagem', 'url_imagem', 'image']:
            val = str(row.get(col_name, '')).strip()
            if val.startswith('http'):
                url_foto = val
                break

        if url_foto:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                req_img = requests.get(url_foto, timeout=10, headers=headers)
                if req_img.status_code == 200 and len(req_img.content) > 0:
                    img_io = BytesIO(req_img.content)
                    doc.add_picture(img_io, width=Inches(3.5))
                else:
                    doc.add_paragraph(f"[Imagem não carregada - status {req_img.status_code}]")
            except Exception as e:
                doc.add_paragraph(f"[Erro ao carregar imagem: {e}]")
        
        doc.add_paragraph(f"A) {row.get('a', row.get('A', ''))}")
        doc.add_paragraph(f"B) {row.get('b', row.get('B', ''))}")
        doc.add_paragraph(f"C) {row.get('c', row.get('C', ''))}")
        doc.add_paragraph(f"D) {row.get('d', row.get('D', ''))}")
        doc.add_paragraph(f"E) {row.get('e', row.get('E', ''))}")
        
        doc.add_paragraph("-" * 40)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
