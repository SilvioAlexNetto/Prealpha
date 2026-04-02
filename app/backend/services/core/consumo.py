from app.backend.services.core.normalizacao import normalizar
import random

ULTIMOS_USADOS = {}
MAX_REPETICAO = 4


def simular_consumo(estoque, categoria, qtd, subcategoria=None, bloquear=False):

    candidatos = [
        i for i in estoque
        if categoria in i["categorias"]
        and i["quantidade"] > 0
        and (subcategoria is None or subcategoria in i.get("subcategorias", []))
    ]

    if not candidatos:
        return None

    item = random.choice(candidatos)

    usar = min(item["quantidade"], qtd)

    return {
        "ref": item,
        "nome": item["nome"],
        "quantidade": usar,
        "quantidade_original": usar,
        "unidade": item["unidade"],
        "categorias": item.get("categorias", []),
        "subcategorias": item.get("subcategorias", [])
    }


def aplicar_consumo(item_simulado):
    if not item_simulado:
        return

    if "ref" not in item_simulado:
        return

    item_real = item_simulado["ref"]

    # 🔥 PROTEÇÃO: evita consumo negativo
    if item_real["quantidade"] < item_simulado["quantidade_original"]:
        return

    item_real["quantidade"] -= item_simulado["quantidade_original"]

    # 🔥 CONTROLE DE REPETIÇÃO AQUI (correto)
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
# 🥛 LEITE
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

    return {
        "ref": item,
        "nome": item["nome"],
        "quantidade": usar,
        "quantidade_original": usar,
        "unidade": item["unidade"],
        "categorias": item["categorias"],
        "subcategorias": item.get("subcategorias", [])
    }, "leite"


# =========================
# ⚙️ PORCIONAMENTO
# =========================
def ajustar_porcionamento(item):
    if not item:
        return None

    if item["unidade"] == "unidade":
        item["quantidade"] = 1
    elif item["unidade"] == "g":
        item["quantidade"] = min(item["quantidade"], 100)

    return item