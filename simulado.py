# Dentro da área de acesso restrito, após carregar os dados da planilha:

df = conn.read(worksheet="Página1", ttl=0).fillna("")

if not df.empty:
    c1, c2 = st.columns(2)
    
    # O multiselect preserva a ordem em que os itens são selecionados
    f_d = c1.multiselect("Filtrar Disciplina:", df["Disciplina"].unique())
    f_t = c2.multiselect("Filtrar Turma:", df["Turma"].unique())
    
    dff = df.copy()
    if f_d: dff = dff[dff["Disciplina"].isin(f_d)]
    if f_t: dff = dff[dff["Turma"].isin(f_t)]

    # --- LÓGICA DE ORDENAÇÃO POR SELEÇÃO ---
    # Se houver turmas selecionadas, define a ordem pela sequência do clique
    if f_t:
        dff['Turma'] = pd.Categorical(dff['Turma'], categories=f_t, ordered=True)
    
    # Se houver disciplinas selecionadas, define a ordem pela sequência do clique
    if f_d:
        dff['Disciplina'] = pd.Categorical(dff['Disciplina'], categories=f_d, ordered=True)

    # Ordena o DataFrame respeitando as categorias definidas acima
    # Se não houver filtros, ele seguirá a ordem alfabética padrão
    dff = dff.sort_values(by=['Turma', 'Disciplina'])
    
    st.dataframe(dff, use_container_width=True)
    
    # Agora, ao clicar nos botões de download, o PDF e o Word já sairão 
    # organizados exatamente na ordem que aparece na tabela acima.
