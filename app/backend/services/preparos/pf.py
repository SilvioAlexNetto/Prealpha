import random

def gerar_preparo_pf(proteina, carbo, legume=None, folha=None):
    preparo = []

    # 🔥 proteína
    preparo += preparo_proteina(proteina)

    # 🍚 carbo
    preparo += preparo_carbo(carbo)

    # 🥕 legume
    if legume:
        preparo += preparo_legume(legume)

    # 🥬 salada (mais realista)
    if folha:
        preparo += [
            random.choice([
                f"Lave bem a {folha} e deixe escorrer.",
                f"Higienize a {folha} em água corrente e seque.",
            ]),
            random.choice([
                f"Tempere a {folha} com azeite e sal a gosto.",
                f"Finalize a {folha} com um fio de azeite.",
            ])
        ]

    # 🍽️ finalização mais natural
    preparo += [
        random.choice([
            "Monte o prato distribuindo os ingredientes de forma equilibrada.",
            "Organize os ingredientes no prato para uma boa apresentação.",
        ]),
        random.choice([
            "Sirva ainda quente.",
            "Finalize e sirva imediatamente.",
        ])
    ]

    return preparo