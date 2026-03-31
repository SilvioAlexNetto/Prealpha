import random
from copy import deepcopy

from app.backend.services.core.consumo import (
    simular_consumo,
    simular_leite,
    simular_cafe_completo,
    aplicar_consumo,
    ajustar_porcionamento
)

from app.backend.services.utils.nomes import nome_prato_cafe
from app.backend.services.utils.ingredientes import consolidar_ingredientes
from app.backend.services.preparos.cafe import gerar_preparo_cafe


def gerar_cafe_com_copia(estoque):
    estoque_temp = deepcopy(estoque)
    receitas = gerar_cafe(estoque_temp)

    for item_temp in estoque_temp:
        for item_real in estoque:
            if item_temp["nome"] == item_real["nome"]:
                item_real["quantidade"] = item_temp["quantidade"]

    return receitas


def gerar_cafe(estoque):

    receitas = []
    tentativas = 0

    while len(receitas) < 31 and tentativas < 200:
        tentativas += 1

        tipo_prato = random.choice(["robusto", "simples"])

        # =========================
        # 🔹 ROBUSTO
        # =========================
        if tipo_prato == "robusto":
            prato = random.choice(["Panqueca", "Mingau", "Crepioca", "Vitamina"])

            # =========================
            # 🥤 VITAMINA
            # =========================
            if prato == "Vitamina":

                liquido, tipo_leite = simular_leite(estoque, 200)
                if not liquido:
                    continue

                fruta1 = simular_consumo(estoque, "fruta", 1)
                fruta2 = simular_consumo(estoque, "fruta", 1)
                fruta3 = simular_consumo(estoque, "fruta", 1)
                cereal = simular_consumo(estoque, "cereal", 30)

                if not fruta1:
                    continue

                ingredientes = [liquido, fruta1]

                tipo_vitamina = random.choice(["basica", "nutritiva", "fortificada"])

                if tipo_vitamina != "basica":
                    if fruta2:
                        ingredientes.append(fruta2)
                    if fruta3:
                        ingredientes.append(fruta3)
                    if cereal and tipo_vitamina == "nutritiva":
                        ingredientes.append(cereal)

                # 🔥 aplica consumo
                for i in ingredientes:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes if i]
                ingredientes = consolidar_ingredientes(ingredientes)

                nomes_frutas = [
                    i["nome"] for i in ingredientes
                    if "fruta" in i.get("categorias", []) or "fruta" in i.get("subcategorias", [])
                ]

                nomes_frutas_unicos = list(dict.fromkeys(nomes_frutas))

                nome = f"Vitamina de {' e '.join(nomes_frutas_unicos)} com {tipo_leite}"

                modo_preparo = [
                    f"Adicione {' e '.join(nomes_frutas_unicos)} no liquidificador.",
                    f"Acrescente {tipo_leite}.",
                    "Bata até ficar homogêneo.",
                    "Sirva gelado."
                ]

                tempo = 5

            # =========================
            # 🍽️ OUTROS ROBUSTOS
            # =========================
            else:

                base_item = simular_consumo(estoque, "farinha", 50) if prato in ["Panqueca", "Crepioca"] \
                    else simular_consumo(estoque, "cereal", 50) or simular_consumo(estoque, "farinha", 50)

                liquido = simular_consumo(estoque, "liquido", 100)
                proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")
                fruta = simular_consumo(estoque, "fruta", 1)
                fermento = simular_consumo(estoque, "fermento", 5) if prato == "Panqueca" else None

                if not base_item or not liquido or not proteina:
                    continue

                ingredientes = [base_item, liquido, proteina]

                if fruta:
                    ingredientes.append(fruta)
                if fermento:
                    ingredientes.append(fermento)

                # 🔥 aplica consumo
                for i in ingredientes:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes if i]

                usa_recheio = prato in ["Panqueca", "Crepioca"]

                nome = nome_prato_cafe(
                    prato,
                    proteina=proteina["nome"],
                    fruta=None if usa_recheio else (fruta["nome"] if fruta else None),
                    recheio=fruta["nome"] if usa_recheio and fruta else None
                )

                modo_preparo = gerar_preparo_cafe(
                    prato,
                    proteina=proteina["nome"],
                    liquido=liquido["nome"],
                    fruta=None if usa_recheio else (fruta["nome"] if fruta else None),
                    recheio=fruta["nome"] if usa_recheio and fruta else None,
                )

                tempo = random.randint(10, 20)

        # =========================
        # 🔹 SIMPLES
        # =========================
        else:

            carbo = simular_consumo(estoque, "carboCF", 2, subcategoria="cafe")
            proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")
            liquido = simular_consumo(estoque, "liquido", 200)
            fruta = simular_consumo(estoque, "fruta", 1)

            bebida, cafe_base, leite = simular_cafe_completo(estoque)

            if not carbo:
                continue

            ingredientes = [carbo]

            if proteina:
                ingredientes.append(proteina)

            if fruta:
                ingredientes.append(fruta)

            if liquido and random.random() < 0.5:
                ingredientes.append(liquido)

            # 🔥 aplica consumo
            for i in ingredientes:
                aplicar_consumo(i)

            ingredientes = [ajustar_porcionamento(i) for i in ingredientes if i]

            nome_base = nome_prato_cafe(
                carbo["nome"],
                proteina=proteina["nome"] if proteina else None,
                fruta=fruta["nome"] if fruta else None
            )

            if bebida:
                nome = f"{nome_base} com {bebida['nome']}"
            else:
                nome = nome_base

            modo_preparo = gerar_preparo_cafe(
                "simples",
                proteina=proteina["nome"] if proteina else None,
                liquido=liquido["nome"] if liquido else None,
                fruta=fruta["nome"] if fruta else None
            )

            tempo = 5

        receita = {
            "nome": nome,
            "categoria": "cafe",
            "ingredientes": ingredientes,
            "modo_preparo": modo_preparo,
            "tempo_preparo": f"{tempo} minutos",
            "Porcao": "1"
        }

        receitas.append(receita)

    return receitas