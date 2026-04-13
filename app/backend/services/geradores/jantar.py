import random
from copy import deepcopy

from app.backend.services.core.consumo import (
    simular_consumo,
    aplicar_consumo
)

from app.backend.services.utils.validacao import receita_valida
from app.backend.services.utils.nomes import nome_prato_pf
from app.backend.services.preparos.pf import gerar_preparo_pf
from app.backend.services.preparos.carbo import preparo_carbo
from app.backend.services.preparos.folha import preparo_folha
from app.backend.services.preparos.legume import preparo_legume
from app.backend.services.preparos.massa import preparo_massa
from app.backend.services.preparos.molho import preparo_molho
from app.backend.services.preparos.proteina import preparo_proteina
from app.backend.services.preparos.finalizacao import finalizar_prato
from app.backend.services.bases import proteinas_proibidas_sopa


def registrar_lista_consumo(lista, tracker):
    for item in lista:
        key = f"{item['nome']}|{item.get('unidade', '')}"

        if key not in tracker:
            tracker[key] = {
                "nome": item["nome"],
                "quantidade": 0,
                "unidade": item.get("unidade", "")
            }

        tracker[key]["quantidade"] += item.get("quantidade", 1)


def gerar_janta(estoque, total_dias, tracker):

    print("🌙 Gerando jantar...", flush=True)

    receitas = []
    tentativas = 0

    while len(receitas) < total_dias and tentativas < 300:
        tentativas += 1

        dias_restantes = total_dias - len(receitas)

        ingredientes = []
        nome = None
        modo_preparo = []
        tempo = 20

        tipo = random.choice(["pf", "massa", "sopa"])

        # =========================
        # 🍽️ PF
        # =========================
        if tipo == "pf":

            proteina = simular_consumo(
                estoque, "proteina", 120,
                bloquear=True,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=200
            )

            carbo = simular_consumo(
                estoque, "carbo", 100,
                bloquear=True,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=150
            )

            if not receita_valida(proteina, carbo):
                continue

            ingredientes_temp = [proteina, carbo]

            legume = simular_consumo(
                estoque, "legume", 80,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=100
            )

            if legume:
                ingredientes_temp.append(legume)

            folha = simular_consumo(
                estoque, "folha", 50,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=50
            )

            if folha:
                ingredientes_temp.append(folha)

            for i in ingredientes_temp:
                aplicar_consumo(i)

            registrar_lista_consumo(ingredientes_temp, tracker)

            ingredientes = ingredientes_temp

            nome = nome_prato_pf(
                proteina["nome"],
                carbo["nome"],
                legume["nome"] if legume else None,
                folha["nome"] if folha else None
            )

            modo_preparo = gerar_preparo_pf(
                proteina["nome"],
                carbo["nome"],
                legume["nome"] if legume else None,
                folha["nome"] if folha else None
            )

            tempo = random.randint(20, 35)

        # =========================
        # 🍝 MASSA
        # =========================
        elif tipo == "massa":

            massa = simular_consumo(
                estoque, "massa", 100,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=120
            )

            molho = simular_consumo(
                estoque, "molho", 50,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=80
            )

            proteina = simular_consumo(
                estoque, "proteina", 100,
                bloquear=True,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=200
            )

            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes_temp = [massa, molho, proteina]

            legume = simular_consumo(
                estoque, "legume", 80,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=100
            )

            if legume:
                ingredientes_temp.append(legume)

            folha = simular_consumo(
                estoque, "folha", 50,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=50
            )

            if folha:
                ingredientes_temp.append(folha)

            for i in ingredientes_temp:
                aplicar_consumo(i)

            registrar_lista_consumo(ingredientes_temp, tracker)

            ingredientes = ingredientes_temp

            modo_preparo = []
            modo_preparo += preparo_massa(massa["nome"])
            modo_preparo += preparo_molho(molho["nome"])
            modo_preparo += preparo_proteina(proteina["nome"])

            if legume:
                modo_preparo += preparo_legume(legume["nome"])

            if folha:
                modo_preparo += preparo_folha(folha["nome"])

            modo_preparo += finalizar_prato()

            tempo = 25

        # =========================
        # 🍲 SOPA
        # =========================
        else:

            proteina = simular_consumo(
                estoque, "proteina", 80,
                bloquear=True,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=150
            )

            caldo = simular_consumo(
                estoque, "caldo", 500,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=600
            )

            legume1 = simular_consumo(
                estoque, "legume", 80,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=100
            )

            legume2 = simular_consumo(
                estoque, "legume", 80,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=100
            )

            if not receita_valida(proteina, caldo, legume1):
                continue

            if proteina["nome"] in proteinas_proibidas_sopa:
                continue

            if legume2 and legume1 and legume2["nome"] == legume1["nome"]:
                legume2 = None

            ingredientes_temp = [caldo, proteina, legume1]

            if legume2:
                ingredientes_temp.append(legume2)

            for i in ingredientes_temp:
                aplicar_consumo(i)

            registrar_lista_consumo(ingredientes_temp, tracker)

            ingredientes = ingredientes_temp

            nome = random.choice([
                f"Sopa caseira de {proteina['nome']} com legumes",
                f"Caldo nutritivo de {proteina['nome']} com vegetais",
                f"Sopa leve de {proteina['nome']} com legumes frescos"
            ])

            modo_preparo = [
                f"Aqueça o {caldo['nome']} em uma panela média.",
                f"Adicione {proteina['nome']} e cozinhe até ficar macio.",
                f"Acrescente {legume1['nome']} e cozinhe por alguns minutos."
            ]

            if legume2:
                modo_preparo.append(
                    f"Adicione também {legume2['nome']} e cozinhe até os legumes ficarem macios."
                )

            modo_preparo += [
                "Ajuste o sal e os temperos a gosto.",
                "Sirva bem quente."
            ]

            tempo = random.randint(25, 40)

        if not ingredientes:
            continue

        receitas.append({
            "nome": nome,
            "categoria": "jantar",
            "ingredientes": ingredientes,
            "modo_preparo": modo_preparo,
            "tempo_preparo": f"{tempo} minutos",
            "Porcao": "1"
        })

        print("receitas:", len(receitas), flush=True)

    return receitas