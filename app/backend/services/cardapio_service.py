import os
import json
from app.backend.services.bases import ( proteinasKG, proteinasUN, folhas_saladas, carboidratos, massas, molhos, legumes, unidades)

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
    """
    Espera lista de receitas já prontas (93 idealmente)
    Estrutura:
    dia -> cafe / almoco / jantar
    """

    cardapio = {}
    total_dias = 31

    i = 0

    for dia in range(1, total_dias + 1):
        cardapio[dia] = {
            "cafe": receitas[i] if i < len(receitas) else {},
            "almoco": receitas[i + 1] if i + 1 < len(receitas) else {},
            "jantar": receitas[i + 2] if i + 2 < len(receitas) else {},
        }
        i += 3

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
        
        legumes
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
    cardapio = montar_cardapio(receitas)
    sobras = carregar_sobras()

    return {
        "cardapio": cardapio,
        "sobras": sobras,
        "total_receitas": len(receitas)
    }