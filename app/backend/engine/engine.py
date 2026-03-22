import random
from copy import deepcopy
from app.database.database import listar_estoque_atual
from app.backend.engine.builders import gerar_pf, gerar_massa, gerar_sopa

from app.backend.engine.core import (
    escolher_tipo,
    escolher_proteina,
    escolher_carbo_compativel,
    adicionar_salada,
    escolher_proteina_sopa
)

# =========================
# VERIFICAR ESTOQUE
# =========================
def tem_no_estoque(item_nome, estoque):
    for item in estoque:
        if item["nome"].lower() == item_nome.lower():
            return item["quantidade"] > 0
    return False


# =========================
# CONSUMIR ESTOQUE
# =========================
def consumir_estoque(item_nome, quantidade, estoque):

    for item in estoque:
        if item["nome"].lower() == item_nome.lower():

            item["quantidade"] -= quantidade

            if item["quantidade"] < 0:
                item["quantidade"] = 0

    return estoque


# =========================
# VALIDAÇÕES
# =========================
def validar_proteina(proteina, estoque):
    return tem_no_estoque(proteina["nome"], estoque)


def validar_carbo(carbo, estoque):
    return tem_no_estoque(carbo, estoque)




# =========================
# 🔥 ENGINE PROCEDURAL MENSAL (NOVO CORE)
# =========================

def gerar_cardapio_mensal():

    estoque_inicial = listar_estoque_atual()
    estoque = deepcopy(estoque_inicial)

    cardapio = {}

    for dia in range(1, 32):

        cardapio[dia] = {
            "cafe": None,
            "almoco": None,
            "jantar": None
        }

        for refeicao in ["cafe", "almoco", "jantar"]:

            receita, estoque = gerar_receita_inteligente(estoque)

            # 🔥 fallback final de segurança
            if receita is None:
                cardapio[dia][refeicao] = {
                    "nome": "Refeição alternativa",
                    "ingredientes": [],
                    "modo_preparo": [],
                    "tempo_preparo": "0 min"
                }
            else:
                cardapio[dia][refeicao] = receita

    return cardapio, estoque

def gerar_receita_inteligente(estoque, max_tentativas=10):

    for _ in range(max_tentativas):

        tipo = escolher_tipo()

        # =========================
        # PRATO FEITO
        # =========================
        if tipo == "pf":

            proteina = escolher_proteina()

            if not validar_proteina(proteina, estoque):
                continue  # 🔥 FALLBACK: tenta outra receita

            carbo = escolher_carbo_compativel(proteina["nome"])

            if not validar_carbo(carbo, estoque):
                carbo = "Arroz branco"

            salada = adicionar_salada()

            receita = gerar_pf()

            estoque = consumir_estoque(proteina["nome"], 1, estoque)
            estoque = consumir_estoque(carbo, 1, estoque)

            return receita, estoque

        # =========================
        # SOPA
        # =========================
        if tipo == "sopa":

            proteina = escolher_proteina_sopa()

            if not validar_proteina(proteina, estoque):
                continue  # 🔥 pula e tenta outra

            receita = gerar_sopa()

            estoque = consumir_estoque(proteina["nome"], 1, estoque)

            return receita, estoque

        # =========================
        # MASSA
        # =========================
        if tipo == "massa":

            proteina = escolher_proteina()

            if not validar_proteina(proteina, estoque):
                continue

            carbo = "Macarrão"

            if not validar_carbo(carbo, estoque):
                carbo = "Arroz branco"

            receita = gerar_massa()

            estoque = consumir_estoque(proteina["nome"], 1, estoque)
            estoque = consumir_estoque(carbo, 1, estoque)

            return receita, estoque

    # 🔥 se nenhuma tentativa funcionar
    return None, estoque


# =========================
# API LEGACY (mantido)
# =========================
def gerar_receita(estoque):

    receita, estoque_atual = gerar_receita_inteligente(estoque)

    if not receita:
        return {
            "status": "sem_ingredientes_suficientes"
        }

    return {
        "receita": receita,
        "estoque": estoque_atual
    }