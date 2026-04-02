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

            if prato == "Vitamina":

                liquido, tipo_leite = simular_leite(estoque, 200)
                fruta1 = simular_consumo(estoque, "fruta", 1)

                if liquido and fruta1:

                    fruta2 = simular_consumo(estoque, "fruta", 1)
                    cereal = simular_consumo(estoque, "cereal", 30)

                    temp_ingredientes = [liquido, fruta1]

                    if fruta2:
                        temp_ingredientes.append(fruta2)
                    if cereal and random.random() < 0.5:
                        temp_ingredientes.append(cereal)

                    # 🔥 AGORA SIM consome
                    for i in temp_ingredientes:
                        aplicar_consumo(i)

                    ingredientes = [ajustar_porcionamento(i) for i in temp_ingredientes]
                    ingredientes = consolidar_ingredientes(ingredientes)

                    frutas_nome = [
                        i["nome"] for i in ingredientes
                        if "fruta" in i.get("categorias", []) or "fruta" in i.get("subcategorias", [])
                    ]

                    nome = f"Vitamina de {' e '.join(frutas_nome)} com {tipo_leite}"
                    modo_preparo = [
                        f"Bata {' e '.join(frutas_nome)} com {tipo_leite}.",
                        "Sirva gelado."
                    ]

                    tempo = 5

        # =========================
        # 🔹 SIMPLES
        # =========================
        else:

            carbo = simular_consumo(estoque, "carboCF", 2, subcategoria="cafe")
            fruta = simular_consumo(estoque, "fruta", 1)

            if carbo:

                proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")
                liquido = simular_consumo(estoque, "liquido", 200)

                temp_ingredientes = [carbo]

                if proteina:
                    temp_ingredientes.append(proteina)

                if fruta:
                    temp_ingredientes.append(fruta)

                if liquido and random.random() < 0.5:
                    temp_ingredientes.append(liquido)

                # 🔥 só consome aqui
                for i in temp_ingredientes:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in temp_ingredientes]

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
        # 🔥 FALLBACK CONTROLADO
        # =========================
        if not ingredientes:

            fruta = simular_consumo(estoque, "fruta", 1)

            # 🔥 SE NÃO TEM MAIS FRUTA → PARA
            if not fruta:
                print("⚠️ Sem mais fruta, parando geração de café")
                break

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