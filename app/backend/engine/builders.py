import random

from app.backend.engine.core import (
    escolher_proteina,
    escolher_carbo_compativel,
    escolher_proteina_sopa,
    adicionar_salada,
    vegetais,
    massas,
    molhos,
    caldos,
    folhas_saladas
)

from app.backend.engine.rules import (
    preparar_proteina,
    metodo_para_nome,
    definir_caldo
)

def montar_consumo(lista_ingredientes):
    return [
        {
            "nome": item["nome"],
            "quantidade": item["quantidade"],
            "unidade": item["unidade"]
        }
        for item in lista_ingredientes
    ]

def gerar_pf():
    proteina = escolher_proteina()
    carbo = escolher_carbo_compativel(proteina["nome"])
    veg1, veg2 = random.sample(vegetais, 2)

    prep = preparar_proteina(proteina["nome"])
    metodo = metodo_para_nome(prep["metodo"])

    tem_salada = adicionar_salada()

    ingredientes = [
        {
            "nome": proteina["nome"],
            "quantidade": proteina["quantidade"],
            "unidade": proteina["unidade"]
        },
        {
            "nome": carbo,
            "quantidade": 90,
            "unidade": "g"
        },
        {
            "nome": veg1,
            "quantidade": 80,
            "unidade": "g"
        },
        {
            "nome": veg2,
            "quantidade": 80,
            "unidade": "g"
        }
    ]

    modo = [
        f"1. Tempere a {proteina['nome'].lower()} com sal e temperos naturais a gosto.",
        f"2. Em uma frigideira, aqueça um fio de azeite ou óleo e {prep['texto'].lower()}",
        f"3. Em uma panela, cozinhe o {carbo.lower()} em água com uma pitada de sal até ficar macio. Escorra e reserve.",
        f"4. Prepare {veg1.lower()} cozinhando no vapor ou salteando levemente até ficar macio.",
        f"5. Prepare {veg2.lower()} da mesma forma, mantendo leve crocância.",
        "6. Monte o prato distribuindo o carboidrato como base.",
        f"7. Adicione a {proteina['nome'].lower()} preparada por cima.",
        f"8. Acrescente {veg1.lower()} e {veg2.lower()} ao lado ou sobre o prato."
    ]

    nome = f"{proteina['nome']} {metodo} com {carbo} e legumes"

    # 🔥 SALADA OPCIONAL (NÃO QUEBRA FLUXO)
    if tem_salada:
        salada = gerar_salada()
        ingredientes.extend(salada["ingredientes"])

        modo.append(f"9. {salada['descricao']}")
        nome += " com salada"

        modo.extend([
            "10. Finalize com um fio de azeite ou ervas frescas, se desejar.",
            "11. Sirva quente."
        ])

    # 🔥 RETURN FORA DO IF (CORRETO)
    return {
        "nome": nome,
        "tipo": "pf",
        "categoria": "almoco",

        "ingredientes": ingredientes,

        "consumo_estoque": montar_consumo(ingredientes),

        "modo_preparo": modo,
        "tempo_preparo": f"{random.randint(25, 50)} min",
        "Porcao": "1"
    }


# =========================
# MASSA (PRATO ÚNICO)
# =========================

def gerar_massa():

    massa = random.choice(massas)
    proteina = escolher_proteina()
    legumes = random.sample(vegetais, 2)
    molho = random.choice(molhos)

    ingredientes = [
        {
            "nome": massa,
            "quantidade": 100,
            "unidade": "g"
        },
        {
            "nome": proteina["nome"],
            "quantidade": proteina["quantidade"],
            "unidade": proteina["unidade"]
        },
        {
            "nome": molho,
            "quantidade": 150,
            "unidade": "ml"
        },
        {
            "nome": legumes[0],
            "quantidade": 70,
            "unidade": "g"
        },
        {
            "nome": legumes[1],
            "quantidade": 70,
            "unidade": "g"
        }
    ]

    return {
        "nome": f"{massa} com {proteina['nome'].lower()} e legumes",
        "tipo": "massa",
        "categoria": "prato único",

        "ingredientes": ingredientes,

        # 🔥 ESTOQUE REAL (fonte única sincronizada)
        "consumo_estoque": montar_consumo(ingredientes),

        "modo_preparo": [
            f"1. Em uma panela com água fervente e uma pitada de sal, cozinhe o {massa.lower()} até ficar al dente (cerca de 8 a 12 minutos). Escorra e reserve.",

            f"2. Tempere a {proteina['nome'].lower()} com sal e temperos a gosto.",

            f"3. Em uma frigideira, aqueça um fio de azeite ou óleo e prepare a {proteina['nome'].lower()} até dourar ou atingir o ponto desejado. Reserve.",

            f"4. Na mesma panela ou frigideira, adicione o {molho.lower()} e aqueça em fogo médio até começar a engrossar.",

            f"5. Acrescente a proteína ao molho e misture bem para incorporar os sabores.",

            f"6. Cozinhe {legumes[0].lower()} e {legumes[1].lower()} rapidamente para manter a textura.",

            f"7. Misture o {massa.lower()} já cozido ao molho com a proteína.",

            f"8. Adicione os legumes e misture delicadamente.",

            "9. Ajuste o sal e finalize com um fio de azeite ou ervas frescas, se desejar.",

            "10. Sirva quente."
        ],

        "tempo_preparo": f"{random.randint(20, 40)} min",
        "Porcao": "1"
    }


# =========================
# SOPA (PRATO ÚNICO)
# =========================

def gerar_sopa():

    proteina = escolher_proteina_sopa()
    legumes = random.sample(vegetais, 3)
    caldo_escolhido = definir_caldo(random.choice(caldos))

    legume_base = legumes[0]
    legume_textura = legumes[1]
    legume_final = legumes[2]

    ingredientes = [
        {
            "nome": proteina["nome"],
            "quantidade": proteina["quantidade"],
            "unidade": proteina["unidade"]
        },
        {
            "nome": legume_base,
            "quantidade": 2,
            "unidade": "unidade"
        },
        {
            "nome": legume_textura,
            "quantidade": 1,
            "unidade": "unidade"
        },
        {
            "nome": legume_final,
            "quantidade": 80,
            "unidade": "g"
        },
        caldo_escolhido
    ]

    return {
        "nome": f"Sopa de {proteina['nome'].lower()} com legumes",
        "tipo": "sopa",
        "categoria": "prato único",

        "ingredientes": ingredientes,

        # 🔥 ESTOQUE REAL
        "consumo_estoque": montar_consumo(ingredientes),

        "modo_preparo": [
            f"Cozinhe a {proteina['nome'].lower()} até ficar macia e desfie.",

            f"Corte os legumes em pedaços pequenos.",

            f"Cozinhe {legume_base} até ficar bem macio e reserve parte para bater.",

            f"Bata o {legume_base} com o {caldo_escolhido['nome'].lower()} no liquidificador até formar um creme.",

            "Refogue alho e cebola até dourar levemente.",

            f"Adicione a proteína desfiada ao refogado.",

            f"Incorpore o creme e adicione os legumes restantes.",

            "Cozinhe em fogo baixo até tudo ficar bem incorporado.",

            "Ajuste o sal e finalize com cheiro-verde.",

            "Sirva quente."
        ],

        "tempo_preparo": f"{random.randint(35, 60)} min",
        "Porcao": "1"
    }


# =========================
# SALADA
# =========================
def gerar_salada():

    folhas = random.sample(folhas_saladas, 2)

    ingredientes = [
        {"nome": folhas[0], "quantidade": 50, "unidade": "g"},
        {"nome": folhas[1], "quantidade": 50, "unidade": "g"}
    ]

    return {
        "tipo": "salada",

        "ingredientes": ingredientes,

        # 🔥 IMPORTANTE: estoque também será abatido
        "consumo_estoque": montar_consumo(ingredientes),

        "descricao": f"Sirva com salada de {folhas[0].lower()} e {folhas[1].lower()}."
    }