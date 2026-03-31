import random

def preparo_legume(nome):
    return [
        random.choice([
            f"Corte o {nome} em pedaços médios.",
            f"Pique o {nome} em partes menores.",
        ]),
        random.choice([
            f"Refogue o {nome} até ficar macio.",
            f"Cozinhe o {nome} até atingir uma textura macia.",
        ])
    ]