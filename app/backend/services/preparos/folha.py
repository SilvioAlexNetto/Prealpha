import random

def preparo_folha(nome):
    return [
        random.choice([
            f"Lave bem a {nome}.",
            f"Higienize a {nome} em água corrente.",
        ]),
        random.choice([
            f"Sirva a {nome} fresca como acompanhamento.",
            f"Tempere a {nome} com azeite e sal a gosto.",
        ])
    ]