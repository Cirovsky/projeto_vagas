import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from collections import Counter
from custom_flat import custom_flat
from misc_func import normaliza_lista_texto
from table_format import export_xlsx


def costumizar_slider():
    return components.html("""
    <script>
            const inputs = window.parent.document.querySelectorAll('input');
            console.log("total de inputs:", inputs.length);
            inputs.forEach(el => {
                console.log("tag:", el.tagName, "type:", el.type, "aria-label:", el.getAttribute("aria-label"));
            });
    </script>
""", height=0)

def criar_nuvem_palavras(contagem_palavras:Counter, densidade)-> go.Figure:
    contagem_palavras = {c:contagem_palavras[c] for c in contagem_palavras if contagem_palavras[c]>=(densidade -1)}
    palavras_chave = list(contagem_palavras.keys())
    frequencias = list(contagem_palavras.values())
    min_f, max_f = min(frequencias), max(frequencias)
    #normalizar tamanho da fonte (entre 9 e 40)
    #tamanhos:list = [ 9+(f-min_f)/(max_f-min_f +1)*41 for f in frequencias]
    tamanhos:list = [ f*(max_f*2) for f in frequencias]
    #posições aleatórias:

    np.random.seed(42)
    x = np.random.uniform(1, 9, len(palavras_chave))
    y = np.random.uniform(0.5, 5, len(palavras_chave))   

    #figura plotly
    fig_frequencias:go.Figure = go.Figure()
    fig_frequencias.add_trace(go.Scatter(
        x= x,
        y= y,
        mode="text",
        text=palavras_chave,
        textfont=dict(size=tamanhos, color=[f"hsl({i * 37 % 360}, 70%, 45%)" for i in range(len(palavras_chave))]),
        customdata=frequencias,
        hovertemplate="<b>%{text}</b><br>Frequência: %{customdata}<extra></extra>"
        )
    )


    fig_frequencias.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=50, b=40),
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


    exp1 = st.expander("vagas referência")
    tab_tabela, tab_frequencia = exp1.tabs(["tabela", "frequencia"])
    with tab_tabela:
        st.dataframe(df)
    with tab_frequencia:
        #densidade = st.slider(label="densidade",min_value=min(frequencias), max_value=max(frequencias))
        densidade = st.slider(label="densidade",min_value=min(frequencias), max_value=max(frequencias),key="slider_densidade")
        costumizar_slider()
        
        fig_frequencias:go.Figure = criar_nuvem_palavras(contagem_palavras, densidade)
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
