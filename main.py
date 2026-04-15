import streamlit as st
import pandas as pd

#Widget de upload de dados
file_upload = st.file_uploader("Faça upload dos dados", type=['xlsx'])

#verifica se foi feito upload
if file_upload:
    #leitura dos dados
    df:pd.DataFrame = pd.read_excel(file_upload)
    column_config = {"palavras-chave_res":st.column_config.ListColumn("palavra-chave_res", width="large")}
    exp1 = st.expander("vagas modelo")
    df["palavras-chave_res"] = df["palavras-chave"].map(lambda palavras: list(set(palavras.split("; "))))
    exp1.dataframe(df)
#não tem arquivos'
