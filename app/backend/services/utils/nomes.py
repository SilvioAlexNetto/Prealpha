import random

def nome_prato_pf(proteina, carbo, legume=None, folha=None):
    tecnica = tecnica_preparo()

    descricoes_carbo = [
        f"{carbo} soltinho",
        f"{carbo} bem cozido",
        f"{carbo} leve e macio"
    ]

    descricoes_legume = [
        "legumes salteados",
        "legumes refogados",
        "mix de legumes"
    ]

    nome = f"{proteina} {tecnica} com {random.choice(descricoes_carbo)}"

    if legume:
        nome += f" e {random.choice(descricoes_legume)}"

    if folha:
        nome += f" acompanhado de salada de {folha}"

    return nome.capitalize()

def nome_prato_cafe(base, proteina=None, fruta=None, recheio=None):

    base_lower = base.lower()
    nome = base

    # 🔥 só usa recheio quando faz sentido
    usa_recheio = base_lower in ["panqueca", "crepioca"]

    if usa_recheio and recheio:
        nome += f" com recheio de {recheio}"

        if proteina:
            nome += f" e {proteina}"

    else:
        if proteina:
            nome += f" com {proteina}"

        if fruta:
            nome += f" e {fruta}"

    return nome.capitalize()


def combinar_partes_nome(base, extras):
    """
    Combina partes do nome evitando repetição de conectores
    e repetição de ingredientes no nome.
    """
    partes = [base]

    conectores = ["com", "e", "acompanhado de"]

    usados = set()
    extras_unicos = []

    # 🔥 remove duplicados mantendo ordem
    vistos = set()
    for extra in extras:
        if extra and extra not in vistos:
            extras_unicos.append(extra)
            vistos.add(extra)

    for extra in extras_unicos:
        conector = random.choice(conectores)

        # evita repetir conector
        tentativas = 0
        while conector in usados and tentativas < 5:
            conector = random.choice(conectores)
            tentativas += 1

        usados.add(conector)
        partes.append(f"{conector} {extra}")

    return " ".join(partes)
