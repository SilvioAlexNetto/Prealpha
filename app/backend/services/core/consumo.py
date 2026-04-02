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
    if not item_simulado or "ref" not in item_simulado:
        return

    item_real = item_simulado["ref"]
    item_real["quantidade"] -= item_simulado["quantidade_original"]

    # proteção contra negativo
    if item_real["quantidade"] < 0:
        item_real["quantidade"] = 0


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