import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
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
    df["aderencia_vaga"] = df["palavras-chave_res"].map(lambda kw: similaridade(kw, list_keywords))
    df["palavras-chave_res"] =df["palavras-chave_res"].map(lambda kw: "; ".join(kw))
    df.drop(columns="palavras-chave", inplace=True)
    df.rename(columns={"palavras-chave_res":"palavras-chave"}, inplace=True)
    return df

@st.cache_data
def criar_nuvem_palavras(contagem_palavras:Counter):
    nuvem = WordCloud(width=800, height=400, background_color="black", mode="RGBA").generate_from_frequencies(contagem_palavras)
    fig, ax = plt.subplots()
    fig.patch.set_alpha(0)   # fundo da figura transparente
    fig.set_dpi(200)
    ax.imshow(nuvem, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
#estilo global:

tabela_md = st.markdown(
    f"""
#### Bem vindo ao seu dashboard para analisar vagas de emprego!
para utilizar, você deve criar uma planilha do excel no seguinte formato:
|nome do cargo|nome da vaga|senioridade|empresa|ramo|tamanho|palavras-chave|
|----|-----------|-----------|-------|----|-------|--------------|
|nome genérico do cargo|nome do cargo na vaga específica|jr,pleno ou senior|nome empresa|ramo da empresa| numero de funcionario ( exemplo 50-100)|descrição das funções do cargo|

    """
)



col_up, col_ex = st.columns(2)
#Widget de upload de dados

with col_up:
    file_upload = st.file_uploader("Faça upload dos dados", type=['xlsx'])
with col_ex:
    tabela_exemplo:pd.DataFrame = pd.read_excel("tabela_exemplo/estudo_vagas_analista_dados.xlsx")
    st.markdown("se precisar ou quiser testar, baixe essa planilha e dê upload no botão ao lado")
    gd_file_ID:str = "1pblemM-HExZQzLyeJup4fY9cKWS_ll0P"
    st.link_button(label="baixar",url=f"https://docs.google.com/uc?export=download&id={gd_file_ID}")

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
        #densidade = st.slider(label="densidade",min_value=min(frequencias), max_value=max(frequencias),key="slider_densidade")
        criar_nuvem_palavras(contagem_palavras)
    exp2 = st.expander("seleção de palavras-chave")
    exp2.text("clique nas palavras-chave abaixo para criar um modelo de palavras chave a serem adicionadas no seu currículo")
    selecionadas = set()
    cols = exp2.columns(3)
    for i, palavra in enumerate(sorted(palavras_chave, key=str.lower)):
        with cols[i % 3]:
            if st.checkbox(palavra, key=f"{i}_{palavra}"):
                selecionadas.add(palavra)
    exp3 = st.expander("salvar seleção de palavras-chaves")
    tab_selecionadas, tab_aderencia, tab_aderencia_grafico = exp3.tabs(["palavras selecionadas","aderência a vaga", "gráfico de aderência"])
    with tab_selecionadas:
        st.text_area(label="palavras-chave selecionadas",value="; ".join(selecionadas))
    with tab_aderencia:
        btn_df_adesao = st.button(label="criar tabela de aderencia")
        if btn_df_adesao:
            df_res = tratar_data_frame(df, selecionadas)
            st.dataframe(df_res)
            st.download_button(label="baixar arquivo com palavras selecionadas",
                            data=export_to_download(df_res,"analise_vagas"),
                            file_name="analise_vagas_aderencia.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
    with tab_aderencia_grafico:
        if btn_df_adesao:
            st.bar_chart(df_res,x = "empresa", y="aderencia_vaga")