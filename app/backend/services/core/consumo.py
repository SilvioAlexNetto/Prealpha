from app.backend.services.core.normalizacao import normalizar
import random

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


def simular_consumo(
    estoque,
    categoria,
    qtd,
    subcategoria=None,
    bloquear=False,
    dias_restantes=None,
    consumo_max_por_dia=None
):
    
    def calcular_peso(item):
        peso = 1.0

        # 📦 mais quantidade → mais chance
        peso += item["quantidade"] / 1000  

        # 🔁 penaliza repetição recente
        chave = f"{categoria}_{subcategoria}" if subcategoria else categoria

        if chave in ULTIMOS_USADOS:
            repeticoes = ULTIMOS_USADOS[chave].count(item["nome"])
            peso -= repeticoes * 0.5

        # 🛑 evita peso negativo
        return max(peso, 0.1)

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

    # 🔥 CORREÇÃO: lógica de proteção real
    if dias_restantes and consumo_max_por_dia:

        candidatos_filtrados = []

        for item in candidatos:
            # quanto PRECISA sobrar pra completar os dias
            necessario_total = dias_restantes * consumo_max_por_dia

            # só usa se tiver margem segura
            if item["quantidade"] >= consumo_max_por_dia:
                candidatos_filtrados.append(item)

        if candidatos_filtrados:
            candidatos = candidatos_filtrados

    chave = f"{categoria}_{subcategoria}" if subcategoria else categoria

    if chave not in ULTIMOS_USADOS:
        ULTIMOS_USADOS[chave] = []

    filtrados = [
        i for i in candidatos
        if i["nome"] not in ULTIMOS_USADOS[chave]
    ]

    pool = filtrados or candidatos

# 🔥 NOVO: prioriza estoque
    pool_priorizado = priorizar_candidatos(pool, dias_restantes)

    pesos = [calcular_peso(i) for i in pool_priorizado]

    item = random.choices(
        pool_priorizado,
        weights=pesos,
        k=1
    )[0]

    # 🔥 CORREÇÃO CRÍTICA: NÃO permite consumo parcial
    if item["quantidade"] < qtd:
        return None

    usar = qtd

    convertido = item_precisa_preparo(item)

    if convertido:
        item_convertido = preparar_item_bruto(item)
        quantidade_final = usar * 0.65
    else:
        item_convertido = item
        quantidade_final = usar

    return {
        "ref": item,
        "nome": item_convertido["nome"],
        "quantidade": quantidade_final,
        "quantidade_original": usar,
        "unidade": item_convertido.get("unidade", item["unidade"]),
        "categorias": item_convertido.get("categorias", item.get("categorias", [])),
        "subcategorias": item_convertido.get("subcategorias", item.get("subcategorias", []))
    }


def aplicar_consumo(item_simulado):
    if not item_simulado or "ref" not in item_simulado:
        return

    item_real = item_simulado["ref"]

    if item_real["quantidade"] < item_simulado["quantidade_original"]:
        return

    item_real["quantidade"] -= item_simulado["quantidade_original"]

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

def analisar_estoque(estoque):
    return {
        "tem_fruta": any("fruta" in i["categorias"] and i["quantidade"] > 0 for i in estoque),
        "tem_leite": any("liquido" in i["categorias"] and "leite" in i["nome"].lower() for i in estoque),
        "tem_cafe": any("cafe" in i["nome"].lower() for i in estoque),
        "tem_carbo_cafe": any("carboCF" in i["categorias"] for i in estoque),
        "tem_proteina_cafe": any("proteinaCF" in i["categorias"] for i in estoque),
        "tem_cereal": any("cereal" in i["categorias"] for i in estoque),
        "tem_farinha": any("farinha" in i["categorias"] for i in estoque),
    }

def gerar_opcoes_cafe(status):
    opcoes = []

    if status["tem_fruta"]:
        opcoes.append("fruta")

    if status["tem_leite"] and status["tem_fruta"]:
        opcoes.append("vitamina")

    if status["tem_cereal"] and status["tem_leite"]:
        opcoes.append("mingau")

    if status["tem_farinha"] and status["tem_leite"]:
        opcoes.append("panqueca")

    if status["tem_carbo_cafe"]:
        opcoes.append("simples")

    return opcoes

def escolher_opcao(opcoes):
    pesos = {
        "vitamina": 4,
        "mingau": 2,
        "panqueca": 2,
        "simples": 3,
        "fruta": 1
    }

    opcoes_validas = [o for o in opcoes if o in pesos]

    return random.choices(
        opcoes_validas,
        weights=[pesos[o] for o in opcoes_validas],
        k=1
    )[0]

def calcular_limites(estoque, total_dias):

    limites = {}

    for item in estoque:
        nome = item["nome"]
        qtd = item["quantidade"]

        limite_dia = qtd / total_dias

        limites[nome] = {
            "total": qtd,
            "por_dia": limite_dia
        }

    return limites

def pode_usar(item, limites, dia_atual):
    nome = item["nome"]

    if nome not in limites:
        return True

    usado_ate_agora = limites[nome].get("usado", 0)
    limite_total_ate_dia = limites[nome]["por_dia"] * dia_atual

    return usado_ate_agora <= limite_total_ate_dia

def registrar_uso(item, limites):
    nome = item["nome"]

    if nome not in limites:
        return

    limites[nome]["usado"] = limites[nome].get("usado", 0) + item["quantidade_original"]


def priorizar_candidatos(candidatos, dias_restantes):

    if not candidatos or not dias_restantes:
        return candidatos

    def score(item):
        # quanto “sobra” por dia
        return item["quantidade"] / dias_restantes

    # 🔥 ordena do maior risco de sobra → menor
    candidatos_ordenados = sorted(
        candidatos,
        key=score,
        reverse=True
    )

    # 🔥 pega os TOP mais críticos
    top_n = max(3, len(candidatos) // 2)
    top = candidatos_ordenados[:top_n]

    return top

def montar_base_cafe(estoque, tipo, dias_restantes):
    itens = []

    # =========================
    # ☕ BEBIDA (SEMPRE TENTA)
    # =========================
    bebida_base = None

    tem_cafe = any("cafe" in i["nome"].lower() for i in estoque)
    tem_leite = any("leite" in i["nome"].lower() for i in estoque)

    # 🔥 tenta café primeiro (melhor uso de estoque parado)
    if tem_cafe:
        bebida, cafe, leite = simular_cafe_completo(estoque)

        if bebida:
            itens.append(("bebida", bebida, cafe, leite))
            bebida_base = bebida

    # fallback → leite puro
    if not bebida_base and tem_leite:
        leite, tipo_leite = simular_leite(estoque, 200)

        if leite:
            itens.append(("bebida", {
                "nome": tipo_leite,
                "quantidade": 200,
                "unidade": "ml",
                "categorias": ["bebida"],
                "subcategorias": ["cafe"]
            }, leite, None))

    # =========================
    # 🍞 BASE SÓLIDA
    # =========================
    if tipo == "simples":

        carbo = simular_consumo(estoque, "carboCF", 2, subcategoria="cafe")
        if carbo:
            itens.append(("principal", carbo))

    elif tipo == "mingau":

        cereal = simular_consumo(estoque, "cereal", 40)
        leite = simular_leite(estoque, 200)[0]

        if cereal and leite:
            itens.append(("principal", cereal))
            itens.append(("extra", leite))

    elif tipo == "panqueca":

        farinha = simular_consumo(estoque, "farinha", 50)
        liquido = simular_consumo(estoque, "liquido", 100)

        if farinha and liquido:
            itens.append(("principal", farinha))
            itens.append(("extra", liquido))

    elif tipo == "vitamina":

        fruta = simular_consumo(estoque, "fruta", 1)
        leite = simular_leite(estoque, 200)[0]

        if fruta and leite:
            itens.append(("principal", fruta))
            itens.append(("extra", leite))

    elif tipo == "fruta":

        fruta = simular_consumo(estoque, "fruta", 1)
        if fruta:
            itens.append(("principal", fruta))

    # =========================
    # 🍎 COMPLEMENTOS INTELIGENTES
    # =========================
    # 🔥 aqui entra o ganho real

    # adiciona fruta se tiver pouco uso
    frutas_restantes = sum(i["quantidade"] for i in estoque if "fruta" in i["categorias"])

    if frutas_restantes > dias_restantes:
        fruta_extra = simular_consumo(estoque, "fruta", 1)
        if fruta_extra:
            itens.append(("extra", fruta_extra))

    # adiciona proteína leve
    proteina = simular_consumo(estoque, "proteinaCF", 1, subcategoria="cafe")
    if proteina and random.random() < 0.5:
        itens.append(("extra", proteina))

    return itens

def aplicar_itens_cafe(itens_base):
    ingredientes = []
    bebidas = []

    for tipo_item in itens_base:

        # estrutura pode variar (bebida tem mais dados)
        if tipo_item[0] == "bebida":
            _, bebida, cafe_ref, leite_ref = tipo_item

            # aplica consumo real
            if cafe_ref:
                aplicar_consumo(cafe_ref)

            if leite_ref:
                aplicar_consumo(leite_ref)

            bebidas.append(bebida)
            continue

        # =========================
        # 🍽️ ITENS NORMAIS
        # =========================
        _, item = tipo_item

        if not item:
            continue

        aplicar_consumo(item)

        item_ajustado = ajustar_porcionamento(item)

        ingredientes.append(item_ajustado)

    return ingredientes, bebidas

