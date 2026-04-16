import pandas as pd
from xlsxwriter.worksheet import Worksheet
from datetime import datetime

def numbers_letters_conversion(len_cols:int)->str:
    '''This function convert a number, from 1 at 16384 in alphabetical code with max 3 letters, from A at XFD'''
    if len_cols > 0 and len_cols <= 26: 
        return chr(64 + len_cols)
    else:
        if len_cols > 26 and len_cols <= 16384:#this number is max number of columns in 
            n1 = 0
            n2 = 0
            n3 = 0
            for i in range(0,len_cols):
                n3+=1
                if i % 26 ==0 and i != 0:
                    n2 += 1
                    n3 = 1
                if n2 > 26:
                    n2 = 1
                    n1+=1
                    l1 = "" if n1 == 0 else chr(64 + n1)
                    l2 = "" if n2 == 0 else chr(64 + n2)
                    l3 = "" if n3 == 0 else chr(64 + n3)
                return l1 + l2 + l3
        else:
            if len_cols >  16384:
                print("The number of columns is more than 16384, which exceeds the excel column limit.")

def table_format(planilha:pd.ExcelWriter, sheet_name:str, df:pd.DataFrame, table_name:str) -> None:
    '''Format a dataframe into an 'Excel' table'''
    table_header:list[dict] = [{'header': col} for col in df.columns]
    bottom_num = len(df) + 1
    right_letter:str = numbers_letters_conversion(len_cols=len(df.columns))
    table_corner = right_letter + str(bottom_num)
    worksheet: Worksheet = planilha.sheets[sheet_name]
    worksheet.add_table('A1:' + table_corner, {'columns': table_header, 'name': table_name})

def export_xlsx (df:pd.DataFrame, output_file:str, sheet_name:str, table_name:str|None = None) -> None:
    '''Export a dataframe to an xlsx document with a formatted table'''
    if table_name is None:
        table_name = sheet_name
    with pd.ExcelWriter(path=f"{output_file}.xlsx", engine="xlsxwriter") as tabela:
        df.to_excel(excel_writer=tabela, sheet_name=sheet_name, index=False)
        table_format(tabela, sheet_name, df, table_name)
        print(f"table created at {output_file}.xlsx.")