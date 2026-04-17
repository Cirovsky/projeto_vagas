import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from collections import Counter
from custom_flat import custom_flat
from misc_func import normaliza_lista_texto
from table_format import export_to_download

def similaridade(lista1: list[str], lista2: list[str]) -> float:
    """
    Calcula a similaridade entre duas listas de palavras.
    Retorna: len(interseção) / len(lista1)
    """
    set1 = set(lista1)
    set2 = set(lista2)
    
    comuns = set1 & set2
    
    if not set1:
        return 0.0
    
    return len(comuns) / len(set1)

def tratar_data_frame(df:pd.DataFrame,selecionadas:set)->pd.DataFrame:
    """adiciona a tabela de pesquisa de vagas as palavras-chave selecionadas e uma coluna de adesão às vagas"""
    list_keywords = sorted(list(selecionadas))
    df["palavras_selecionadas"] = df["palavras-chave_res"].map(lambda a: "; ".join(list_keywords))
    df["adesao_a_vaga"] = df["palavras-chave_res"].map(lambda kw: similaridade(kw, list_keywords))
    df["palavras-chave_res"] =df["palavras-chave_res"].map(lambda kw: "; ".join(kw))
    df.drop(columns="palavras-chave", inplace=True)
    df.rename(columns={"palavras-chave_res":"palavras-chave"}, inplace=True)
    return df
def exportar_arquivo(df)->bytes:
    return export_to_download(df,"analise_vagas_adesao",sheet_name="analise_vagas")

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
        margin=dict(l=20, r=20, t=30, b=20),
        title="Nuvem de Palavras",
    )

    return fig_frequencias

#estilo global:

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
    exp3 = st.expander("salvar seleção de palavras-chaves")
    tab_selecionadas, tab_adesao = exp3.tabs(["palavras selecionadas","adesão a vaga"])
    with tab_selecionadas:
        st.text_area(label="palavras-chave selecionadas",value="; ".join(selecionadas))
    with tab_adesao:
        btn_df_adesao = st.button(label="criar tabela de adesão")
        if btn_df_adesao:
            df_res = tratar_data_frame(df, selecionadas)
            st.dataframe(df_res)
            st.download_button(label="baixar arquivo com palavras selecionadas",
                            data=exportar_arquivo(df_res),
                            file_name="analise_vagas_adesao.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )