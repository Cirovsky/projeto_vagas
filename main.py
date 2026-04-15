import streamlit as st
import pandas as pd
from custom_flat import custom_flat
from misc_func import normaliza_lista_texto

#Widget de upload de dados
file_upload = st.file_uploader("Faça upload dos dados", type=['xlsx'])

#verifica se foi feito upload
if file_upload:
    #leitura dos dados
    df:pd.DataFrame = pd.read_excel(file_upload)
    column_config = {"palavras-chave_res":st.column_config.ListColumn("palavra-chave_res", width="large")}
    exp1 = st.expander("tabela de vagas referência")
    df["palavras-chave_res"] = df["palavras-chave"].map(lambda palavras: list(set(palavras.split("; "))))
    exp1.dataframe(df)
    exp2 = st.expander("seleção de palavras-chave")
    exp2.text("clique nas palavras-chave abaixo para criar um modelo de palavras chave a serem adicionadas no seu currículo")
    palavras_chave:set = set(custom_flat(df["palavras-chave_res"].to_list(),2))
    exp2.text(palavras_chave)
#não tem arquivos'
    selecionadas = set()
    cols = st.columns(3)
    print(sorted(palavras_chave))
    for i, palavra in enumerate(sorted(normaliza_lista_texto(palavras_chave))):
        with cols[i % 3]:
            if st.checkbox(palavra, key=f"{i}_{palavra}"):
                selecionadas.add(palavra)