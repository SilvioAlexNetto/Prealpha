import json
import random
import unicodedata
from copy import deepcopy

from bases import (
    proteinasUN, proteinasKG, legumes, carboidratos,
    folhas_saladas, massas, proteinas_proibidas_sopa,
    molhos, caldos
)

# =========================
# NORMALIZAÇÃO
# =========================
def normalizar(texto):
    return unicodedata.normalize("NFD", texto.lower()) \
        .encode("ascii", "ignore") \
        .decode("utf-8")


# =========================
# CLASSIFICAÇÃO DO ESTOQUE
# =========================
def classificar_estoque(estoque):
    estoque_classificado = []

    for item in estoque:
        nome_original = item["nome"]
        nome = normalizar(nome_original)

        categoria = None

        # =========================
        # PRIORIDADE DE CLASSIFICAÇÃO
        # =========================

        # 🥩 PROTEÍNA (primeiro sempre)
        if any(normalizar(p) in nome for p in proteinasKG + proteinasUN):
            categoria = "proteina"

        # 🍝 MASSA (antes de carbo)
        elif any(normalizar(m) in nome for m in massas):
            categoria = "massa"

        # 🍚 CARBO
        elif any(normalizar(c) in nome for c in carboidratos):
            categoria = "carbo"

        # 🥕 LEGUMES
        elif any(normalizar(l) in nome for l in legumes):
            categoria = "legume"

        # 🥬 FOLHAS
        elif any(normalizar(f) in nome for f in folhas_saladas):
            categoria = "folha"

        # 🥫 MOLHOS
        elif any(normalizar(mol) in nome for mol in molhos):
            categoria = "molho"

        # 🍲 CALDOS
        elif any(normalizar(caldo["nome"]) in nome for caldo in caldos):
            categoria = "caldo"

        # =========================
        # FALLBACK INTELIGENTE
        # =========================
        else:
            # tenta deduzir pelo nome
            if "arroz" in nome or "feijao" in nome or "batata" in nome:
                categoria = "carbo"

            elif "frango" in nome or "carne" in nome or "ovo" in nome:
                categoria = "proteina"

            elif "alface" in nome or "rucula" in nome:
                categoria = "folha"

            elif "molho" in nome:
                categoria = "molho"

            elif "caldo" in nome:
                categoria = "caldo"

        # =========================
        # SALVA SE FOI CLASSIFICADO
        # =========================
        if categoria:
            estoque_classificado.append({
                "nome": nome_original,
                "quantidade": float(item.get("quantidade", 0)),
                "unidade": item["unidade"],
                "categoria": categoria
            })

    return estoque_classificado


# =========================
# CONSUMO
# =========================
def consumir(estoque, categoria, qtd):
    candidatos = [i for i in estoque if i["categoria"] == categoria and i["quantidade"] > 0]

    if not candidatos:
        return None

    item = random.choice(candidatos)

    usar = min(item["quantidade"], qtd)
    item["quantidade"] -= usar

    return {
        "nome": item["nome"],
        "quantidade": usar,
        "unidade": item["unidade"]
    }


# =========================
# VALIDAÇÃO
# =========================
def receita_valida(*args):
    return all(arg is not None for arg in args)


# =========================
# CAFÉ
# =========================
def gerar_cafe(estoque):
    receitas = []

    for _ in range(31):
        proteina = consumir(estoque, "proteina", 2)
        carbo = consumir(estoque, "carbo", 50)

        if not receita_valida(proteina, carbo):
            continue

        receita = {
            "nome": f"Café com {proteina['nome']} e {carbo['nome']}",
            "categoria": "café",
            "ingredientes": [proteina, carbo],
            "modo_preparo": [
                "Prepare os ingredientes.",
                "Cozinhe ou aqueça conforme necessário.",
                "Monte o prato e sirva."
            ],
            "tempo_preparo": "10 minutos",
            "Porcao": "1"
        }

        receitas.append(receita)

    return receitas


# =========================
# ALMOÇO - PRATO SIMPLES
# =========================
def gerar_almoco_simples(estoque):
    # tenta consumir
    proteina = consumir(estoque, "proteina", 120)
    carbo = consumir(estoque, "carbo", 100)

    if not receita_valida(proteina, carbo):
        return None

    ingredientes = [proteina, carbo]

    # opcionais
    legume = consumir(estoque, "legume", 80)
    if legume:
        ingredientes.append(legume)

    folha = consumir(estoque, "folha", 50)
    if folha:
        ingredientes.append(folha)

    return {
        "nome": f"{proteina['nome']} com {carbo['nome']}",
        "categoria": "almoço",
        "ingredientes": ingredientes,
        "modo_preparo": [
            f"Grelhe {proteina['nome']} até dourar.",
            f"Cozinhe {carbo['nome']}.",
            "Prepare acompanhamentos.",
            "Monte o prato.",
            "Sirva quente."
        ],
        "tempo_preparo": "30 minutos",
        "Porcao": "1"
    }


# =========================
# ALMOÇO - MASSA (SEM BUG DE CONSUMO)
# =========================
def gerar_almoco_massa(estoque):
    # 🔥 copia temporária (evita consumir errado)
    estoque_temp = deepcopy(estoque)

    massa = consumir(estoque_temp, "massa", 100)
    molho = consumir(estoque_temp, "molho", 50)
    proteina = consumir(estoque_temp, "proteina", 100)

    if not massa or not molho or not proteina:
        return None

    ingredientes = [massa, molho, proteina]

    folha = consumir(estoque_temp, "folha", 50)
    if folha:
        ingredientes.append(folha)

    # 🔥 aplica consumo real só se receita for válida
    for item_temp in estoque_temp:
        for item_real in estoque:
            if item_temp["nome"] == item_real["nome"]:
                item_real["quantidade"] = item_temp["quantidade"]

    return {
        "nome": f"{massa['nome']} com {molho['nome']} e {proteina['nome']}",
        "categoria": "almoço",
        "ingredientes": ingredientes,
        "modo_preparo": [
            f"Cozinhe {massa['nome']} até al dente.",
            f"Aqueça {molho['nome']}.",
            f"Prepare {proteina['nome']}.",
            "Misture tudo.",
            "Sirva quente."
        ],
        "tempo_preparo": "25 minutos",
        "Porcao": "1"
    }


# =========================
# GERADOR PRINCIPAL (50/50 + FALLBACK)
# =========================
def gerar_almoco(estoque):
    receitas = []

    total = 31
    metade = total // 2
    restante = total - metade

    # =========================
    # SIMPLES
    # =========================
    for _ in range(metade):
        receita = gerar_almoco_simples(estoque)

        # fallback: tenta massa
        if not receita:
            receita = gerar_almoco_massa(estoque)

        if receita:
            receitas.append(receita)

    # =========================
    # MASSA
    # =========================
    for _ in range(restante):
        receita = gerar_almoco_massa(estoque)

        # fallback: vira simples
        if not receita:
            receita = gerar_almoco_simples(estoque)

        if receita:
            receitas.append(receita)

    # =========================
    # GARANTIR 31 (tentar completar)
    # =========================
    tentativas = 0
    while len(receitas) < 31 and tentativas < 20:
        receita = gerar_almoco_simples(estoque) or gerar_almoco_massa(estoque)

        if receita:
            receitas.append(receita)

        tentativas += 1

    random.shuffle(receitas)

    return receitas


# =========================
# JANTAR (COM SOPA)
# =========================
def gerar_janta(estoque):
    receitas = []
    tentativas = 0

    while len(receitas) < 31 and tentativas < 200:
        tentativas += 1

        tipo = random.choice(["pf", "massa", "sopa"])
        ingredientes = []

        # =========================
        # 🍲 SOPA
        # =========================
        if tipo == "sopa":
            proteina = consumir(estoque, "proteina", 80)
            caldo = consumir(estoque, "caldo", 500)
            legume1 = consumir(estoque, "legume", 80)
            legume2 = consumir(estoque, "legume", 80)

            if not receita_valida(proteina, caldo, legume1):
                continue

            if proteina["nome"] in proteinas_proibidas_sopa:
                continue

            ingredientes.extend([proteina, caldo, legume1])
            if legume2:
                ingredientes.append(legume2)

            receita = {
                "nome": f"Sopa de {proteina['nome']} com legumes",
                "categoria": "jantar",
                "ingredientes": ingredientes,
                "modo_preparo": [
                    "Ferva o caldo.",
                    "Adicione a proteína e cozinhe.",
                    "Acrescente os legumes.",
                    "Cozinhe até ficar macio.",
                    "Sirva quente."
                ],
                "tempo_preparo": "30 minutos",
                "Porcao": "1"
            }

        # =========================
        # 🍝 MASSA
        # =========================
        elif tipo == "massa":
            massa = consumir(estoque, "massa", 100)
            molho = consumir(estoque, "molho", 150)

            if not receita_valida(massa, molho):
                continue

            ingredientes.extend([massa, molho])

            # opcionais
            if random.random() < 0.7:
                legume = consumir(estoque, "legume", 70)
                if legume:
                    ingredientes.append(legume)

            if random.random() < 0.5:
                salada = consumir(estoque, "folha", 50)
                if salada:
                    ingredientes.append(salada)

            receita = {
                "nome": f"{massa['nome']} com {molho['nome']}",
                "categoria": "jantar",
                "ingredientes": ingredientes,
                "modo_preparo": [
                    "Cozinhe a massa até ficar al dente.",
                    "Aqueça o molho.",
                    "Misture tudo.",
                    "Sirva quente."
                ],
                "tempo_preparo": "25 minutos",
                "Porcao": "1"
            }

        # =========================
        # 🍽️ PF (PRATO NORMAL)
        # =========================
        else:
            proteina = consumir(estoque, "proteina", 120)
            carbo = consumir(estoque, "carbo", 100)

            if not receita_valida(proteina, carbo):
                continue

            ingredientes.extend([proteina, carbo])

            # opcionais
            if random.random() < 0.8:
                legume1 = consumir(estoque, "legume", 80)
                legume2 = consumir(estoque, "legume", 80)

                if legume1:
                    ingredientes.append(legume1)
                if legume2:
                    ingredientes.append(legume2)

            if random.random() < 0.5:
                salada = consumir(estoque, "folha", 50)
                if salada:
                    ingredientes.append(salada)

            receita = {
                "nome": f"{proteina['nome']} com {carbo['nome']}",
                "categoria": "jantar",
                "ingredientes": ingredientes,
                "modo_preparo": [
                    "Prepare a proteína.",
                    "Cozinhe o carboidrato.",
                    "Prepare os acompanhamentos.",
                    "Monte o prato.",
                    "Sirva quente."
                ],
                "tempo_preparo": "25 minutos",
                "Porcao": "1"
            }

        receitas.append(receita)

    return receitas


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def gerar_tudo(estoque_usuario):
    estoque_copia = deepcopy(estoque_usuario)

    estoque_classificado = classificar_estoque(estoque_copia)

    cafe = gerar_cafe(estoque_classificado)
    almoco = gerar_almoco(estoque_classificado)
    janta = gerar_janta(estoque_classificado)

    todas_receitas = cafe + almoco + janta

    with open("BancoReceitas.json", "w", encoding="utf-8") as f:
        json.dump(todas_receitas, f, ensure_ascii=False, indent=4)

    sobras = [i for i in estoque_classificado if i["quantidade"] > 0]

    with open("Sobras.json", "w", encoding="utf-8") as f:
        json.dump(sobras, f, ensure_ascii=False, indent=4)

    return {
        "total_receitas": len(todas_receitas),
        "sobras": sobras
    }