import os
import json
from app.backend.services.bases import ( proteinasKG, proteinasUN, folhas_saladas, carboidratos, massas, molhos, legumes, unidades, frutas, proteinasCF, carboidratosCF, liquidos)

# =========================
# PATHS
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

RECEITAS_PATH = os.path.join(BASE_DIR, "database", "BancoReceitas.json")
SOBRAS_PATH = os.path.join(BASE_DIR, "database", "Sobras.json")


# =========================
# CARREGAR RECEITAS
# =========================
def carregar_receitas():
    if not os.path.exists(RECEITAS_PATH):
        return []

    with open(RECEITAS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# CARREGAR SOBRAS
# =========================
def carregar_sobras():
    if not os.path.exists(SOBRAS_PATH):
        return []

    with open(SOBRAS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# ORGANIZAR CARDÁPIO
# =========================
def montar_cardapio(receitas):
    cardapio = {}
    total_dias = 31

    # 🔥 separa por categoria (ESSA É A CORREÇÃO PRINCIPAL)
    cafes = [r for r in receitas if r.get("categoria") == "cafe"]
    almocos = [r for r in receitas if r.get("categoria") == "almoco"]
    jantas = [r for r in receitas if r.get("categoria") == "jantar"]

    for dia in range(1, total_dias + 1):
        cardapio[dia] = {
            "cafe": cafes[dia - 1] if dia - 1 < len(cafes) else None,
            "almoco": almocos[dia - 1] if dia - 1 < len(almocos) else None,
            "jantar": jantas[dia - 1] if dia - 1 < len(jantas) else None,
        }

    return cardapio

# =========================
# LISTAR INGREDIENTES
# =========================
def listar_ingredientes_e_unidades():

    todas_listas = (
        proteinasKG +
        proteinasUN +
        folhas_saladas +
        carboidratos +
        massas +
        molhos +
        frutas +
        proteinasCF +
        carboidratosCF+
        legumes +
        liquidos
    )

    ingredientes = set()

    for item in todas_listas:
        # 🔥 PROTEÇÃO TOTAL
        if isinstance(item, dict):
            nome = item.get("nome")
        else:
            nome = str(item)

        if nome:
            ingredientes.add(nome.strip().lower())

    return {
        "ingredientes": sorted(ingredientes),
        "unidades": unidades
    }


# =========================
# FUNÇÃO PRINCIPAL (USO NO BACKEND)
# =========================
def obter_cardapio():
    receitas = carregar_receitas()

    # 🔒 proteção
    if not receitas:
        return {
            "cardapio": {},
            "sobras": [],
            "total_receitas": 0
        }

    cardapio = montar_cardapio(receitas)
    sobras = carregar_sobras()

    return {
        "cardapio": cardapio,
        "sobras": sobras or [],
        "total_receitas": len(receitas)
    }