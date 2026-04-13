import random
from copy import deepcopy

from app.backend.services.core.consumo import (
    simular_consumo,
    simular_leite,
    analisar_estoque,
    gerar_opcoes_cafe,
    escolher_opcao,
    montar_base_cafe, 
    aplicar_itens_cafe
)

from app.backend.services.utils.nomes import nome_prato_cafe
from app.backend.services.utils.ingredientes import consolidar_ingredientes
from app.backend.services.preparos.cafe import gerar_preparo_cafe
from app.backend.services.utils.tracker import registrar_lista_consumo


def montar_cafe_base(estoque, dias_restantes):

    base = []

    # prioridade: equilíbrio nutricional + uso de estoque

    carbo = simular_consumo(estoque, "carboCF", 2, subcategoria="cafe",
                            dias_restantes=dias_restantes,
                            consumo_max_por_dia=2)

    proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe",
                               dias_restantes=dias_restantes,
                               consumo_max_por_dia=1)

    fruta = simular_consumo(estoque, "fruta", 1,
                            dias_restantes=dias_restantes,
                            consumo_max_por_dia=1)

    cereal = simular_consumo(estoque, "cereal", 40,
                             dias_restantes=dias_restantes,
                             consumo_max_por_dia=40)

    leite = simular_leite(estoque, 200)[0]

    # =========================
    # 🧠 MONTAGEM INTELIGENTE
    # =========================

    if carbo:
        base.append(carbo)

    if proteina:
        base.append(proteina)

    if fruta:
        base.append(fruta)

    # 🔥 só adiciona cereal se fizer sentido
    if cereal and not carbo:
        base.append(cereal)

    # 🔥 bebida SEMPRE que possível
    if leite:
        base.append(leite)

    return base


def montar_receita_cafe(base):

    if not base:
        return None, None, None

    nomes = [i["nome"] for i in base]

    tem_fruta = any("fruta" in i["categorias"] for i in base)
    tem_leite = any("liquido" in i["categorias"] for i in base)
    tem_cereal = any("cereal" in i["categorias"] for i in base)
    tem_carbo = any("carboCF" in i["categorias"] for i in base)
    tem_proteina = any("proteinaCF" in i["categorias"] for i in base)

    nome = ""
    modo_preparo = []
    tempo = 5

    # =========================
    # 🥤 VITAMINA
    # =========================
    if tem_fruta and tem_leite and not tem_carbo:

        frutas = [i["nome"] for i in base if "fruta" in i["categorias"]]

        nome = f"Vitamina de {' e '.join(frutas)} com leite"

        modo_preparo = [
            f"Bata {' e '.join(frutas)} com leite.",
            "Sirva gelado."
        ]

        tempo = 5

    # =========================
    # 🥣 MINGAU
    # =========================
    elif tem_cereal and tem_leite:

        cereal = next(i for i in base if "cereal" in i["categorias"])

        nome = f"Mingau de {cereal['nome']}"

        modo_preparo = [
            f"Cozinhe {cereal['nome']} com leite até engrossar.",
            "Sirva quente."
        ]

        tempo = 10

    # =========================
    # ☕ CAFÉ COMPLETO (NOVO 🔥)
    # =========================
    elif tem_carbo or tem_proteina:

        partes = []

        if tem_carbo:
            partes.append("base de carboidrato")

        if tem_proteina:
            partes.append("fonte de proteína")

        if tem_fruta:
            partes.append("acompanhamento de fruta")

        nome = "Café da manhã com " + ", ".join(partes)

        modo_preparo = [
            f"Prepare {' ,'.join(nomes)}.",
            "Monte o prato e sirva."
        ]

        tempo = 5

    # =========================
    # 🍎 FRUTA (fallback)
    # =========================
    else:

        nome = nomes[0]

        modo_preparo = [
            f"Lave e prepare {nomes[0]}.",
            "Sirva imediatamente."
        ]

        tempo = 2

    return nome, modo_preparo, tempo



def gerar_cafe_com_copia(estoque, total_dias):
    estoque_temp = deepcopy(estoque)
    receitas = gerar_cafe(estoque_temp, total_dias)

    # aplica consumo no estoque real
    for item_temp in estoque_temp:
        for item_real in estoque:
            if item_temp["nome"] == item_real["nome"]:
                item_real["quantidade"] = item_temp["quantidade"]

    return receitas



def gerar_cafe(estoque, total_dias, tracker):

    print("☕ Gerando café...", flush=True)

    receitas = []
    tentativas = 0

    while len(receitas) < total_dias and tentativas < 300:
        tentativas += 1

        dias_restantes = total_dias - len(receitas)

        # =========================
        # 🧠 INTELIGÊNCIA
        # =========================
        status = analisar_estoque(estoque)
        opcoes = gerar_opcoes_cafe(status)

        if not opcoes:
            print("⚠️ Sem opções possíveis")
            break

        tipo = escolher_opcao(opcoes)

        # =========================
        # 🔥 NOVA BASE INTELIGENTE
        # =========================
        itens_base = montar_base_cafe(estoque, tipo, dias_restantes)

        if not itens_base:
            continue

        ingredientes, bebidas = aplicar_itens_cafe(itens_base)

        if not ingredientes and not bebidas:
            continue

        # =========================
        # 🧾 CONSOLIDA INGREDIENTES
        # =========================
        ingredientes = consolidar_ingredientes(ingredientes)

        # =========================
        # 🏷️ NOME INTELIGENTE
        # =========================
        nomes = [i["nome"] for i in ingredientes]

        nome = "Café da manhã"

        if bebidas:
            nome = bebidas[0]["nome"]

            if nomes:
                nome += " com " + " e ".join(nomes)

        elif nomes:
            nome = " + ".join(nomes)

        # =========================
        # 🍳 PREPARO
        # =========================
        modo_preparo = gerar_preparo_cafe(
            tipo,
            ingredientes=nomes,
            bebida=bebidas[0]["nome"] if bebidas else None
        )

        tempo = 5

        if tipo == "panqueca":
            tempo = 15
        elif tipo == "mingau":
            tempo = 10

        # =========================
        # 📦 RECEITA FINAL
        # =========================
        if not ingredientes and not bebidas:
            continue

        registrar_lista_consumo(ingredientes + bebidas, tracker)

        receitas.append({
            "nome": nome,
            "categoria": "cafe",
            "ingredientes": ingredientes + bebidas,
            "modo_preparo": modo_preparo,
            "tempo_preparo": f"{tempo} minutos",
            "Porcao": "1"
        })

        print("receitas:", len(receitas), flush=True)

    return receitas