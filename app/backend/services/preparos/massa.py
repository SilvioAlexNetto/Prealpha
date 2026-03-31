import random

def preparo_massa(nome):
    return [
        random.choice([
            f"Cozinhe o {nome} em água fervente com sal até ficar al dente.",
            f"Leve o {nome} para cozinhar em bastante água até atingir o ponto ideal.",
        ]),
        random.choice([
            f"Escorra a água e reserve o {nome}.",
            f"Após o cozimento, escorra bem o {nome}.",
        ])
    ]