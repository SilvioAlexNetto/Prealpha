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

MAX_REPETICAO = 4

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
        ("farinha", farinhas, "cafe"),
        ("cereal", cereais, "cafe"),
        ("caldo", [c["nome"] for c in caldos], "ambos"),
        ("fruta", frutas, "cafe")
    ]

    for item in estoque:
        nome_original = item["nome"]
        nome = normalizar(nome_original)

        categorias_encontradas = []
        subcategorias_encontradas = []

        for cat, lista, sub in categorias:
            if any(normalizar(x) in nome for x in lista):
                categorias_encontradas.append(cat)
                subcategorias_encontradas.append(sub)

        # fallback inteligente
        if not categorias_encontradas:
            if any(x in nome for x in ["arroz", "feijao", "batata"]):
                categorias_encontradas.append("carbo")
            elif any(x in nome for x in ["frango", "carne", "ovo"]):
                categorias_encontradas.append("proteina")
            elif "leite" in nome:
                categorias_encontradas.append("liquido")

        if categorias_encontradas:
            unidade = str(item.get("unidade", "")).strip().lower()
            quantidade = float(item.get("quantidade", 0))

            if unidade in ["kg", "quilo", "quilos"]:
                quantidade *= 1000
                unidade = "g"
            elif unidade in ["l", "litro", "litros"]:
                quantidade *= 1000
                unidade = "ml"
            elif unidade in ["un", "unidade", "unidades"]:
                unidade = "unidade"
            elif unidade in ["fatia", "fatias"]:
                unidade = "fatia"

            estoque_classificado.append({
                "nome": nome_original,
                "quantidade": quantidade,
                "unidade": unidade,
                "categorias": categorias_encontradas,
                "subcategorias": subcategorias_encontradas
            })

    return estoque_classificado

# =========================
# CONSUMO
# =========================
def consumir(estoque, categoria, qtd, subcategoria=None, bloquear=False):

    candidatos = [
        i for i in estoque
        if categoria in i["categorias"]
        and i["quantidade"] > 0
        and (subcategoria is None or subcategoria in i.get("subcategorias", []))
        and (
            not bloquear or
            (
                "cereal" not in i["categorias"] and
                "farinha" not in i["categorias"]
            )
        )
    ]

    if not candidatos and bloquear:
        candidatos = [
            i for i in estoque
            if categoria in i["categorias"]
            and i["quantidade"] > 0
            and (subcategoria is None or subcategoria in i.get("subcategorias", []))
        ]

    if not candidatos:
        return None

    chave = f"{categoria}_{subcategoria}" if subcategoria else categoria

    if chave not in ULTIMOS_USADOS:
        ULTIMOS_USADOS[chave] = []

    filtrados = [
        i for i in candidatos
        if i["nome"] not in ULTIMOS_USADOS[chave]
    ]

    item = random.choice(filtrados or candidatos)

    # 🔥 CONVERSÃO (ANTES do consumo lógico)
    convertido = item_precisa_preparo(item)

    if convertido:
        item_convertido = preparar_item_bruto(item)
    else:
        item_convertido = item

    # 🔥 CONSUMO REAL (sempre do item original)
    usar = min(item["quantidade"], qtd)
    item["quantidade"] -= usar

    # 🔥 QUANTIDADE FINAL (ajustada se houve conversão)
    if convertido:
        quantidade_final = usar * 0.65
    else:
        quantidade_final = usar

    # 🔥 MONTA RESULTADO (IMPORTANTE: NOVO OBJETO)
    resultado = {
        "nome": item_convertido["nome"],
        "quantidade": quantidade_final,
        "unidade": item_convertido.get("unidade", item["unidade"]),
        "categorias": item_convertido.get("categorias", item.get("categorias", [])),
        "subcategorias": item_convertido.get("subcategorias", item.get("subcategorias", []))
    }

    ULTIMOS_USADOS[chave].append(resultado["nome"])

    if len(ULTIMOS_USADOS[chave]) > MAX_REPETICAO:
        ULTIMOS_USADOS[chave].pop(0)

    return resultado

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

def item_precisa_preparo(item):
    nome = normalizar(item["nome"])

    return any(x in nome for x in [
        "inteiro", "inteira", "frango inteiro", "peixe inteiro"
    ])

def preparar_item_bruto(item):
    nome = normalizar(item["nome"])
    categorias = item.get("categorias", [])

    if "inteiro" or "inteira" in nome and "proteina" in categorias:
        nome_base = item["nome"].replace("inteiro", "").strip()

        return {
            "nome": f"{nome_base} em pedaços",
            "unidade": "g",
            "categorias": categorias,
            "subcategorias": item.get("subcategorias", [])
        }

    return item

def eh_cafe_po(item):
    nome = normalizar(item["nome"])
    return "cafe" in nome and item["unidade"] == "g"

def preparar_cafe(item, ml_desejado=200):
    # proporção média: 10g → 100ml
    proporcao = 0.1

    g_necessario = ml_desejado * proporcao

    if item["quantidade"] < g_necessario:
        return None

    item["quantidade"] -= g_necessario

    return {
        "nome": "café preparado",
        "quantidade": ml_desejado,
        "unidade": "ml"
    }

def ajustar_porcionamento(item):
    if not item:
        return None

    unidade = item["unidade"]

    categorias = item.get("categorias", [])
    subcategorias = item.get("subcategorias", [])

    categoria = categorias[0] if categorias else None
    subcategoria = subcategorias[0] if subcategorias else None

    if subcategoria == "cafe":

        # 🥩 proteína café
        if categoria in ["proteina", "proteinaCF"]:
            if unidade == "unidade":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 80

        # 🍞 carbo café
        elif categoria in ["carbo", "carboCF"]:
            if unidade == "fatia":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 50
            elif unidade == "unidade":
                item["quantidade"] = 1

        # 🌾 farinha
        elif categoria == "farinha":
            if unidade == "g":
                item["quantidade"] = 50

        # 🥣 cereal
        elif categoria == "cereal":
            if unidade == "g":
                item["quantidade"] = 40

        # 🍎 fruta
        elif categoria == "fruta":
            if unidade == "unidade":
                item["quantidade"] = 1
            elif unidade == "g":
                item["quantidade"] = 100

        # 🥤 líquido
        elif categoria == "liquido":
            if unidade == "ml":
                item["quantidade"] = 200

        # 🧪 fermento
        elif categoria == "fermento":
            if unidade == "g":
                item["quantidade"] = 3

    return item

# =========================
# CAFÉ
# =========================
# =========================
# 🍽️ CAFÉ - NOME PROFISSIONAL
# =========================

def nome_prato_cafe(base, proteina=None, fruta=None, recheio=None):

    base_lower = base.lower()
    nome = base

    # 🔥 só usa recheio quando faz sentido
    usa_recheio = base_lower in ["panqueca", "crepioca"]

    if usa_recheio and recheio:
        nome += f" com recheio de {recheio}"

        if proteina:
            nome += f" e {proteina}"

    else:
        if proteina:
            nome += f" com {proteina}"

        if fruta:
            nome += f" e {fruta}"

    return nome.capitalize()
# =========================
# 🍽️ CAFÉ - MODO DE PREPARO PROFISSIONAL
# =========================
def gerar_preparo_cafe(base, proteina=None, liquido=None, fruta=None, recheio=None, fermento=None):
    preparo = []
    base_lower = base.lower()

    def escolher(opcoes):
        return random.choice(opcoes)

    # =========================
    # 🔹 PANQUECA
    # =========================
    if "panqueca" in base_lower:
        preparo.append(escolher([
            f"Em uma tigela, misture os ingredientes com {liquido} e {proteina}.",
            f"Combine a base com {liquido} e {proteina} até formar uma massa.",
        ]))

        if fermento:
            preparo.append(escolher([
                f"Adicione {fermento} e misture delicadamente.",
                f"Incorpore {fermento} para deixar a massa mais leve.",
            ]))

        preparo.append(escolher([
            "Mexa até obter uma massa lisa e homogênea.",
            "Misture bem até a massa ficar uniforme.",
        ]))

        preparo.append(escolher([
            "Aqueça uma frigideira antiaderente em fogo médio.",
            "Leve uma frigideira ao fogo médio e unte levemente se necessário.",
        ]))

        preparo.append(escolher([
            "Despeje pequenas porções da massa e cozinhe até formar bolhas.",
            "Coloque porções da massa na frigideira e aguarde dourar a base.",
        ]))

        preparo.append(escolher([
            "Vire e doure o outro lado.",
            "Vire a panqueca e deixe dourar levemente.",
        ]))

        if recheio:
            preparo.append(escolher([
                f"Recheie com {recheio} antes de servir.",
                f"Finalize com recheio de {recheio}.",
            ]))

        if fruta:
            preparo.append(escolher([
                f"Sirva com {fruta} por cima.",
                f"Acompanhe com {fruta}.",
            ]))

        preparo.append(escolher([
            "Sirva ainda quente.",
            "Finalize e sirva na sequência.",
        ]))

    # =========================
    # 🔹 CREPIOCA
    # =========================
    elif "crepioca" in base_lower:
        preparo.append(escolher([
            f"Misture a base com {proteina} até formar uma massa homogênea.",
            f"Em uma tigela, combine os ingredientes com {proteina}.",
        ]))

        if liquido:
            preparo.append(escolher([
                f"Adicione {liquido} aos poucos para ajustar a textura.",
                f"Se necessário, acrescente {liquido} para deixar a massa mais leve.",
            ]))

        preparo.append(escolher([
            "Misture bem até ficar uniforme.",
            "Mexa até obter uma massa lisa.",
        ]))

        preparo.append(escolher([
            "Aqueça uma frigideira antiaderente.",
            "Leve uma frigideira ao fogo médio.",
        ]))

        preparo.append(escolher([
            "Espalhe a massa formando uma camada fina.",
            "Despeje a massa e espalhe bem pela superfície.",
        ]))

        preparo.append(escolher([
            "Cozinhe até firmar e vire para dourar o outro lado.",
            "Quando firmar, vire e deixe dourar levemente.",
        ]))

        if recheio:
            preparo.append(escolher([
                f"Adicione {recheio} antes de dobrar.",
                f"Recheie com {recheio} e feche ao meio.",
            ]))

        if fruta:
            preparo.append(escolher([
                f"Sirva com {fruta}.",
                f"Acompanhe com {fruta}.",
            ]))

        preparo.append(escolher([
            "Sirva na sequência.",
            "Finalize e sirva quente.",
        ]))

    # =========================
    # 🔹 MINGAU
    # =========================
    elif "mingau" in base_lower:
        preparo.append(escolher([
            f"Aqueça {liquido} em fogo médio.",
            f"Leve {liquido} ao fogo até começar a aquecer.",
        ]))

        preparo.append(escolher([
            "Adicione a base aos poucos, mexendo sempre.",
            "Incorpore a base gradualmente, mexendo sem parar.",
        ]))

        preparo.append(escolher([
            "Cozinhe até engrossar e ficar cremoso.",
            "Mexa até atingir uma textura cremosa.",
        ]))

        if fruta:
            preparo.append(escolher([
                f"Finalize com {fruta} por cima.",
                f"Sirva com {fruta}.",
            ]))

        if proteina:
            preparo.append(escolher([
                f"Acompanhe com {proteina}.",
                f"Sirva junto com {proteina}.",
            ]))

        preparo.append(escolher([
            "Sirva quente.",
            "Finalize e sirva imediatamente.",
        ]))

    # =========================
    # 🔹 VITAMINA (NOVO 🔥)
    # =========================
    elif "vitamina" in base_lower:
        preparo.append(escolher([
            f"Adicione {liquido} no liquidificador.",
            f"Coloque {liquido} no liquidificador.",
        ]))

        if fruta:
            preparo.append(escolher([
                f"Acrescente {fruta}.",
                f"Adicione {fruta} ao liquidificador.",
            ]))

        preparo.append(escolher([
            "Bata até obter uma mistura homogênea.",
            "Bata bem até ficar cremoso.",
        ]))

        preparo.append(escolher([
            "Sirva gelado.",
            "Sirva imediatamente após o preparo.",
        ]))

    # =========================
    # 🔹 SIMPLES
    # =========================
    elif "simples" in base_lower:
        preparo.append(escolher([
            "Organize os ingredientes em um prato ou tigela.",
            "Disponha os ingredientes de forma prática para consumo.",
        ]))

        if proteina:
            preparo.append(escolher([
                f"Separe {proteina} para acompanhar.",
                f"Inclua {proteina} como acompanhamento.",
            ]))

        if fruta:
            preparo.append(escolher([
                f"Corte {fruta} e adicione ao prato.",
                f"Adicione {fruta} já cortada.",
            ]))

        if liquido:
            preparo.append(escolher([
                f"Sirva com {liquido}.",
                f"Acompanhe com {liquido}.",
            ]))

        preparo.append(escolher([
            "Finalize e sirva.",
            "Pronto para consumo.",
        ]))

    # =========================
    # 🔹 FALLBACK
    # =========================
    else:
        preparo.append(f"Prepare {base}.")
        if fruta:
            preparo.append(f"Sirva com {fruta}.")
        preparo.append("Finalize e sirva.")

    return [p for p in preparo if p]

def combinar_partes_nome(base, extras):
    """
    Combina partes do nome evitando repetição de conectores
    e repetição de ingredientes no nome.
    """
    partes = [base]

    conectores = ["com", "e", "acompanhado de"]

    usados = set()
    extras_unicos = []

    # 🔥 remove duplicados mantendo ordem
    vistos = set()
    for extra in extras:
        if extra and extra not in vistos:
            extras_unicos.append(extra)
            vistos.add(extra)

    for extra in extras_unicos:
        conector = random.choice(conectores)

        # evita repetir conector
        tentativas = 0
        while conector in usados and tentativas < 5:
            conector = random.choice(conectores)
            tentativas += 1

        usados.add(conector)
        partes.append(f"{conector} {extra}")

    return " ".join(partes)

def eh_farinha(item):
    return item and "farinha" in normalizar(item["nome"])

def consumir_leite(estoque, qtd=200):
    candidatos = [
        i for i in estoque
        if "liquido" in i["categorias"]
        and "leite" in normalizar(i["nome"])
        and i["quantidade"] > 0
    ]

    if not candidatos:
        return None, None

    item = random.choice(candidatos)

    usar = min(item["quantidade"], qtd)
    item["quantidade"] -= usar

    nome = item["nome"]
    nome_norm = normalizar(nome)

    # 🔍 detecta tipo de leite
    if "amendoa" in nome_norm:
        tipo = "leite de amêndoas"
    elif "soja" in nome_norm:
        tipo = "leite de soja"
    elif "aveia" in nome_norm:
        tipo = "leite de aveia"
    elif "coco" in nome_norm:
        tipo = "leite de coco"
    elif "desnatado" in nome_norm:
        tipo = "leite desnatado"
    elif "integral" in nome_norm:
        tipo = "leite integral"
    else:
        tipo = "leite"

    return {
        "nome": nome,
        "quantidade": usar,
        "unidade": item["unidade"]
    }, tipo

def agrupar_ingredientes(lista):
    agrupado = {}

    for item in lista:
        chave = (item["nome"], item["unidade"])

        if chave not in agrupado:
            agrupado[chave] = item.copy()
        else:
            agrupado[chave]["quantidade"] += item["quantidade"]

    return list(agrupado.values())

def consolidar_ingredientes(ingredientes):
    """
    Agrupa ingredientes iguais (mesmo nome + unidade)
    somando suas quantidades.
    """

    mapa = {}

    for item in ingredientes:
        if not item:
            continue

        chave = (item["nome"], item["unidade"])

        if chave not in mapa:
            mapa[chave] = item.copy()
        else:
            mapa[chave]["quantidade"] += item["quantidade"]

    return list(mapa.values())

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
            # 🥤 VITAMINA (NOVO)
            # =========================
            if prato == "Vitamina":

                liquido, tipo_leite = consumir_leite(estoque, 200)

                if not liquido:
                    continue

                fruta1 = consumir(estoque, "fruta", 1)
                fruta2 = consumir(estoque, "fruta", 1)
                fruta3 = consumir(estoque, "fruta", 1)
                cereal = consumir(estoque, "cereal", 30)

                if not fruta1:
                    continue

                ingredientes = [liquido, fruta1]

                tipo_vitamina = random.choice(["basica", "nutritiva", "fortificada"])

                if tipo_vitamina == "basica":
                    frutas_usadas = [fruta1]

                elif tipo_vitamina == "nutritiva":
                    if fruta2:
                        ingredientes.append(fruta2)
                    if fruta3:
                        ingredientes.append(fruta3)
                    if cereal:
                        ingredientes.append(cereal)

                    frutas_usadas = [f for f in [fruta1, fruta2, fruta3] if f]

                else:
                    if fruta2:
                        ingredientes.append(fruta2)
                    if fruta3 and random.random() < 0.5:
                        ingredientes.append(fruta3)

                    frutas_usadas = [f for f in [fruta1, fruta2, fruta3] if f]

                # 🔥 porcionamento
                ingredientes = [ajustar_porcionamento(i) for i in ingredientes if i]

                # 🔥 consolidação
                ingredientes = consolidar_ingredientes(ingredientes)

                # 🔥 nomes REAIS (baseado no resultado final)
                nomes_frutas = [
                    i["nome"] for i in ingredientes
                    if "fruta" in i.get("categorias", []) or "fruta" in i.get("subcategorias", [])
                ]

                # 🔥 remove duplicados mantendo ordem
                nomes_frutas_unicos = list(dict.fromkeys(nomes_frutas))

                # 🔥 nome final LIMPO
                nome = f"Vitamina de {' e '.join(nomes_frutas_unicos)} com {tipo_leite}"

                modo_preparo = [
                    f"Adicione {' e '.join(nomes_frutas_unicos)} no liquidificador.",
                    f"Acrescente {tipo_leite}.",
                    "Bata até obter uma mistura homogênea.",
                    "Sirva gelado."
                ]

                tempo = 5

            # =========================
            # 🍽️ OUTROS ROBUSTOS (INALTERADO)
            # =========================
            else:
                if prato in ["Panqueca", "Crepioca"]:
                    base_item = consumir(estoque, "farinha", 50)
                else:
                    base_item = consumir(estoque, "cereal", 50) or consumir(estoque, "farinha", 50)

                liquido = consumir(estoque, "liquido", 100)
                proteina = consumir(estoque, "proteinaCF", 1, subcategoria="cafe")
                fruta = consumir(estoque, "fruta", 1)
                fermento = consumir(estoque, "fermento", 5) if prato == "Panqueca" else None

                if not base_item or not liquido or not proteina:
                    continue

                ingredientes = [base_item, liquido, proteina]

                if fruta:
                    ingredientes.append(fruta)
                if fermento:
                    ingredientes.append(fermento)

                ingredientes = [ajustar_porcionamento(i) for i in ingredientes if i]

                usa_recheio = prato in ["Panqueca", "Crepioca"]

                nomes_ingredientes = [i["nome"] for i in ingredientes]
                tem_fruta = fruta if fruta and fruta["nome"] in nomes_ingredientes else None

                nome = nome_prato_cafe(
                    prato,
                    proteina=proteina["nome"],
                    fruta=None if usa_recheio else (tem_fruta["nome"] if tem_fruta else None),
                    recheio=tem_fruta["nome"] if usa_recheio and tem_fruta else None
                )

                modo_preparo = gerar_preparo_cafe(
                    prato,
                    proteina=proteina["nome"],
                    liquido=liquido["nome"],
                    fruta=None if usa_recheio else (tem_fruta["nome"] if tem_fruta else None),
                    recheio=tem_fruta["nome"] if usa_recheio and tem_fruta else None,
                )

                tempo = random.randint(10, 20)

        # =========================
        # 🔹 SIMPLES
        # =========================
        else:
            carbo = consumir(estoque, "carboCF", 2, subcategoria="cafe")
            proteina = consumir(estoque, "proteinaCF", 1, subcategoria="cafe")
            liquido = consumir(estoque, "liquido", 200)
            fruta = consumir(estoque, "fruta", 1)

            if not carbo or eh_farinha(carbo):
                continue

            ingredientes = [carbo]
            adicionou_algo = False

            # 🥣 CEREAL
            if "cereal" in normalizar(carbo["nome"]):

                if proteina and random.random() < 0.5:
                    ingredientes.append(proteina)

                if fruta and random.random() < 0.7:
                    ingredientes.append(fruta)
                    adicionou_algo = True

                if liquido and random.random() < 0.7:
                    ingredientes.append(liquido)
                    adicionou_algo = True

                if not adicionou_algo:
                    if fruta:
                        ingredientes.append(fruta)
                    elif liquido:
                        ingredientes.append(liquido)

            # 🍞 NÃO CEREAL
            else:
                if proteina:
                    ingredientes.append(proteina)

                if fruta and random.random() < 0.6:
                    ingredientes.append(fruta)

                if liquido and random.random() < 0.4:
                    ingredientes.append(liquido)

            ingredientes = [ajustar_porcionamento(i) for i in ingredientes if i]

            nomes_ingredientes = [i["nome"] for i in ingredientes]

            tem_proteina = proteina["nome"] if proteina and proteina["nome"] in nomes_ingredientes else None
            tem_fruta = fruta["nome"] if fruta and fruta["nome"] in nomes_ingredientes else None

            nome = nome_prato_cafe(
                carbo["nome"],
                proteina=tem_proteina,
                fruta=tem_fruta
            )

            modo_preparo = gerar_preparo_cafe(
                "simples",
                proteina=tem_proteina,
                liquido=liquido["nome"] if liquido else None,
                fruta=tem_fruta
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

    return receitas


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