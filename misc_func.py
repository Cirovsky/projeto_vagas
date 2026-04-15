import re
def normaliza_lista_texto(lista:list[str]):
     return [
        parte.strip()
        for item in lista
        for parte in re.split(r"[,;.]+", item)
        if parte.strip()
    ]