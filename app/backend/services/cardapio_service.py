import os
import json
import unicodedata

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RECEITAS_PATH = os.path.join(BASE_DIR, "database", "BancoReceitas.json")


# =========================
# NORMALIZAÇÃO
# =========================
def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


def normalizar(texto):
    return remover_acentos(texto.strip().lower())


# =========================
# CARREGAR RECEITAS
# =========================
def carregar_receitas():
    if not os.path.exists(RECEITAS_PATH):
        raise FileNotFoundError("Banco de receitas não encontrado")

    with open(RECEITAS_PATH, "r", encoding="utf-8") as f:
        receitas = json.load(f)

    for r in receitas:
        r["categoria"] = normalizar(r["categoria"])

        for ing in r.get("ingredientes", []):
            ing["nome"] = normalizar(ing["nome"])
            ing["unidade"] = normalizar(ing["unidade"])

    return receitas


# =========================
# LISTAR INGREDIENTES
# =========================
def listar_ingredientes_e_unidades():
    receitas = carregar_receitas()

    ingredientes = set()
    unidades = set()

    for r in receitas:
        for ing in r.get("ingredientes", []):
            ingredientes.add(ing["nome"])
            unidades.add(ing["unidade"])

    return {
        "ingredientes": sorted(list(ingredientes)),
        "unidades": sorted(list(unidades))
    }