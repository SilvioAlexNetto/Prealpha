import unicodedata

def normalizar(texto):
    return unicodedata.normalize("NFD", texto.lower()) \
        .encode("ascii", "ignore") \
        .decode("utf-8")