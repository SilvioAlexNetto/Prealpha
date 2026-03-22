import random

# =========================
# PROTEÍNA (REGRAS DE PREPARO)
# =========================

def preparar_proteina(proteina):
    nome = proteina["nome"].lower()

    # Frango
    if any(p in nome for p in ["frango", "peito de frango", "coxa"]):
        metodo = random.choice(["grelhe", "asse", "refogue"])
        texto = (
            f"{metodo.capitalize()} o {nome} até dourar bem por fora "
            f"e cozinhar completamente por dentro."
        )

    # Carne bovina
    elif any(p in nome for p in ["patinho", "alcatra", "carne", "bovina"]):
        metodo = random.choice(["grelhe", "sele", "refogue"])
        texto = (
            f"{metodo.capitalize()} a {nome} em fogo alto até dourar "
            f"e manter suculenta."
        )

    # Peixes
    elif any(p in nome for p in ["salmão", "tilápia", "peixe", "pescada", "linguado"]):
        metodo = random.choice(["grelhe", "asse"])
        texto = (
            f"{metodo.capitalize()} o {nome} por poucos minutos de cada lado "
            f"até ficar macio."
        )

    # Ovos
    elif "ovo" in nome:
        metodo = random.choice(["mexa", "refogue"])
        texto = (
            f"{metodo.capitalize()} o {nome} mexendo até ficar completamente cozido."
        )

    # Embutidos
    elif any(p in nome for p in ["linguiça", "salsicha"]):
        metodo = random.choice(["frite levemente", "asse"])
        texto = (
            f"{metodo.capitalize()} a {nome} até dourar por fora."
        )

    # Vegetal proteico
    elif any(p in nome for p in ["tofu", "tempeh"]):
        metodo = random.choice(["grelhe", "refogue"])
        texto = (
            f"{metodo.capitalize()} o {nome} até dourar levemente."
        )

    # fallback
    else:
        metodo = random.choice(["grelhe", "refogue", "cozinhe"])
        texto = (
            f"{metodo.capitalize()} o {nome} por cerca de 5 a 10 minutos até dourar."
        )

    return {
        "texto": texto,
        "metodo": metodo,
        "nome": nome
    }


# =========================
# CONVERSOR DE MÉTODO
# =========================

def metodo_para_nome(metodo):

    mapa = {
        "grelhe": "grelhado",
        "refogue": "refogado",
        "asse": "assado",
        "cozinhe": "cozido",
        "mexa": "mexido",
        "sele": "selado",
        "frite levemente": "levemente frito"
    }

    return mapa.get(metodo, "preparado")


# =========================
# CALDO (SOPA)
# =========================

def definir_caldo(caldo):

    if caldo["forma"] == "liquido":
        return {
            "nome": caldo["nome"],
            "quantidade": 500,
            "unidade": "ml"
        }

    elif caldo["forma"] == "tablete":
        return {
            "nome": caldo["nome"],
            "quantidade": 1,
            "unidade": "unidade"
        }

    elif caldo["forma"] == "po":
        return {
            "nome": caldo["nome"],
            "quantidade": 10,
            "unidade": "g"
        }

    # fallback seguro
    return {
        "nome": caldo["nome"],
        "quantidade": 1,
        "unidade": "unidade"
    }