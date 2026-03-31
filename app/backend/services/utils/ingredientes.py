from app.backend.services.core.normalizacao import normalizar

def agrupar_ingredientes(lista):
    agrupado = {}

    for item in lista:
        chave = (item["nome"], item["unidade"])

        if chave not in agrupado:
            agrupado[chave] = item.copy()
        else:
            agrupado[chave]["quantidade"] += item["quantidade"]

    return list(agrupado.values())

def eh_farinha(item):
    return item and "farinha" in normalizar(item["nome"])

def consolidar_ingredientes(ingredientes):
    """
    Agrupa ingredientes iguais (mesmo nome + unidade)
    somando suas quantidades.
    """

    mapa = {}

    for item in ingredientes:
        if not item:
            continue

        chave = (item["nome"], item["unidade"])

        if chave not in mapa:
            mapa[chave] = item.copy()
        else:
            mapa[chave]["quantidade"] += item["quantidade"]

    return list(mapa.values())