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
from app.backend.services.bases import proteinas_proibidas_sopa


def gerar_janta(estoque):
    receitas = []
    tentativas = 0

    while len(receitas) < 31 and tentativas < 200:
        tentativas += 1

        tipo = random.choice(["pf", "massa", "sopa"])

        # =========================
        # 🍽️ PF
        # =========================
        if tipo == "pf":
            proteina = consumir(estoque, "proteina", 120, bloquear=True)
            carbo = consumir(estoque, "carbo", 100, bloquear=True)

            if not receita_valida(proteina, carbo):
                continue

            ingredientes = [proteina, carbo]

            # 🥕 LEGUME (CORRIGIDO)
            legume = consumir(estoque, "legume", 80)
            if legume:
                if legume["unidade"] == "g":
                    legume["quantidade"] = 80
                elif legume["unidade"] == "unidade":
                    legume["quantidade"] = random.choice([1, 2])
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
                "categoria": "jantar",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

        # =========================
        # 🍝 MASSA
        # =========================
        elif tipo == "massa":
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
                    legume["quantidade"] = random.choice([1, 2])
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
                "categoria": "jantar",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

        # =========================
        # 🍲 SOPA (CORRIGIDO)
        # =========================
        else:
            proteina = consumir(estoque, "proteina", 80, bloquear=True)
            caldo = consumir(estoque, "caldo", 500)
            legume1 = consumir(estoque, "legume", 80)
            legume2 = consumir(estoque, "legume", 80)

            if not receita_valida(proteina, caldo, legume1):
                continue

            if proteina["nome"] in proteinas_proibidas_sopa:
                continue

            # 🥕 AJUSTE LEGUME 1
            if legume1:
                if legume1["unidade"] == "g":
                    legume1["quantidade"] = 80
                elif legume1["unidade"] == "unidade":
                    legume1["quantidade"] = random.choice([1, 2])

            # 🥕 AJUSTE LEGUME 2 (evita duplicação ruim)
            if legume2 and legume2["nome"] != legume1["nome"]:
                if legume2["unidade"] == "g":
                    legume2["quantidade"] = 80
                elif legume2["unidade"] == "unidade":
                    legume2["quantidade"] = random.choice([1, 2])
            else:
                legume2 = None  # evita "2x cenoura separada"

            ingredientes = [caldo, proteina, legume1]
            if legume2:
                ingredientes.append(legume2)

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

            receita = {
                "nome": nome,
                "categoria": "jantar",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

        receitas.append(receita)

    return receitas
