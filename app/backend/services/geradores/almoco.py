import random

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
from app.backend.services.utils.tracker import registrar_lista_consumo


def gerar_almoco(estoque, total_dias, tracker):

    print("🍽️ Gerando almoço...", flush=True)

    receitas = []
    tentativas = 0

    while len(receitas) < total_dias and tentativas < 300:
        tentativas += 1

        dias_restantes = total_dias - len(receitas)

        ingredientes = []
        nome = None
        modo_preparo = []
        tempo = 20

        tipo = random.choice(["pf", "massa"])

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

            # 🔥 valida base
            if not receita_valida(proteina, carbo):
                continue

            if proteina.get("subcategoria") == "liquido":
                continue

            ingredientes_temp = [proteina, carbo]

            # 🥕 LEGUME
            legume = simular_consumo(
                estoque, "legume", 80,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=100
            )

            if legume:
                ingredientes_temp.append(legume)

            # 🥬 FOLHA
            folha = simular_consumo(
                estoque, "folha", 50,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=50
            )

            if folha:
                ingredientes_temp.append(folha)

            # 🔥 valida final (igual café: só segue se tudo ok)
            if not receita_valida(*ingredientes_temp):
                continue

            # 🔥 consumo só acontece aqui
            registrar_lista_consumo(ingredientes_temp, tracker)
            
            for i in ingredientes_temp:
                aplicar_consumo(i)

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
        else:

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

            # 🔥 valida base
            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes_temp = [massa, molho, proteina]

            # 🥕 LEGUME
            legume = simular_consumo(
                estoque, "legume", 80,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=100
            )

            if legume:
                ingredientes_temp.append(legume)

            # 🥬 FOLHA
            folha = simular_consumo(
                estoque, "folha", 50,
                dias_restantes=dias_restantes,
                consumo_max_por_dia=50
            )

            if folha:
                ingredientes_temp.append(folha)

            # 🔥 valida final
            if not receita_valida(*ingredientes_temp):
                continue

            # 🔥 consumo só aqui

            registrar_lista_consumo(ingredientes_temp, tracker)

            for i in ingredientes_temp:
                aplicar_consumo(i)

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
            if legume:
                tempo += random.randint(3, 7)
            if folha:
                tempo += random.randint(1, 3)

            nome = f"{massa['nome']} com {molho['nome']} e {proteina['nome']}"

        # =========================
        # FINAL
        # =========================
        if not ingredientes:
            continue

        registrar_lista_consumo(ingredientes_temp, tracker)

        for i in ingredientes_temp:
                aplicar_consumo(i)

        receitas.append({
            "nome": nome,
            "categoria": "almoco",
            "ingredientes": ingredientes,
            "modo_preparo": modo_preparo,
            "tempo_preparo": f"{tempo} minutos",
            "Porcao": "1"
        })

        print("receitas:", len(receitas), flush=True)

    return receitas