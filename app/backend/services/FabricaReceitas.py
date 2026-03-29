import json
import random
import unicodedata
import os
from copy import deepcopy

from app.backend.services.bases import (
    proteinasUN, proteinasKG, legumes, carboidratos,
    folhas_saladas, massas, proteinas_proibidas_sopa,
    molhos, caldos, frutas, proteinasCF, carboidratosCF, liquidos, cereais, farinhas
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
    "liquidos": []
}

MAX_REPETICAO = 2

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

    for item in estoque:
        nome_original = item["nome"]
        nome = normalizar(nome_original)

        categoria = None
        subcategoria = "ambos"  # 🔥 NOVO (default)

        # =========================
        # PRIORIDADE DE CLASSIFICAÇÃO
        # =========================

        # 🔥 PROTEÍNA (CAFÉ OU GERAL)
        if any(normalizar(pcf) in nome for pcf in proteinasCF):
            categoria = "proteina"
            subcategoria = "cafe"

        elif any(normalizar(ccf) in nome for ccf in carboidratosCF):
            categoria = "carbo"
            subcategoria = "cafe"

        # 🥤 LÍQUIDOS (ANTES DE PROTEÍNA)
        elif any(normalizar(lq) in nome for lq in liquidos):
            categoria = "liquido"
            subcategoria = "cafe"

        # 🥩 PROTEÍNA
        elif any(normalizar(p) in nome for p in proteinasKG + proteinasUN):
            categoria = "proteina"

        # 🍝 MASSA (antes de fruta e carbo)
        elif any(normalizar(m) in nome for m in massas):
            categoria = "massa"

        # 🥕 LEGUMES
        elif any(normalizar(l) in nome for l in legumes):
            categoria = "legume"


        # 🍚 CARBO
        elif any(normalizar(c) in nome for c in carboidratos):
            categoria = "carbo"

        # 🥬 FOLHAS
        elif any(normalizar(f) in nome for f in folhas_saladas):
            categoria = "folha"

        # 🥫 MOLHOS
        elif any(normalizar(mol) in nome for mol in molhos):
            categoria = "molho"

        # 🥫 Farinhas
        elif any(normalizar(far) in nome for far in farinhas):
            categoria = "farinha"

        # 🥫 Cereais
        elif any(normalizar(cer) in nome for cer in cereais):
            categoria = "cereal"

        # 🍲 CALDOS
        elif any(normalizar(caldo["nome"]) in nome for caldo in caldos):
            categoria = "caldo"

        # 🍎 FRUTA (AGORA POR ÚLTIMO E MAIS SEGURO)
        elif any(normalizar(fcf) in nome.split() for fcf in frutas):
            categoria = "fruta"
            subcategoria = "cafe"

        # =========================
        # FALLBACK INTELIGENTE
        # =========================
        else:
            if "arroz" in nome or "feijao" in nome or "batata" in nome:
                categoria = "carbo"

            elif "frango" in nome or "carne" in nome or "ovo" in nome:
                categoria = "proteina"

            elif "alface" in nome or "rucula" in nome:
                categoria = "folha"

            elif "molho" in nome:
                categoria = "molho"

            elif "caldo" in nome:
                categoria = "caldo"

        # =========================
        # SALVA
        # =========================
        if categoria:
            unidade = str(item.get("unidade", "")).lower()
            quantidade = float(item.get("quantidade", 0))

            if unidade in ["kg", "quilo", "quilos"]:
                quantidade *= 1000
                unidade = "g"

            elif unidade in ["g", "grama", "gramas"]:
                unidade = "g"

            elif unidade in ["l", "litro", "litros"]:
                quantidade *= 1000
                unidade = "ml"

            elif unidade in ["ml"]:
                unidade = "ml"

            elif unidade in ["un", "unidade", "unidades"]:
                unidade = "unidade"

            elif unidade in ["fatia", "fatias"]:
                unidade = "fatia"

            estoque_classificado.append({
                "nome": nome_original,
                "quantidade": quantidade,
                "unidade": unidade,
                "categoria": categoria,
                "subcategoria": subcategoria  # 🔥 NOVO
            })

    return estoque_classificado


# =========================
# CONSUMO
# =========================
def consumir(estoque, categoria, qtd, subcategoria=None):
    candidatos = [
        i for i in estoque
        if i["categoria"] == categoria
        and i["quantidade"] > 0
        and (subcategoria is None or i.get("subcategoria") == subcategoria)
    ]

    # 🔒 NÃO faz fallback (corrige o bug)
    if not candidatos:
        return None

    # 🔥 evita repetição recente
    chave = categoria if subcategoria is None else f"{categoria}_{subcategoria}"

    if chave not in ULTIMOS_USADOS:
        ULTIMOS_USADOS[chave] = []

    filtrados = [
        i for i in candidatos
        if i["nome"] not in ULTIMOS_USADOS[chave]
    ]

    if filtrados:
        item = random.choice(filtrados)
    else:
        item = random.choice(candidatos)

    usar = min(item["quantidade"], qtd)
    item["quantidade"] -= usar

    # 🔥 histórico
    ULTIMOS_USADOS[chave].append(item["nome"])

    if len(ULTIMOS_USADOS[chave]) > MAX_REPETICAO:
        ULTIMOS_USADOS[chave].pop(0)

    return {
        "nome": item["nome"],
        "quantidade": usar,
        "unidade": item["unidade"],
        "categoria": item["categoria"],
        "subcategoria": item.get("subcategoria")
    }


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


def ajustar_porcionamento(item):
    unidade = item["unidade"]
    categoria = item["categoria"]
    subcategoria = item.get("subcategoria")

    # =========================
    # CAFÉ DA MANHÃ
    # =========================
    if subcategoria == "cafe":

        # 🥩 proteína café
        if categoria == "proteina":
            if unidade == "unidade":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 80

        # 🍞 carbo café
        elif categoria == "carbo":
            if unidade == "fatia":
                item["quantidade"] = 2
            elif unidade == "g":
                item["quantidade"] = 50
            elif unidade == "unidade":
                item["quantidade"] = 1

        # 🍎 fruta
        elif categoria == "fruta":
            if unidade == "unidade":
                item["quantidade"] = 1
            elif unidade == "g":
                item["quantidade"] = 100

        # 🥤 líquido (se você já criou a lista)
        elif categoria == "liquido":
            if unidade == "ml":
                item["quantidade"] = 200

    return item


# =========================
# CAFÉ
# =========================

def nome_prato_cafe(tipo, ingredientes):
    if tipo == "panqueca":
        return f"Panqueca de {ingredientes['farinha']['nome']}" + (f" com {ingredientes['recheio']['nome']}" if 'recheio' in ingredientes else "")
    elif tipo == "crepioca":
        return f"Crepioca de {ingredientes['ovo']['nome']}" + (f" com {ingredientes['recheio']['nome']}" if 'recheio' in ingredientes else "")
    elif tipo == "mingau":
        return f"Mingau de {ingredientes['farinha']['nome']}" + (f" com {ingredientes['fruta']['nome']}" if 'fruta' in ingredientes else "")
    elif tipo == "omelete":
        return f"Omelete matinal" + (f" com {ingredientes['recheio']['nome']}" if 'recheio' in ingredientes else "")
    else:
        return "Café simples"

def gerar_preparo_cafe(tipo, ingredientes):
    passos = []
    if tipo == "panqueca":
        passos.append(f"Misture {ingredientes['farinha']['nome']} com {ingredientes['liquido']['nome']} e {ingredientes['ovo']['nome']}.")
        if 'fermento' in ingredientes:
            passos.append(f"Adicione {ingredientes['fermento']['nome']} para dar leveza.")
        passos.append("Aqueça uma frigideira antiaderente e cozinhe até dourar ambos os lados.")
        if 'recheio' in ingredientes:
            passos.append(f"Recheie com {ingredientes['recheio']['nome']} e dobre a panqueca.")
        passos.append("Sirva imediatamente, acompanhado de fruta ou leite.")
    elif tipo == "crepioca":
        passos.append(f"Misture {ingredientes['tapioca']['nome']} com {ingredientes['ovo']['nome']}.")
        if 'liquido' in ingredientes:
            passos.append(f"Adicione {ingredientes['liquido']['nome']} para uma consistência mais cremosa.")
        passos.append("Cozinhe em frigideira antiaderente até firmar.")
        if 'recheio' in ingredientes:
            passos.append(f"Recheie com {ingredientes['recheio']['nome']}, dobre e sirva.")
    elif tipo == "mingau":
        passos.append(f"Aqueça {ingredientes['liquido']['nome']} e adicione {ingredientes['farinha']['nome']} mexendo sempre.")
        if 'fruta' in ingredientes:
            passos.append(f"Finalize com {ingredientes['fruta']['nome']} picada por cima.")
        passos.append("Sirva quente.")
    elif tipo == "omelete":
        passos.append(f"Bata {ingredientes['ovo']['nome']}" + (f" com {ingredientes['liquido']['nome']}" if 'liquido' in ingredientes else ""))
        if 'recheio' in ingredientes:
            passos.append(f"Adicione {ingredientes['recheio']['nome']} à mistura.")
        passos.append("Cozinhe em frigideira até dourar.")
        passos.append("Sirva quente.")
    else:
        # simples
        for k, v in ingredientes.items():
            passos.append(f"Sirva {v['nome']}.")
    return passos

def gerar_cafe(estoque):
    """
    Gera até 31 cafés da manhã variados.
    Usa defs nome_prato_cafe e gerar_preparo_cafe para modo de preparo realista.
    """
    estoque = classificar_estoque(estoque)
    receitas = []
    tentativas = 0

    while len(receitas) < 31 and tentativas < 300:
        tentativas += 1
        receita = None

        tem_farinha = any(i["categoria"] in ["farinha", "cereal"] and i["quantidade"] > 0 for i in estoque)
        tem_liquido = any(i["categoria"] == "liquido" and i["quantidade"] > 0 for i in estoque)
        tem_ovo = any(i["categoria"] == "proteina" and i["subcategoria"] == "cafe" and i["quantidade"] > 0 for i in estoque)
        tem_fruta = any(i["categoria"] == "fruta" and i["quantidade"] > 0 for i in estoque)

        if tem_farinha and tem_liquido and tem_ovo:
            tipo_prato = random.choice(["panqueca", "crepioca", "mingau", "omelete"])
        else:
            tipo_prato = "simples"

        ingredientes = {}

        if tipo_prato == "panqueca":
            ingredientes['farinha'] = consumir(estoque, "farinha", 30, subcategoria="cafe") or consumir(estoque, "cereal", 30, subcategoria="cafe")
            ingredientes['liquido'] = consumir(estoque, "liquido", 100, subcategoria="cafe")
            ingredientes['ovo'] = consumir(estoque, "proteina", 1, subcategoria="cafe")
            ingredientes['fermento'] = consumir(estoque, "fermento", 5, subcategoria="cafe")  # opcional
            ingredientes['recheio'] = consumir(estoque, "fruta", 1, subcategoria="cafe")  # opcional

        elif tipo_prato == "crepioca":
            ingredientes['tapioca'] = consumir(estoque, "farinha", 30, subcategoria="cafe")
            ingredientes['ovo'] = consumir(estoque, "proteina", 1, subcategoria="cafe")
            ingredientes['liquido'] = consumir(estoque, "liquido", 50, subcategoria="cafe")  # opcional
            ingredientes['recheio'] = consumir(estoque, "fruta", 1, subcategoria="cafe") or consumir(estoque, "proteina", 1, subcategoria="cafe")  # opcional

        elif tipo_prato == "mingau":
            ingredientes['farinha'] = consumir(estoque, "farinha", 30, subcategoria="cafe") or consumir(estoque, "cereal", 30, subcategoria="cafe")
            ingredientes['liquido'] = consumir(estoque, "liquido", 150, subcategoria="cafe")
            ingredientes['fruta'] = consumir(estoque, "fruta", 1, subcategoria="cafe")  # opcional

        elif tipo_prato == "omelete":
            ingredientes['ovo'] = consumir(estoque, "proteina", 2, subcategoria="cafe")
            ingredientes['liquido'] = consumir(estoque, "liquido", 30, subcategoria="cafe")  # opcional
            ingredientes['recheio'] = consumir(estoque, "fruta", 1, subcategoria="cafe") or consumir(estoque, "legume", 50)  # opcional

        else:
            # simples fallback
            carbo = consumir(estoque, "carbo", 20, subcategoria="cafe") or consumir(estoque, "farinha", 30, subcategoria="cafe")
            proteina = consumir(estoque, "proteina", 1, subcategoria="cafe")
            liquido = consumir(estoque, "liquido", 150, subcategoria="cafe")
            fruta = consumir(estoque, "fruta", 1, subcategoria="cafe")
            for k,v in zip(["carbo","proteina","liquido","fruta"], [carbo,proteina,liquido,fruta]):
                if v: ingredientes[k] = v
            tipo_prato = "simples"

        if not ingredientes:
            continue

        nome = nome_prato_cafe(tipo_prato, ingredientes)
        modo_preparo = gerar_preparo_cafe(tipo_prato, ingredientes)
        tempo = random.randint(8, 20) if tipo_prato != "simples" else 5

        receita = {
            "nome": nome,
            "categoria": "cafe",
            "ingredientes": list(ingredientes.values()),
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
            proteina = consumir(estoque, "proteina", 120)
            carbo = consumir(estoque, "carbo", 100)

            if proteina and proteina.get("subcategoria") == "liquido":
                continue

            if not receita_valida(proteina, carbo):
                continue

            ingredientes = [proteina, carbo]

            legume = consumir(estoque, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque, "folha", 50)
            if folha:
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
            proteina = consumir(estoque_temp, "proteina", 100)

            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes = [massa, molho, proteina]

            legume = consumir(estoque_temp, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque_temp, "folha", 50)
            if folha:
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
        # 🍽️ PF (REUTILIZA ALMOÇO)
        # =========================
        if tipo == "pf":
            proteina = consumir(estoque, "proteina", 120)
            carbo = consumir(estoque, "carbo", 100)

            if not receita_valida(proteina, carbo):
                continue

            ingredientes = [proteina, carbo]

            legume = consumir(estoque, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque, "folha", 50)
            if folha:
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
        # 🍝 MASSA (REUTILIZA ALMOÇO)
        # =========================
        elif tipo == "massa":
            estoque_temp = deepcopy(estoque)

            massa = consumir(estoque_temp, "massa", 100)
            molho = consumir(estoque_temp, "molho", 50)
            proteina = consumir(estoque_temp, "proteina", 100)

            if not receita_valida(massa, molho, proteina):
                continue

            ingredientes = [massa, molho, proteina]

            legume = consumir(estoque_temp, "legume", 80)
            if legume:
                ingredientes.append(legume)

            folha = consumir(estoque_temp, "folha", 50)
            if folha:
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
        # 🍲 SOPA (UPGRADE REAL)
        # =========================
        else:
            proteina = consumir(estoque, "proteina", 80)
            caldo = consumir(estoque, "caldo", 500)
            legume1 = consumir(estoque, "legume", 80)
            legume2 = consumir(estoque, "legume", 80)

            if not receita_valida(proteina, caldo, legume1):
                continue

            if proteina["nome"] in proteinas_proibidas_sopa:
                continue

            ingredientes = [caldo, proteina, legume1]
            if legume2:
                ingredientes.append(legume2)

            # 🧠 nome mais realista
            nome = random.choice([
                f"Sopa caseira de {proteina['nome']} com legumes",
                f"Caldo nutritivo de {proteina['nome']} com vegetais",
                f"Sopa leve de {proteina['nome']} com legumes frescos"
            ])

            # 🔥 preparo realista
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