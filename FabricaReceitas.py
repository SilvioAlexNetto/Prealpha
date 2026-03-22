import random
import json

# =========================
# BASES
# =========================

proteinasKG = [
    "Peito de frango", "Coxa de frango", "Sobrecoxa de frango", "Frango inteiro",
    "Filé de frango", "Asa de frango", "Frango desfiado",
    "Patinho", "Acém", "Alcatra", "Músculo bovino", "Coxão mole",
    "Coxão duro", "Lagarto", "Fraldinha", "Picanha", "Contrafilé",
    "Maminha", "Filé mignon", "Costela bovina", "Cupim", "Acém moído",
    "Carne moída", "Carne de segunda",
]

proteinasUN = [
    "Ovo", "Ovo caipira", "Ovo vermelho", "Ovo de codorna",
    "Gema de ovo", "Hambúrguer bovino", "Hambúrguer de frango",
    "Hambúrguer suíno", "Hambúrguer artesanal", "Salsicha",
    "Salsicha de frango", "Salsicha bovina", "Salsicha hot dog",
    "Nuggets de frango", "Empanado de frango", "Almôndega",
    "Tofu", "Tofu defumado", "Tempeh", "Queijo coalho",
    "Queijo muçarela", "Queijo prato", "Presunto",
    "Peito de peru", "Sardinha enlatada", "Atum enlatado",
    "Hambúrguer vegetal", "Proteína vegetal"
]

carboidratos = [
    "Quinoa", "Cuscuz", "Aveia", "Milho verde", "Milho",
    "Polenta", "Fubá", "Farofa",
    "Grão-de-bico", "Lentilha", "Feijão carioca",
    "Feijão preto", "Feijão branco", "Ervilha",
    "Batata baroa", "Mandioquinha", "Inhame",
    "Cará", "Tapioca", "Cuscuz nordestino",
    "Arroz branco",
    "Arroz integral",
    "Arroz parboilizado",
    "Arroz basmati",
    "Arroz jasmim",
    "Arroz arbóreo",
    "Arroz selvagem",
    "Arroz cateto",
    "Arroz vermelho",
    "Arroz negro",
]

massas = [
    "Macarrão Espaguete", "Macarrão Penne", "Macarrão Fusilli",
    "Macarrão Rigatoni", "Macarrão Linguine", "Macarrão Talharim",
    "Macarrão Tagliatelle", "Macarrão Farfalle", "Macarrão Parafuso",
    "Nhoque", "Ravioli", "Capeletti", "Tortellini", "Canelone",
]

molhos = [
    "Molho de tomate", "Molho branco", "Molho quatro queijos",
    "Molho pesto", "Molho cheddar", "Molho bolonhesa"
]

vegetais = [
    "Brócolis", "Cenoura", "Abobrinha", "Couve-flor",
    "Beterraba", "Vagem", "Espinafre", "Couve",
    "Repolho", "Tomate", "Pimentão", "Berinjela",
    "Abóbora", "Ervilha", "Chuchu"
]

caldos = [
    {"nome": "Caldo de legumes", "forma": "liquido"},
    {"nome": "Caldo de frango", "forma": "liquido"},
    {"nome": "Caldo de carne", "forma": "liquido"},
]

proteinas_proibidas_sopa = ["Ovo"]

# =========================
# ESTOQUE (2 ETAPAS)
# =========================

ESTOQUE_BRUTO = []
ESTOQUE_CLASSIFICADO = {
    "proteina": [],
    "carboidrato": [],
    "massa": [],
    "vegetal": []
}

def classificar_item(nome):
    n = nome.lower()

    if any(p.lower() in n for p in proteinasKG + proteinasUN):
        return "proteina"
    if any(c.lower() in n for c in carboidratos):
        return "carboidrato"
    if any(m.lower() in n for m in massas):
        return "massa"
    if any(v.lower() in n for v in vegetais):
        return "vegetal"
    return None

def registrar_estoque(nome, quantidade=1, unidade="unidade"):
    ESTOQUE_BRUTO.append({"nome": nome, "quantidade": quantidade, "unidade": unidade})

    categoria = classificar_item(nome)
    if categoria:
        ESTOQUE_CLASSIFICADO[categoria].append({
            "nome": nome,
            "quantidade": quantidade,
            "unidade": unidade
        })

# =========================
# UTILITÁRIO ESTOQUE
# =========================

def escolher_do_estoque_ou_base(categoria, base):
    if ESTOQUE_CLASSIFICADO[categoria]:
        return random.choice(ESTOQUE_CLASSIFICADO[categoria])
    return {"nome": random.choice(base), "quantidade": 1, "unidade": "unidade"}

# =========================
# CONTROLE DE CICLO (evita repetição)
# =========================

ciclo = ["pf", "massa", "sopa"]
indice_ciclo = 0

def escolher_tipo():
    global indice_ciclo
    tipo = ciclo[indice_ciclo]
    indice_ciclo = (indice_ciclo + 1) % len(ciclo)
    return tipo

# =========================
# PROTEÍNA
# =========================

def escolher_proteina():
    return escolher_do_estoque_ou_base("proteina", proteinasKG + proteinasUN)

# =========================
# CARBO
# =========================

def escolher_carbo():
    return escolher_do_estoque_ou_base("carboidrato", carboidratos)

# =========================
# PF
# =========================

def gerar_pf():
    proteina = escolher_proteina()
    carbo = escolher_carbo()

    return {
        "nome": f"{proteina['nome']} com {carbo['nome']}",
        "tipo": "pf",
        "ingredientes": [proteina, carbo],
        "modo_preparo": [
            f"Prepare {proteina['nome'].lower()}",
            f"Cozinhe {carbo['nome'].lower()}"
        ],
        "tempo_preparo": f"{random.randint(20, 40)} min"
    }

# =========================
# MASSA
# =========================

def gerar_massa():
    massa = escolher_do_estoque_ou_base("massa", massas)
    proteina = escolher_proteina()

    return {
        "nome": f"{massa['nome']} com {proteina['nome']}",
        "tipo": "massa",
        "ingredientes": [massa, proteina],
        "modo_preparo": [
            f"Cozinhe {massa['nome'].lower()}",
            f"Prepare {proteina['nome'].lower()}"
        ],
        "tempo_preparo": f"{random.randint(20, 40)} min"
    }

# =========================
# SOPA
# =========================

def escolher_proteina_sopa():
    while True:
        p = escolher_proteina()
        if p["nome"] not in proteinas_proibidas_sopa:
            return p

def gerar_sopa():
    proteina = escolher_proteina_sopa()

    return {
        "nome": f"Sopa de {proteina['nome']}",
        "tipo": "sopa",
        "ingredientes": [proteina],
        "modo_preparo": [
            f"Cozinhe {proteina['nome'].lower()}"
        ],
        "tempo_preparo": f"{random.randint(30, 60)} min"
    }

# =========================
# GERADOR
# =========================

def gerar_receita():
    tipo = escolher_tipo()

    if tipo == "pf":
        return gerar_pf()
    elif tipo == "massa":
        return gerar_massa()
    else:
        return gerar_sopa()

# =========================
# LOTE
# =========================

def gerar_lote(qtd=1000):
    return [gerar_receita() for _ in range(qtd)]

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    # EXEMPLO DE ESTOQUE (CLASSIFICA AUTOMATICAMENTE)
    registrar_estoque("arroz integral", 8, "kg")
    registrar_estoque("ovo", 6400, "unidade")
    registrar_estoque("patinho", 55500, "g")
    registrar_estoque("abobrinha", 150400, "g")

    receitas = gerar_lote(500)

    with open("receitas.json", "w", encoding="utf-8") as f:
        json.dump(receitas, f, ensure_ascii=False, indent=4)

    print("receitas.json!")