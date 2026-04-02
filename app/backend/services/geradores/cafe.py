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

        # 🔥 NOVO MODELO INTELIGENTE
        status = analisar_estoque(estoque)
        opcoes = gerar_opcoes_cafe(status)

        if not opcoes:
            print("⚠️ Sem opções possíveis")
            break

        tipo = escolher_opcao(opcoes)

        # =========================
        # 🥤 VITAMINA
        # =========================
        if tipo == "vitamina":

            liquido, tipo_leite = simular_leite(estoque, 200)
            fruta = simular_consumo(estoque, "fruta", 1)

            if liquido and fruta:

                ingredientes_temp = [liquido, fruta]

                # opcional extra
                fruta2 = simular_consumo(estoque, "fruta", 1)
                if fruta2 and random.random() < 0.5:
                    ingredientes_temp.append(fruta2)

                for i in ingredientes_temp:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes_temp]
                ingredientes = consolidar_ingredientes(ingredientes)

                frutas_nome = [i["nome"] for i in ingredientes]

                nome = f"Vitamina de {' e '.join(frutas_nome)} com {tipo_leite}"

                modo_preparo = [
                    f"Bata {' e '.join(frutas_nome)} com {tipo_leite}.",
                    "Sirva gelado."
                ]

        # =========================
        # 🥣 MINGAU
        # =========================
        elif tipo == "mingau":

            cereal = simular_consumo(estoque, "cereal", 40)
            liquido = simular_leite(estoque, 200)[0]

            if cereal and liquido:

                ingredientes_temp = [cereal, liquido]

                for i in ingredientes_temp:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes_temp]

                nome = f"Mingau de {cereal['nome']}"

                modo_preparo = [
                    f"Cozinhe {cereal['nome']} com leite até engrossar.",
                    "Sirva quente."
                ]

                tempo = 10

        # =========================
        # 🥞 PANQUECA
        # =========================
        elif tipo == "panqueca":

            farinha = simular_consumo(estoque, "farinha", 50)
            liquido = simular_consumo(estoque, "liquido", 100)

            if farinha and liquido:

                ingredientes_temp = [farinha, liquido]

                for i in ingredientes_temp:
                    aplicar_consumo(i)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes_temp]

                nome = f"Panqueca de {farinha['nome']}"

                modo_preparo = [
                    "Misture os ingredientes.",
                    "Asse em frigideira até dourar."
                ]

                tempo = 15

        # =========================
        # 🍞 SIMPLES
        # =========================
        elif tipo == "simples":

            carbo = simular_consumo(estoque, "carboCF", 2, subcategoria="cafe")

            if carbo:

                fruta = simular_consumo(estoque, "fruta", 1)
                proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")

                ingredientes_temp = [carbo]

                if fruta:
                    ingredientes_temp.append(fruta)

                if proteina:
                    ingredientes_temp.append(proteina)

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

        # =========================
        # 🍎 FRUTA (fallback inteligente)
        # =========================
        elif tipo == "fruta":

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
        # 🔥 FALLBACK FINAL (só se tudo falhar)
        # =========================
        if not ingredientes:

            fruta = simular_consumo(estoque, "fruta", 1)

            if not fruta:
                print("⚠️ Sem mais fruta → parando")
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