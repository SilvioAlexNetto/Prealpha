import json
import random
import unicodedata
import os
from copy import deepcopy

from app.backend.services.bases import (
    proteinasUN, proteinasKG, legumes, carboidratos,
    folhas_saladas, massas, proteinas_proibidas_sopa,
    molhos, caldos, frutas, proteinasCF, carboidratosCF, liquidos, cereais, farinhas, fermentos
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

RECEITAS_PATH = os.path.join(BASE_DIR, "database", "BancoReceitas.json")
SOBRAS_PATH = os.path.join(BASE_DIR, "database", "Sobras.json")

ULTIMOS_USADOS = {
    "proteina": [],
    "carbo": [],
    "massa": [],
    "molho": [],
    "legume": [],
    "folha": [],
    "caldo": [],
    "proteinaCF": [],
    "carboCF": [],
    "fruta": [],
    "liquidos": [],
    "cereais": [],
    "farinhas": [],
    "fermentos": []
}

MAX_REPETICAO = 2

# =========================
# PROTEÍNA
# =========================
def preparo_proteina(nome):
    tecnica = tecnica_preparo()
    nome_lower = nome.lower()

    base_temp = random.choice([
        f"Tempere o {nome} com sal, alho e pimenta.",
        f"Tempere o {nome} com sal, limão e ervas.",
    ])

    if tecnica == "grelhado":
        preparo = f"Grelhe o {nome} até dourar bem."
    elif tecnica == "assado":
        preparo = f"Leve o {nome} ao forno até ficar bem assado."
    elif tecnica == "cozido":
        preparo = f"Cozinhe o {nome} em água temperada até ficar macio."
    elif tecnica == "selado":
        preparo = f"Sele o {nome} em fogo alto até formar crosta."
    else:
        preparo = f"Refogue o {nome} até dourar levemente."

    return [base_temp, preparo]


# =========================
# CARBO
# =========================
def preparo_carbo(nome):
    return [
        random.choice([
            f"Cozinhe o {nome} em água fervente com uma pitada de sal.",
            f"Leve o {nome} para cozinhar em água quente até ficar macio.",
        ]),
        random.choice([
            f"Escorra e reserve o {nome}.",
            f"Após o cozimento, deixe o {nome} descansar por alguns minutos.",
        ])
    ]


# =========================
# MASSA
# =========================
def preparo_massa(nome):
    return [
        random.choice([
            f"Cozinhe o {nome} em água fervente com sal até ficar al dente.",
            f"Leve o {nome} para cozinhar em bastante água até atingir o ponto ideal.",
        ]),
        random.choice([
            f"Escorra a água e reserve o {nome}.",
            f"Após o cozimento, escorra bem o {nome}.",
        ])
    ]


# =========================
# MOLHO
# =========================
def preparo_molho(nome):
    return [
        random.choice([
            f"Aqueça o {nome} em fogo baixo.",
            f"Leve o {nome} ao fogo até aquecer bem.",
        ]),
        random.choice([
            f"Misture bem até ficar homogêneo.",
            f"Ajuste o tempero do {nome} se necessário.",
        ])
    ]


# =========================
# LEGUME
# =========================
def preparo_legume(nome):
    return [
        random.choice([
            f"Corte o {nome} em pedaços médios.",
            f"Pique o {nome} em partes menores.",
        ]),
        random.choice([
            f"Refogue o {nome} até ficar macio.",
            f"Cozinhe o {nome} até atingir uma textura macia.",
        ])
    ]


# =========================
# FOLHA
# =========================
def preparo_folha(nome):
    return [
        random.choice([
            f"Lave bem a {nome}.",
            f"Higienize a {nome} em água corrente.",
        ]),
        random.choice([
            f"Sirva a {nome} fresca como acompanhamento.",
            f"Tempere a {nome} com azeite e sal a gosto.",
        ])
    ]


# =========================
# FINALIZAÇÃO
# =========================
def finalizar_prato():
    return [
        random.choice([
            "Monte o prato organizando os ingredientes.",
            "Disponha os ingredientes no prato de forma equilibrada.",
        ]),
        random.choice([
            "Sirva ainda quente.",
            "Finalize e sirva imediatamente.",
        ])
    ]

# =========================
# NORMALIZAÇÃO
# =========================
def normalizar(texto):
    return unicodedata.normalize("NFD", texto.lower()) \
        .encode("ascii", "ignore") \
        .decode("utf-8")


# =========================
# CLASSIFICAÇÃO DO ESTOQUE
# =========================
def classificar_estoque(estoque):
    estoque_classificado = []

    # =========================
    # DICIONÁRIOS DE CATEGORIAS (ordem = prioridade)
    # =========================
    categorias = [
        ("proteinaCF", proteinasCF, "cafe"),
        ("carboCF", carboidratosCF, "cafe"),
        ("liquido", liquidos, "cafe"),
        ("proteina", proteinasKG + proteinasUN, "ambos"),
        ("massa", massas, "ambos"),
        ("legume", legumes, "ambos"),
        ("carbo", carboidratos, "ambos"),
        ("folha", folhas_saladas, "ambos"),
        ("molho", molhos, "ambos"),
        ("fermento", fermentos, "ambos"),
        ("farinha", farinhas, "ambos"),
        ("cereal", cereais, "ambos"),
        ("caldo", [c["nome"] for c in caldos], "ambos"),
        ("fruta", frutas, "cafe")
    ]

    # =========================
    # PROCESSA CADA ITEM
    # =========================
    for item in estoque:
        nome_original = item["nome"]
        nome = normalizar(nome_original)
        categoria = None
        subcategoria = "ambos"

        # =========================
        # CHECA CATEGORIAS
        # =========================
        for cat, lista, sub in categorias:
            if any(normalizar(x) in nome for x in lista):
                categoria = cat
                subcategoria = sub
                break  # prioridade: primeira categoria que bater
        # =========================
        # FALLBACK
        # =========================
        if not categoria:
            if any(x in nome for x in ["arroz", "feijao", "batata"]):
                categoria = "carbo"
            elif any(x in nome for x in ["frango", "carne", "ovo"]):
                categoria = "proteina"
            elif any(x in nome for x in ["alface", "rucula"]):
                categoria = "folha"
            elif "molho" in nome:
                categoria = "molho"
            elif "caldo" in nome:
                categoria = "caldo"

        # =========================
        # NORMALIZA UNIDADES
        # =========================
        if categoria:
            unidade = str(item.get("unidade", "")).strip().lower()
            quantidade = float(item.get("quantidade", 0))

            if unidade in ["kg", "quilo", "quilos"]:
                quantidade *= 1000
                unidade = "g"
            elif unidade in ["g", "grama", "gramas"]:
                unidade = "g"
            elif unidade in ["l", "litro", "litros"]:
                quantidade *= 1000
                unidade = "ml"
            elif unidade in ["ml"]:
                unidade = "ml"
            elif unidade in ["un", "unidade", "unidades"]:
                unidade = "unidade"
            elif unidade in ["fatia", "fatias"]:
                unidade = "fatia"

            estoque_classificado.append({
                "nome": nome_original,
                "quantidade": quantidade,
                "unidade": unidade,
                "categoria": categoria,
                "subcategoria": subcategoria
            })

    return estoque_classificado


# =========================
# CONSUMO
# =========================
def consumir(estoque, categoria, qtd, subcategoria=None):
    candidatos = [
        i for i in estoque
        if i["categoria"] == categoria
        and i["quantidade"] > 0
        and (subcategoria is None or i.get("subcategoria") == subcategoria)
    ]

    # 🔒 NÃO faz fallback (corrige o bug)
    if not candidatos:
        return None

    # 🔥 evita repetição recente
    chave = categoria if subcategoria is None else f"{categoria}_{subcategoria}"

    if chave not in ULTIMOS_USADOS:
        ULTIMOS_USADOS[chave] = []

    filtrados = [
        i for i in candidatos
        if i["nome"] not in ULTIMOS_USADOS[chave]
    ]

    if filtrados:
        item = random.choice(filtrados)
    else:
        item = random.choice(candidatos)

    usar = min(item["quantidade"], qtd)
    item["quantidade"] -= usar

    # 🔥 histórico
    ULTIMOS_USADOS[chave].append(item["nome"])

    if len(ULTIMOS_USADOS[chave]) > MAX_REPETICAO:
        ULTIMOS_USADOS[chave].pop(0)

    return {
        "nome": item["nome"],
        "quantidade": usar,
        "unidade": item["unidade"],
        "categoria": item["categoria"],
        "subcategoria": item.get("subcategoria")
    }


# =========================
# VALIDAÇÃO
# =========================
def receita_valida(*args):
    return all(arg is not None for arg in args)

def tecnica_preparo():
    return random.choice([
        "grelhado",
        "assado",
        "cozido",
        "selado",
        "refogado"
    ])

# =========================
# 🍽️ PF - NÍVEL PROFISSIONAL
# =========================

def nome_prato_pf(proteina, carbo, legume=None, folha=None):
    tecnica = tecnica_preparo()

    descricoes_carbo = [
        f"{carbo} soltinho",
        f"{carbo} bem cozido",
        f"{carbo} leve e macio"
    ]

    descricoes_legume = [
        "legumes salteados",
        "legumes refogados",
        "mix de legumes"
    ]

    nome = f"{proteina} {tecnica} com {random.choice(descricoes_carbo)}"

    if legume:
        nome += f" e {random.choice(descricoes_legume)}"

    if folha:
        nome += f" acompanhado de salada de {folha}"

    return nome.capitalize()


def gerar_preparo_pf(proteina, carbo, legume=None, folha=None):
    preparo = []

    # 🔥 proteína
    preparo += preparo_proteina(proteina)

    # 🍚 carbo
    preparo += preparo_carbo(carbo)

    # 🥕 legume
    if legume:
        preparo += preparo_legume(legume)

    # 🥬 salada (mais realista)
    if folha:
        preparo += [
            random.choice([
                f"Lave bem a {folha} e deixe escorrer.",
                f"Higienize a {folha} em água corrente e seque.",
            ]),
            random.choice([
                f"Tempere a {folha} com azeite e sal a gosto.",
                f"Finalize a {folha} com um fio de azeite.",
            ])
        ]

    # 🍽️ finalização mais natural
    preparo += [
        random.choice([
            "Monte o prato distribuindo os ingredientes de forma equilibrada.",
            "Organize os ingredientes no prato para uma boa apresentação.",
        ]),
        random.choice([
            "Sirva ainda quente.",
            "Finalize e sirva imediatamente.",
        ])
    ]

    return preparo


def ajustar_porcionamento(item):
    unidade = item["unidade"]
    categoria = item["categoria"]
    subcategoria = item.get("subcategoria")

    # =========================
    # CAFÉ DA MANHÃ
    # =========================
    if subcategoria == "cafe":

        # 🥩 proteína café
        if categoria == "proteina":
            if unidade == "unidade":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 80

        # 🍞 carbo café
        elif categoria == "carbo":
            if unidade == "fatia":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 50
            elif unidade == "unidade":
                item["quantidade"] = 1

        # 🍎 fruta
        elif categoria == "fruta":
            if unidade == "unidade":
                item["quantidade"] = 1
            elif unidade == "g":
                item["quantidade"] = 100

        # 🥤 líquido (se você já criou a lista)
        elif categoria == "liquido":
            if unidade == "ml":
                item["quantidade"] = 200

    return item


# =========================
# CAFÉ
# =========================
# =========================
# 🍽️ CAFÉ - NOME PROFISSIONAL
# =========================
def nome_prato_cafe(base, proteina=None, fruta=None, recheio=None):
    """
    Gera um nome profissional para o café da manhã, similar ao almoço.
    """
    nome = base

    if proteina:
        nome += f" com {proteina}"

    if fruta:
        nome += f" e {fruta}"

    if recheio:
        nome += f" recheado com {recheio}"

    return nome.capitalize()


# =========================
# 🍽️ CAFÉ - MODO DE PREPARO PROFISSIONAL
# =========================
def gerar_preparo_cafe(base, proteina=None, liquido=None, fruta=None, recheio=None, fermento=None):
    """
    Gera uma lista de passos de preparo para o café da manhã, estilo profissional.
    """
    preparo = []

    # 🔹 Base (panqueca, mingau, crepioca)
    preparo.append(f"Prepare a base: {base}.")

    if liquido:
        preparo.append(f"Adicione {liquido} e misture bem até formar uma consistência homogênea.")

    if proteina:
        preparo.append(f"Incorpore {proteina} à mistura ou sirva ao lado, conforme apropriado.")

    if fermento:
        preparo.append(f"Adicione {fermento} para dar leveza à preparação.")

    if recheio:
        preparo.append(f"Recheie com {recheio} se desejar.")

    if fruta:
        preparo.append(f"Acompanhe com {fruta} fresca ou picada.")

    preparo.append("Cozinhe ou asse conforme necessário até atingir o ponto ideal.")
    preparo.append("Sirva imediatamente, ainda quente.")

    return preparo


def gerar_cafe(estoque):
    estoque = classificar_estoque(estoque)
    receitas = []
    tentativas = 0

    while len(receitas) < 31 and tentativas < 200:
        tentativas += 1
        receita = None
        tipo_prato = random.choice(["robusto", "simples"])

        if tipo_prato == "robusto":
            prato = random.choice(["Panqueca", "Mingau", "Crepioca"])

            farinha = consumir(estoque, "farinha", 50)
            liquido = consumir(estoque, "liquido", 100)
            proteina = consumir(estoque, "proteinaCF", 1, subcategoria="cafe")
            fruta = consumir(estoque, "fruta", 1)  # opcional
            fermento = consumir(estoque, "fermento", 5)  # opcional

            if not farinha or not liquido or not proteina:
                continue

            ingredientes = [farinha, liquido, proteina]
            if fruta:
                ingredientes.append(fruta)
            if fermento:
                ingredientes.append(fermento)

            nome = nome_prato_cafe(prato, proteina=proteina["nome"], fruta=fruta["nome"] if fruta else None, recheio=None)
            modo_preparo = gerar_preparo_cafe(prato, proteina=proteina["nome"], liquido=liquido["nome"],
                                              fruta=fruta["nome"] if fruta else None, fermento=fermento["nome"] if fermento else None)

            tempo = random.randint(10, 20)

            receita = {
                "nome": nome,
                "categoria": "cafe",
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": f"{tempo} minutos",
                "Porcao": "1"
            }

        else:  # simples
            carbo = consumir(estoque, "carboCF", 2, subcategoria="cafe")
            proteina = consumir(estoque, "proteinaCF", 1, subcategoria="cafe")
            liquido = consumir(estoque, "liquido", 200)
            fruta = consumir(estoque, "fruta", 1)

            if not carbo:
                continue

            ingredientes = [carbo]
            if proteina:
                ingredientes.append(proteina)
            if liquido:
                ingredientes.append(liquido)
            if fruta:
                ingredientes.append(fruta)

            nome = nome_prato_cafe(carbo["nome"], proteina=proteina["nome"] if proteina else None, fruta=fruta["nome"] if fruta else None)
            modo_preparo = gerar_preparo_cafe(carbo["nome"], proteina=proteina["nome"] if proteina else None,
                                              liquido=liquido["nome"] if liquido else None,
                                              fruta=fruta["nome"] if fruta else None)

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

# =========================
# ALMOÇO 
# =========================
def gerar_almoco(estoque):
    receitas = []

    tentativas = 0

    while len(receitas) < 31 and tentativas < 200:
        tentativas += 1

        tipo = random.choice(["pf", "massa"])

        # =========================
        # 🍽️ PF
        # =========================
        if tipo == "pf":
            proteina = consumir(estoque, "proteina", 120)
            carbo = consumir(estoque, "carbo", 100)

            if proteina and proteina.get("subcategoria") == "liquido":
                continue

            if not receita_valida(proteina, carbo):
                continue

            ingredientes = [proteina, carbo]

            legume = consumir(estoque, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque, "folha", 50)
            if folha:
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
            proteina = consumir(estoque_temp, "proteina", 100)

            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes = [massa, molho, proteina]

            legume = consumir(estoque_temp, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque_temp, "folha", 50)
            if folha:
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

    return receitas


def gerar_janta(estoque):
    receitas = []
    tentativas = 0

    while len(receitas) < 31 and tentativas < 200:
        tentativas += 1

        tipo = random.choice(["pf", "massa", "sopa"])

        # =========================
        # 🍽️ PF (REUTILIZA ALMOÇO)
        # =========================
        if tipo == "pf":
            proteina = consumir(estoque, "proteina", 120)
            carbo = consumir(estoque, "carbo", 100)

            if not receita_valida(proteina, carbo):
                continue

            ingredientes = [proteina, carbo]

            legume = consumir(estoque, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque, "folha", 50)
            if folha:
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
        # 🍝 MASSA (REUTILIZA ALMOÇO)
        # =========================
        elif tipo == "massa":
            estoque_temp = deepcopy(estoque)

            massa = consumir(estoque_temp, "massa", 100)
            molho = consumir(estoque_temp, "molho", 50)
            proteina = consumir(estoque_temp, "proteina", 100)

            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes = [massa, molho, proteina]

            legume = consumir(estoque_temp, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque_temp, "folha", 50)
            if folha:
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
        # 🍲 SOPA (UPGRADE REAL)
        # =========================
        else:
            proteina = consumir(estoque, "proteina", 80)
            caldo = consumir(estoque, "caldo", 500)
            legume1 = consumir(estoque, "legume", 80)
            legume2 = consumir(estoque, "legume", 80)

            if not receita_valida(proteina, caldo, legume1):
                continue

            if proteina["nome"] in proteinas_proibidas_sopa:
                continue

            ingredientes = [caldo, proteina, legume1]
            if legume2:
                ingredientes.append(legume2)

            # 🧠 nome mais realista
            nome = random.choice([
                f"Sopa caseira de {proteina['nome']} com legumes",
                f"Caldo nutritivo de {proteina['nome']} com vegetais",
                f"Sopa leve de {proteina['nome']} com legumes frescos"
            ])

            # 🔥 preparo realista
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


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def gerar_tudo(estoque_usuario):

    ULTIMOS_USADOS["proteina"] = []
    ULTIMOS_USADOS["carbo"] = []

    estoque_copia = deepcopy(estoque_usuario)

    estoque_classificado = classificar_estoque(estoque_copia)

    cafe = gerar_cafe(estoque_classificado)
    almoco = gerar_almoco(estoque_classificado)
    janta = gerar_janta(estoque_classificado)

    todas_receitas = cafe + almoco + janta

    with open(RECEITAS_PATH, "w", encoding="utf-8") as f:
        json.dump(todas_receitas, f, ensure_ascii=False, indent=4)

    sobras = [i for i in estoque_classificado if i["quantidade"] > 0]

    with open(SOBRAS_PATH, "w", encoding="utf-8") as f:
        json.dump(sobras, f, ensure_ascii=False, indent=4)

    return {
        "total_receitas": len(todas_receitas),
        "sobras": sobras
    }