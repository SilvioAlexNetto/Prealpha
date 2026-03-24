import random
from copy import deepcopy

from app.backend.engine.builders import gerar_pf, gerar_massa, gerar_sopa
from app.backend.data.alimentos import (
    proteinasKG, proteinasUN, carboidratos, vegetais, massas
)

# =========================
# NORMALIZAÇÃO
# =========================
def nome_igual(a, b):
    return a.strip().lower() == b.strip().lower()


# =========================
# BUSCAR ITEM NO ESTOQUE
# =========================
def buscar_item(nome, estoque):
    for item in estoque:
        if nome_igual(item["nome"], nome):
            return item
    return None


# =========================
# VALIDAR QUANTIDADE REAL
# =========================
def tem_quantidade(nome, quantidade, estoque):
    item = buscar_item(nome, estoque)
    if not item:
        return False
    return item["quantidade"] >= quantidade


# =========================
# CONSUMIR ESTOQUE REAL
# =========================
def consumir_estoque(nome, quantidade, estoque):
    item = buscar_item(nome, estoque)
    if item:
        item["quantidade"] -= quantidade
        if item["quantidade"] < 0:
            item["quantidade"] = 0
    return estoque


# =========================
# FILTROS BASEADOS NO ESTOQUE
# =========================
def filtrar_proteinas(estoque):
    return [
        item for item in estoque
        if item["nome"] in proteinasKG + proteinasUN
        and item["quantidade"] > 0
    ]


def filtrar_carbo(estoque):
    return [
        item for item in estoque
        if item["nome"] in carboidratos
        and item["quantidade"] > 0
    ]


def filtrar_vegetais(estoque):
    return [
        item for item in estoque
        if item["nome"] in vegetais
        and item["quantidade"] > 0
    ]


def filtrar_massas(estoque):
    return [
        item for item in estoque
        if item["nome"] in massas
        and item["quantidade"] > 0
    ]


# =========================
# GERAR RECEITA INTELIGENTE
# =========================
def gerar_receita_inteligente(estoque, max_tentativas=20):

    for _ in range(max_tentativas):

        proteinas = filtrar_proteinas(estoque)
        if not proteinas:
            return None, estoque

        proteina = random.choice(proteinas)

        # =========================
        # PF
        # =========================
        if random.random() < 0.5:

            carbos = filtrar_carbo(estoque)
            vegetais_disp = filtrar_vegetais(estoque)

            if not carbos or len(vegetais_disp) < 2:
                continue

            carbo = random.choice(carbos)
            vegs = random.sample(vegetais_disp, 2)

            # quantidades padrão
            qtd_prot = proteina["quantidade"] >= 120 and 120 or proteina["quantidade"]
            qtd_carbo = 90
            qtd_veg = 80

            # valida tudo
            if not (
                tem_quantidade(proteina["nome"], qtd_prot, estoque) and
                tem_quantidade(carbo["nome"], qtd_carbo, estoque) and
                tem_quantidade(vegs[0]["nome"], qtd_veg, estoque) and
                tem_quantidade(vegs[1]["nome"], qtd_veg, estoque)
            ):
                continue

            receita = gerar_pf(
                proteina["nome"], qtd_prot, proteina["unidade"],
                carbo["nome"], qtd_carbo,
                vegs
            )

            # consumir
            consumir_estoque(proteina["nome"], qtd_prot, estoque)
            consumir_estoque(carbo["nome"], qtd_carbo, estoque)
            consumir_estoque(vegs[0]["nome"], qtd_veg, estoque)
            consumir_estoque(vegs[1]["nome"], qtd_veg, estoque)

            return receita, estoque

        # =========================
        # MASSA
        # =========================
        if random.random() < 0.75:

            massas_disp = filtrar_massas(estoque)
            vegetais_disp = filtrar_vegetais(estoque)

            if not massas_disp or len(vegetais_disp) < 2:
                continue

            massa = random.choice(massas_disp)
            vegs = random.sample(vegetais_disp, 2)

            if not (
                tem_quantidade(massa["nome"], 100, estoque) and
                tem_quantidade(proteina["nome"], 120, estoque)
            ):
                continue

            receita = gerar_massa(
                massa["nome"],
                proteina["nome"], 120,
                vegs
            )

            consumir_estoque(massa["nome"], 100, estoque)
            consumir_estoque(proteina["nome"], 120, estoque)

            return receita, estoque

        # =========================
        # SOPA
        # =========================
        vegetais_disp = filtrar_vegetais(estoque)

        if len(vegetais_disp) < 3:
            continue

        vegs = random.sample(vegetais_disp, 3)

        if not tem_quantidade(proteina["nome"], 100, estoque):
            continue

        receita = gerar_sopa(
            proteina["nome"], 100,
            vegs
        )

        consumir_estoque(proteina["nome"], 100, estoque)

        return receita, estoque

    return None, estoque


# =========================
# API
# =========================
def gerar_receita(estoque):

    estoque_copia = deepcopy(estoque)

    receita, estoque_final = gerar_receita_inteligente(estoque_copia)

    if not receita:
        return {
            "status": "sem_ingredientes_suficientes"
        }

    return {
        "receita": receita,
        "estoque": estoque_final
    }