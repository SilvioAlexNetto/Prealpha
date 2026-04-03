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

    extras = []

    if proteina:
        extras.append(proteina)

    if fruta:
        extras.append(fruta)

    # 🔥 REMOVE DUPLICADOS (CRÍTICO)
    extras = list(dict.fromkeys(extras))

    # =========================
    # ☕ CASO: BEBIDA
    # =========================
    if "cafe" in base_lower or "leite" in base_lower:

        if not extras:
            return base.capitalize()

        return f"{base} acompanhado de {' e '.join(extras)}".capitalize()

    # =========================
    # 🥞 MASSAS / BASES
    # =========================
    nome = base

    if recheio:
        nome += f" com recheio de {recheio}"

    if extras:
        nome += f" com {' e '.join(extras)}"

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
