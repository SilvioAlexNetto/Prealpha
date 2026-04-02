import random
from copy import deepcopy
from app.backend.services.core.consumo import consumir
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

def gerar_almoco(estoque, total_dias):
    receitas = []

    tentativas = 0

    while len(receitas) < total_dias and tentativas < 200:
        tentativas += 1

        tipo = random.choice(["pf", "massa"])

        # =========================
        # 🍽️ PF
        # =========================
        if tipo == "pf":
            proteina = consumir(estoque, "proteina", 120, bloquear=True)
            carbo = consumir(estoque, "carbo", 100, bloquear=True)

            if proteina and proteina.get("subcategoria") == "liquido":
                continue

            if not receita_valida(proteina, carbo):
                continue

            ingredientes = [proteina, carbo]

            # 🥕 LEGUME (CORRIGIDO)
            legume = consumir(estoque, "legume", 80)
            if legume:
                if legume["unidade"] == "g":
                    legume["quantidade"] = 80
                elif legume["unidade"] == "unidade":
                    legume["quantidade"] = 1
                ingredientes.append(legume)

            # 🥬 FOLHA (CORRIGIDO)
            folha = consumir(estoque, "folha", 50)
            if folha:
                if folha["unidade"] == "g":
                    folha["quantidade"] = 50
                elif folha["unidade"] == "unidade":
                    folha["quantidade"] = 1
                ingredientes.append(folha)

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

            receita = {
                "nome": nome,
                "categoria": "almoco",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

        # =========================
        # 🍝 MASSA
        # =========================
        else:
            estoque_temp = deepcopy(estoque)

            massa = consumir(estoque_temp, "massa", 100)
            molho = consumir(estoque_temp, "molho", 50)
            proteina = consumir(estoque_temp, "proteina", 100, bloquear=True)

            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes = [massa, molho, proteina]

            # 🥕 LEGUME (CORRIGIDO)
            legume = consumir(estoque_temp, "legume", 80)
            if legume:
                if legume["unidade"] == "g":
                    legume["quantidade"] = 80
                elif legume["unidade"] == "unidade":
                    legume["quantidade"] = 1
                ingredientes.append(legume)

            # 🥬 FOLHA (CORRIGIDO)
            folha = consumir(estoque_temp, "folha", 50)
            if folha:
                if folha["unidade"] == "g":
                    folha["quantidade"] = 50
                elif folha["unidade"] == "unidade":
                    folha["quantidade"] = 1
                ingredientes.append(folha)

            # aplica consumo real
            for item_temp in estoque_temp:
                for item_real in estoque:
                    if item_temp["nome"] == item_real["nome"]:
                        item_real["quantidade"] = item_temp["quantidade"]

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

            receita = {
                "nome": f"{massa['nome']} com {molho['nome']} e {proteina['nome']}",
                "categoria": "almoco",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

        receitas.append(receita)
        print("receitas:", len(receitas))

    return receitas