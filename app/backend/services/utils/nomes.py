import random
from app.backend.services.preparos.proteina import tecnica_preparo

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

    # =========================
    # 🧠 NORMALIZA
    # =========================
    usados = set()

    def adicionar(item):
        if not item:
            return None

        item_lower = item.lower()

        # 🔥 evita duplicar leite
        if "leite" in item_lower and "leite" in base_lower:
            return None

        # 🔥 evita duplicar ingrediente
        if item_lower in usados:
            return None

        usados.add(item_lower)
        return item

    proteina = adicionar(proteina)
    fruta = adicionar(fruta)
    recheio = adicionar(recheio)

    # =========================
    # 🥞 CASOS COM RECHEIO
    # =========================
    if base_lower in ["panqueca", "crepioca"]:

        partes = []

        if recheio:
            partes.append(f"recheio de {recheio}")

        if proteina:
            partes.append(proteina)

        if fruta:
            partes.append(fruta)

        if partes:
            nome += " com " + " e ".join(partes)

    # =========================
    # ☕ CASOS GERAIS
    # =========================
    else:
        partes = []

        if proteina:
            partes.append(proteina)

        if fruta:
            partes.append(fruta)

        if partes:
            nome += " com " + " e ".join(partes)

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
