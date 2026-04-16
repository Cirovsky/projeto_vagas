import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from collections import Counter
from custom_flat import custom_flat
from misc_func import normaliza_lista_texto
from table_format import export_xlsx


def criar_nuvem_palavras(palavras_chave, frequencia)-> go.Figure:
    min_f, max_f = min(frequencias), max(frequencias)
    #normalizar tamanho da fonte (entre 9 e 40)
    tamanhos:list = [ 9+(f-min_f)/(max_f-min_f +1)*41 for f in frequencias]
    #posições aleatórias:

    np.random.seed(42)
    x = np.random.uniform(0, 10, len(palavras_chave))
    y = np.random.uniform(0, 5, len(palavras_chave))   

    #figura plotly
    fig_frequencias:go.Figure = go.Figure()
    fig_frequencias.add_trace(go.Scatter(
        x= x,
        y= y,
        mode="text",
        text=palavras_chave,
        textfont=dict(size=tamanhos, color=[f"hsl({i * 37 % 360}, 70%, 45%)" for i in range(len(palavras_chave))]),
        hovertemplate="<b>%{text}</b><br>Frequência: " +
        [str(f) for f in frequencias][0] + "<extra></extra>",
        customdata=frequencias,
        #hovertemplate="<b>%{text}</b><br>Frequência: %{customdata}<extra></extra>",
        )
    )


    fig_frequencias.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
        title="Nuvem de Palavras",
    )

    return fig_frequencias

#Widget de upload de dados
file_upload = st.file_uploader("Faça upload dos dados", type=['xlsx'])

#verifica se foi feito upload
if file_upload:
    #leitura dos dados
    df:pd.DataFrame = pd.read_excel(file_upload)
    column_config = {"palavras-chave_res":st.column_config.ListColumn("palavra-chave_res", width="large")}
    df["palavras-chave_res"] = df["palavras-chave"].map(lambda palavras: list(set(palavras.split("; "))))
    #contar frequência de palavras
    palavras_chave_raw = normaliza_lista_texto(custom_flat(df["palavras-chave_res"].to_list(),3))
    contagem_palavras:Counter = Counter(palavras_chave_raw)
    palavras_chave = list(contagem_palavras.keys())
    frequencias = list(contagem_palavras.values())

    fig_frequencias:go.Figure = criar_nuvem_palavras(palavras_chave, frequencias)

    exp1 = st.expander("vagas referência")
    tab_tabela, tab_frequencia = exp1.tabs(["tabela", "frequencia"])
    with tab_tabela:
        st.dataframe(df)
    with tab_frequencia:
        st.plotly_chart(fig_frequencias)
        pass
    exp2 = st.expander("seleção de palavras-chave")
    exp2.text("clique nas palavras-chave abaixo para criar um modelo de palavras chave a serem adicionadas no seu currículo")
    selecionadas = set()
    cols = exp2.columns(3)
    for i, palavra in enumerate(sorted(palavras_chave)):
        with cols[i % 3]:
            if st.checkbox(palavra, key=f"{i}_{palavra}"):
                selecionadas.add(palavra)
