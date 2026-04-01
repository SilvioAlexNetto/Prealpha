from app.backend.services.core.normalizacao import normalizar
import random

# =========================
# CONTROLE DE REPETIÇÃO
# =========================
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
    "fermentos": [],
    "produtoBruto": []
}

MAX_REPETICAO = 4


# =========================
# 🔥 SIMULAÇÃO BASE
# =========================
def simular_consumo(estoque, categoria, qtd, subcategoria=None, bloquear=False):

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

    usar = min(item["quantidade"], qtd)

    convertido = item_precisa_preparo(item)

    if convertido:
        item_convertido = preparar_item_bruto(item)
        quantidade_final = usar * 0.65
    else:
        item_convertido = item
        quantidade_final = usar

    resultado = {
        "ref": item,
        "nome": item_convertido["nome"],
        "quantidade": quantidade_final,
        "quantidade_original": usar,
        "unidade": item_convertido.get("unidade", item["unidade"]),
        "categorias": item_convertido.get("categorias", item.get("categorias", [])),
        "subcategorias": item_convertido.get("subcategorias", item.get("subcategorias", []))
    }


    return resultado


# =========================
# 🔥 COMMIT REAL
# =========================
def aplicar_consumo(item_simulado):
    if not item_simulado:
        print("💥 aplicar_consumo recebeu None")
        return

    if "ref" not in item_simulado:
        print("💥 ERRO: item sem ref", item_simulado)
        return

    item_real = item_simulado["ref"]
    item_real["quantidade"] -= item_simulado["quantidade_original"]

    # 🔥 CONTROLE DE REPETIÇÃO AGORA ACONTECE AQUI
    categorias = item_simulado.get("categorias", [])
    subcategorias = item_simulado.get("subcategorias", [])

    if not categorias:
        return

    categoria = categorias[0]
    subcategoria = subcategorias[0] if subcategorias else None

    chave = f"{categoria}_{subcategoria}" if subcategoria else categoria

    if chave not in ULTIMOS_USADOS:
        ULTIMOS_USADOS[chave] = []

    ULTIMOS_USADOS[chave].append(item_simulado["nome"])

    if len(ULTIMOS_USADOS[chave]) > MAX_REPETICAO:
        ULTIMOS_USADOS[chave].pop(0)

# =========================
# 🔥 CONSUMO LEGADO (EVITAR)
# =========================
def consumir(estoque, categoria, qtd, subcategoria=None, bloquear=False):
    simulado = simular_consumo(estoque, categoria, qtd, subcategoria, bloquear)

    if not simulado:
        return None

    aplicar_consumo(simulado)

    return {
        k: v for k, v in simulado.items()
        if k not in ["ref", "quantidade_original"]
    }


# =========================
# 🥛 LEITE (SIMULADO)
# =========================
def simular_leite(estoque, qtd=200):

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

    nome = item["nome"]
    nome_norm = normalizar(nome)

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

    simulado = {
        "ref": item,
        "nome": nome,
        "quantidade": usar,
        "quantidade_original": usar,
        "unidade": item["unidade"],
        "categorias": item["categorias"],
        "subcategorias": item.get("subcategorias", [])
    }

    return simulado, tipo


# =========================
# ☕ CAFÉ (SIMULADO)
# =========================
def eh_cafe_po(item):
    nome = normalizar(item["nome"])
    return "cafe" in nome and item["unidade"] == "g"


def simular_cafe(estoque, ml_desejado=200):

    cafes = [
        i for i in estoque
        if eh_cafe_po(i) and i["quantidade"] > 0
    ]

    if not cafes:
        return None

    item = random.choice(cafes)

    proporcao = 0.1
    g_necessario = ml_desejado * proporcao

    if item["quantidade"] < g_necessario:
        return None

    return {
        "ref": item,
        "nome": "café preparado",
        "quantidade": ml_desejado,
        "quantidade_original": g_necessario,
        "unidade": "ml",
        "categorias": ["bebida"],
        "subcategorias": ["cafe"]
    }


def simular_cafe_completo(estoque):

    cafe = simular_cafe(estoque, 200)
    if not cafe:
        return None, None, None

    leite, tipo_leite = simular_leite(estoque, 100)

    if leite and random.random() < 0.6:
        return {
            "nome": "café com leite",
            "quantidade": 200,
            "unidade": "ml",
            "categorias": ["bebida"],
            "subcategorias": ["cafe"]
        }, cafe, leite

    return {
        "nome": "café preto",
        "quantidade": 200,
        "unidade": "ml",
        "categorias": ["bebida"],
        "subcategorias": ["cafe"]
    }, cafe, None


# =========================
# ⚙️ PORCIONAMENTO
# =========================
def ajustar_porcionamento(item):
    if not item:
        return None

    unidade = item["unidade"]
    categorias = item.get("categorias", [])
    subcategorias = item.get("subcategorias", [])

    categoria = categorias[0] if categorias else None
    subcategoria = subcategorias[0] if subcategorias else None

    if subcategoria == "cafe":

        if categoria in ["proteina", "proteinaCF"]:
            item["quantidade"] = 2 if unidade == "unidade" else 80

        elif categoria in ["carbo", "carboCF"]:
            if unidade == "fatia":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 50
            elif unidade == "unidade":
                item["quantidade"] = 1

        elif categoria == "farinha":
            item["quantidade"] = 50

        elif categoria == "cereal":
            item["quantidade"] = 40

        elif categoria == "fruta":
            item["quantidade"] = 1 if unidade == "unidade" else 100

        elif categoria == "liquido":
            item["quantidade"] = 200

        elif categoria == "fermento":
            item["quantidade"] = 3

    return item


# =========================
# 🔥 CONVERSÃO BRUTO
# =========================
def item_precisa_preparo(item):
    nome = normalizar(item["nome"])
    return any(x in nome for x in [
        "inteiro", "inteira", "frango inteiro", "peixe inteiro"
    ])


def preparar_item_bruto(item):
    nome_original = item["nome"]
    nome = normalizar(nome_original)
    categorias = item.get("categorias", [])

    if "proteina" in categorias and ("inteiro" in nome or "inteira" in nome):

        nome_base = nome_original.lower()
        nome_base = nome_base.replace("inteiro", "").replace("inteira", "").strip()
        nome_base = nome_base.capitalize()

        return {
            "nome": f"{nome_base} em pedaços",
            "unidade": "g",
            "categorias": categorias,
            "subcategorias": item.get("subcategorias", [])
        }

    return item