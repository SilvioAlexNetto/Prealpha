import random
from copy import deepcopy

from app.backend.services.core.consumo import (
    simular_consumo,
    simular_leite,
    aplicar_consumo,
    ajustar_porcionamento
)

from app.backend.services.utils.nomes import nome_prato_cafe
from app.backend.services.utils.ingredientes import consolidar_ingredientes
from app.backend.services.preparos.cafe import gerar_preparo_cafe


def gerar_cafe_com_copia(estoque, total_dias):
    estoque_temp = deepcopy(estoque)
    receitas = gerar_cafe(estoque_temp, total_dias)

    # aplica consumo no estoque real
    for item_temp in estoque_temp:
        for item_real in estoque:
            if item_temp["nome"] == item_real["nome"]:
                item_real["quantidade"] = item_temp["quantidade"]

    return receitas


def gerar_cafe(estoque, total_dias):

    print("☕ Gerando café...", flush=True)

    receitas = []
    tentativas = 0

    while len(receitas) < total_dias and tentativas < 400:
        tentativas += 1

        ingredientes = []
        nome = None
        modo_preparo = []
        tempo = 5

        tipo_prato = random.choice(["robusto", "simples"])

        # =========================
        # 🔹 ROBUSTO
        # =========================
        if tipo_prato == "robusto":

            prato = random.choice(["Vitamina", "Panqueca", "Mingau", "Crepioca"])

            # -------------------------
            # 🥤 VITAMINA
            # -------------------------
            if prato == "Vitamina":

                liquido, tipo_leite = simular_leite(estoque, 200)
                fruta1 = simular_consumo(estoque, "fruta", 1)

                if not liquido or not fruta1:
                    continue  # 🔥 NÃO consome nada

                fruta2 = simular_consumo(estoque, "fruta", 1)
                cereal = simular_consumo(estoque, "cereal", 30)

                ingredientes_temp = [liquido, fruta1]

                if fruta2:
                    ingredientes_temp.append(fruta2)

                if cereal and random.random() < 0.5:
                    ingredientes_temp.append(cereal)

                # 🔥 AGORA SIM consome
                for i in ingredientes_temp:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes_temp]
                ingredientes = consolidar_ingredientes(ingredientes)

                frutas_nome = [
                    i["nome"] for i in ingredientes
                    if "fruta" in i.get("categorias", [])
                ]

                nome = f"Vitamina de {' e '.join(frutas_nome)} com {tipo_leite}"

                modo_preparo = [
                    f"Bata {' e '.join(frutas_nome)} com {tipo_leite}.",
                    "Sirva gelado."
                ]

                tempo = 5

            # -------------------------
            # 🍽️ OUTROS ROBUSTOS
            # -------------------------
            else:

                base = simular_consumo(estoque, "farinha", 50) \
                    or simular_consumo(estoque, "cereal", 50)

                liquido = simular_consumo(estoque, "liquido", 100)
                proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")

                if not base or not liquido or not proteina:
                    continue  # 🔥 NÃO consome

                fruta = simular_consumo(estoque, "fruta", 1)

                ingredientes_temp = [base, liquido, proteina]

                if fruta:
                    ingredientes_temp.append(fruta)

                # 🔥 consome só aqui
                for i in ingredientes_temp:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes_temp]

                nome = nome_prato_cafe(
                    prato,
                    proteina=proteina["nome"],
                    fruta=fruta["nome"] if fruta else None
                )

                modo_preparo = gerar_preparo_cafe(
                    prato,
                    proteina=proteina["nome"],
                    liquido=liquido["nome"],
                    fruta=fruta["nome"] if fruta else None
                )

                tempo = random.randint(10, 20)

        # =========================
        # 🔹 SIMPLES
        # =========================
        else:

            carbo = simular_consumo(estoque, "carboCF", 2, subcategoria="cafe")

            if not carbo:
                continue

            fruta = simular_consumo(estoque, "fruta", 1)
            proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")

            ingredientes_temp = [carbo]

            if fruta:
                ingredientes_temp.append(fruta)

            if proteina:
                ingredientes_temp.append(proteina)

            # 🔥 consome só depois de validar
            for i in ingredientes_temp:
                aplicar_consumo(i)

            ingredientes = [ajustar_porcionamento(i) for i in ingredientes_temp]

            nome = nome_prato_cafe(
                carbo["nome"],
                proteina=proteina["nome"] if proteina else None,
                fruta=fruta["nome"] if fruta else None
            )

            modo_preparo = gerar_preparo_cafe(
                "simples",
                proteina=proteina["nome"] if proteina else None,
                fruta=fruta["nome"] if fruta else None
            )

            tempo = 5

        # =========================
        # 🔥 FALLBACK CONTROLADO
        # =========================
        if not ingredientes:

            fruta = simular_consumo(estoque, "fruta", 1)

            if not fruta:
                continue  # 🔥 NÃO consome nada

            # 🔥 só consome se realmente vai usar
            aplicar_consumo(fruta)

            ingredientes = [ajustar_porcionamento(fruta)]

            nome = fruta["nome"]

            modo_preparo = [
                f"Lave e sirva {fruta['nome']}."
            ]

            tempo = 2

        # =========================
        # FINAL
        # =========================
        receitas.append({
            "nome": nome,
            "categoria": "cafe",
            "ingredientes": ingredientes,
            "modo_preparo": modo_preparo,
            "tempo_preparo": f"{tempo} minutos",
            "Porcao": "1"
        })

        print("receitas:", len(receitas), flush=True)

    return receitas