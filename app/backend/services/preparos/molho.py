import random

def preparo_molho(nome):
    return [
        random.choice([
            f"Aqueça o {nome} em fogo baixo.",
            f"Leve o {nome} ao fogo até aquecer bem.",
        ]),
        random.choice([
            f"Misture bem até ficar homogêneo.",
            f"Ajuste o tempero do {nome} se necessário.",
        ])
    ]