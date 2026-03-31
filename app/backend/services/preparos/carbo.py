import random

def preparo_carbo(nome):
    return [
        random.choice([
            f"Cozinhe o {nome} em água fervente com uma pitada de sal.",
            f"Leve o {nome} para cozinhar em água quente até ficar macio.",
        ]),
        random.choice([
            f"Escorra e reserve o {nome}.",
            f"Após o cozimento, deixe o {nome} descansar por alguns minutos.",
        ])
    ]