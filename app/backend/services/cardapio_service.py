import os, json, calendar
from datetime import datetime

from app.backend.services.bases import (
    proteinasKG, proteinasUN, folhas_saladas, carboidratos,
    massas, molhos, legumes, unidades, frutas,
    proteinasCF, carboidratosCF, liquidos,
    cereais, farinhas, fermentos, produtoBruto
)

from app.backend.services.config.paths import RECEITAS_PATH, SOBRAS_PATH


# =========================
# 💾 SALVAR RESULTADO
# =========================
def salvar_resultado(resultado):

    try:
        os.makedirs(os.path.dirname(RECEITAS_PATH), exist_ok=True)

        with open(RECEITAS_PATH, "w", encoding="utf-8") as f:
            json.dump(resultado.get("receitas", []), f, ensure_ascii=False, indent=4)

        with open(SOBRAS_PATH, "w", encoding="utf-8") as f:
            json.dump(resultado.get("sobras", []), f, ensure_ascii=False, indent=4)

        with open("consumidos.json", "w", encoding="utf-8") as f:
            json.dump(resultado.get("consumidos", []), f, ensure_ascii=False, indent=4)

        print("💾 Receitas, sobras e consumidos salvos com sucesso", flush=True)

        print("\n💾 DEBUG SALVAMENTO:")
        print("Receitas:", len(resultado.get("receitas", [])))
        print("Sobras:", len(resultado.get("sobras", [])))
        print("Consumidos:", len(resultado.get("consumidos", [])))

    except Exception as e:
        print("💥 Erro ao salvar resultado:", e, flush=True)


def carregar_consumidos():
    try:
        if not os.path.exists("consumidos.json"):
            return []

        with open("consumidos.json", "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("💥 Erro ao carregar consumidos:", e, flush=True)
        return []


# =========================
# 📥 CARREGAR RECEITAS
# =========================
def carregar_receitas():
    try:
        if not os.path.exists(RECEITAS_PATH):
            return []

        with open(RECEITAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("💥 Erro ao carregar receitas:", e, flush=True)
        return []


# =========================
# 📥 CARREGAR SOBRAS
# =========================
def carregar_sobras():
    try:
        if not os.path.exists(SOBRAS_PATH):
            return []

        with open(SOBRAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("💥 Erro ao carregar sobras:", e, flush=True)
        return []


# =========================
# 📅 ORGANIZAR CARDÁPIO
# =========================
def montar_cardapio(receitas, ano=None, mes=None):

    if not ano or not mes:
        hoje = datetime.now()
        ano = hoje.year
        mes = hoje.month

    total_dias = calendar.monthrange(ano, mes)[1]

    cardapio = {}

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
# 🧾 LISTAR INGREDIENTES
# =========================
def listar_ingredientes_e_unidades():

    todas_listas = (
        proteinasKG + proteinasUN + folhas_saladas + carboidratos +
        massas + molhos + frutas + proteinasCF + carboidratosCF +
        legumes + liquidos + cereais + farinhas +
        fermentos + produtoBruto
    )

    ingredientes = set()

    for item in todas_listas:
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
# 🎯 OBTER CARDÁPIO
# =========================
def obter_cardapio(ano=None, mes=None):

    receitas = carregar_receitas()

    if not receitas:
        return {
            "cardapio": {},
            "sobras": [],
            "total_receitas": 0
        }

    cardapio = montar_cardapio(receitas, ano, mes)
    sobras = carregar_sobras()

    return {
        "cardapio": cardapio,
        "sobras": sobras or [],
        "total_receitas": len(receitas)
    }