import random
from app.backend.data.alimentos import *


def escolher_tipo():
    r = random.random()

    if r < 0.5:
        return "pf"
    elif r < 0.8:
        return "massa"
    else:
        return "sopa"
    
def escolher_proteina():

    tipo = random.choice(["KG", "UN"])

    if tipo == "KG":
        return {
            "nome": random.choice(proteinasKG),
            "quantidade": 120,
            "unidade": "g"
        }

    return {
        "nome": random.choice(proteinasUN),
        "quantidade": 2,
        "unidade": "unidade"
    }

def escolher_carbo_compativel(proteina_nome):

    nome = proteina_nome.lower()

    if "peixe" in nome or "salmão" in nome:
        return random.choice([
            "Arroz integral",
            "Quinoa",
            "Legumes cozidos"
        ])

    if "bovina" in nome or "patinho" in nome or "carne" in nome:
        return random.choice([
            "Arroz branco",
            "Feijão",
            "Batata",
            "Mandioca"
        ])

    return random.choice(carboidratos)

def adicionar_salada():
    return random.random() < 0.5

def escolher_proteina_sopa():

    while True:
        proteina = escolher_proteina()

        if proteina["nome"] not in proteinas_proibidas_sopa:
            return proteina