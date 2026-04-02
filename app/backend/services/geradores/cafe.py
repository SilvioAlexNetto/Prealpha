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


def gerar_cafe_com_copia(estoque, total_dias):
    estoque_temp = deepcopy(estoque)
    receitas = gerar_cafe(estoque_temp, total_dias)

    for item_temp in estoque_temp:
        for item_real in estoque:
            if item_temp["nome"] == item_real["nome"]:
                item_real["quantidade"] = item_temp["quantidade"]

    return receitas


def gerar_cafe(estoque, total_dias):

    print("☕ Gerando café...", flush=True)

    receitas = []
    tentativas = 0

    while len(receitas) < total_dias and tentativas < 300:
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

            prato = random.choice(["Panqueca", "Mingau", "Crepioca", "Vitamina"])

            # 🥤 VITAMINA
            if prato == "Vitamina":

                liquido, tipo_leite = simular_leite(estoque, 200)
                fruta1 = simular_consumo(estoque, "fruta", 1)

                if liquido and fruta1:

                    fruta2 = simular_consumo(estoque, "fruta", 1)
                    fruta3 = simular_consumo(estoque, "fruta", 1)
                    cereal = simular_consumo(estoque, "cereal", 30)

                    ingredientes = [liquido, fruta1]

                    if fruta2:
                        ingredientes.append(fruta2)
                    if fruta3 and random.random() < 0.5:
                        ingredientes.append(fruta3)
                    if cereal and random.random() < 0.5:
                        ingredientes.append(cereal)

                    # 🔥 CONSOME SÓ AGORA
                    for i in ingredientes:
                        aplicar_consumo(i)

                    ingredientes = [ajustar_porcionamento(i) for i in ingredientes]
                    ingredientes = consolidar_ingredientes(ingredientes)

                    frutas_nome = [
                        i["nome"] for i in ingredientes
                        if "fruta" in i.get("categorias", []) or "fruta" in i.get("subcategorias", [])
                    ]

                    frutas_nome = list(dict.fromkeys(frutas_nome))

                    nome = f"Vitamina de {' e '.join(frutas_nome)} com {tipo_leite}"

                    modo_preparo = [
                        f"Bata {' e '.join(frutas_nome)} com {tipo_leite}.",
                        "Sirva gelado."
                    ]

                    tempo = 5

            # 🍽️ OUTROS
            else:

                base = simular_consumo(estoque, "farinha", 50) if prato in ["Panqueca", "Crepioca"] \
                    else simular_consumo(estoque, "cereal", 50) or simular_consumo(estoque, "farinha", 50)

                liquido = simular_consumo(estoque, "liquido", 100)
                proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")

                if base and liquido and proteina:

                    fruta = simular_consumo(estoque, "fruta", 1)
                    fermento = simular_consumo(estoque, "fermento", 5) if prato == "Panqueca" else None

                    ingredientes = [base, liquido, proteina]

                    if fruta:
                        ingredientes.append(fruta)
                    if fermento:
                        ingredientes.append(fermento)

                    # 🔥 CONSOME SÓ AGORA
                    for i in ingredientes:
                        aplicar_consumo(i)

                    ingredientes = [ajustar_porcionamento(i) for i in ingredientes]

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
            fruta = simular_consumo(estoque, "fruta", 1)

            if carbo:

                proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")
                liquido = simular_consumo(estoque, "liquido", 200)

                ingredientes = [carbo]

                if proteina:
                    ingredientes.append(proteina)

                if fruta:
                    ingredientes.append(fruta)

                if liquido and random.random() < 0.5:
                    ingredientes.append(liquido)

                # 🔥 CONSOME SÓ AGORA
                for i in ingredientes:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes]

                nome = nome_prato_cafe(
                    carbo["nome"],
                    proteina=proteina["nome"] if proteina else None,
                    fruta=fruta["nome"] if fruta else None
                )

                modo_preparo = gerar_preparo_cafe(
                    "simples",
                    proteina=proteina["nome"] if proteina else None,
                    liquido=liquido["nome"] if liquido else None,
                    fruta=fruta["nome"] if fruta else None
                )

                tempo = 5

        # =========================
        # 🔥 FALLBACK OBRIGATÓRIO
        # =========================
        if not ingredientes:

            fruta = simular_consumo(estoque, "fruta", 1)

            if fruta:
                aplicar_consumo(fruta)

                ingredientes = [ajustar_porcionamento(fruta)]

                nome = fruta["nome"]

                modo_preparo = [
                    f"Lave e prepare {fruta['nome']}.",
                    "Sirva imediatamente."
                ]

                tempo = 2

        # =========================
        # FINALIZA
        # =========================
        if ingredientes:

            receita = {
                "nome": nome,
                "categoria": "cafe",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

            receitas.append(receita)
            print("receitas:", len(receitas), flush=True)

    return receitas