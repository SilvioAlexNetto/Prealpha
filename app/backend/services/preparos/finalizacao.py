import random

def finalizar_prato():
    return [
        random.choice([
            "Monte o prato organizando os ingredientes.",
            "Disponha os ingredientes no prato de forma equilibrada.",
        ]),
        random.choice([
            "Sirva ainda quente.",
            "Finalize e sirva imediatamente.",
        ])
    ]