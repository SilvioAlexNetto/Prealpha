import random

def tecnica_preparo():
    return random.choice([
        "grelhado",
        "assado",
        "cozido",
        "selado",
        "refogado"
    ])

def preparo_proteina(nome):
    tecnica = tecnica_preparo()
    nome_lower = nome.lower()

    base_temp = random.choice([
        f"Tempere o {nome} com sal, alho e pimenta.",
        f"Tempere o {nome} com sal, limão e ervas.",
    ])

    if tecnica == "grelhado":
        preparo = f"Grelhe o {nome} até dourar bem."
    elif tecnica == "assado":
        preparo = f"Leve o {nome} ao forno até ficar bem assado."
    elif tecnica == "cozido":
        preparo = f"Cozinhe o {nome} em água temperada até ficar macio."
    elif tecnica == "selado":
        preparo = f"Sele o {nome} em fogo alto até formar crosta."
    else:
        preparo = f"Refogue o {nome} até dourar levemente."

    return [base_temp, preparo]


